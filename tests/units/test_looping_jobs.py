from collections.abc import Callable
from typing import Any

import pytest

from canarytokens import looping_jobs


class FakeLog:
    def __init__(self):
        self.info_calls: list[tuple[str, dict[str, Any]]] = []
        self.warn_calls: list[tuple[str, dict[str, Any]]] = []
        self.failure_calls: list[tuple[str, dict[str, Any]]] = []

    def info(self, message: str, **kwargs):
        self.info_calls.append((message, kwargs))

    def warn(self, message: str, **kwargs):
        self.warn_calls.append((message, kwargs))

    def failure(self, message: str, **kwargs):
        self.failure_calls.append((message, kwargs))


class FakeDoneDeferred:
    def __init__(self):
        self.errbacks: list[Callable[[Any], Any]] = []

    def addErrback(self, callback: Callable[[Any], Any]):
        self.errbacks.append(callback)
        return self


class FakeWorkerDeferred:
    def __init__(self):
        self.errbacks: list[Callable[[Any], Any]] = []
        self.boths: list[Callable[[Any], Any]] = []

    def addErrback(self, callback: Callable[[Any], Any]):
        self.errbacks.append(callback)
        return self

    def addBoth(self, callback: Callable[[Any], Any]):
        self.boths.append(callback)
        return self

    def fire_success(self, result: Any = None):
        value = result
        for callback in self.boths:
            value = callback(value)
        return value

    def fire_failure(self, failure: Any):
        value = failure
        for callback in self.errbacks:
            value = callback(value)
        for callback in self.boths:
            value = callback(value)
        return value


class FakeDelayedCall:
    def __init__(self, callback: Callable[[], None]):
        self._active = True
        self._callback = callback

    def active(self):
        return self._active

    def cancel(self):
        self._active = False

    def fire(self):
        if self._active:
            self._active = False
            self._callback()


class FakeReactor:
    def __init__(self, delayed_calls: list[FakeDelayedCall]):
        self._delayed_calls = delayed_calls

    def callLater(self, _seconds, callback, *args, **kwargs):
        delayed = FakeDelayedCall(lambda: callback(*args, **kwargs))
        self._delayed_calls.append(delayed)
        return delayed


class FakeLoopingCall:
    def __init__(self, func: Callable[[], Any]):
        self.func = func
        self.started_with: tuple[float, bool] | None = None
        self.done = FakeDoneDeferred()

    def start(self, interval_seconds: float, now: bool = False):
        self.started_with = (interval_seconds, now)
        return self.done


@pytest.fixture
def fake_runtime(monkeypatch):
    fake_log = FakeLog()
    fake_loop_calls: list[FakeLoopingCall] = []
    worker_deferreds: list[FakeWorkerDeferred] = []
    delayed_calls: list[FakeDelayedCall] = []

    def _looping_call_factory(func):
        call = FakeLoopingCall(func)
        fake_loop_calls.append(call)
        return call

    def _defer_to_thread(_work):
        deferred = FakeWorkerDeferred()
        worker_deferreds.append(deferred)
        return deferred

    monkeypatch.setattr(looping_jobs, "log", fake_log)
    monkeypatch.setattr(looping_jobs.internet.task, "LoopingCall", _looping_call_factory)
    monkeypatch.setattr(looping_jobs.threads, "deferToThread", _defer_to_thread)
    monkeypatch.setattr(looping_jobs, "reactor", FakeReactor(delayed_calls))

    return {
        "log": fake_log,
        "loop_calls": fake_loop_calls,
        "worker_deferreds": worker_deferreds,
        "delayed_calls": delayed_calls,
    }


def test_start_threaded_looping_job_rejects_non_positive_values():
    with pytest.raises(ValueError, match="interval_seconds"):
        looping_jobs.start_threaded_looping_job(
            job_name="job",
            work=lambda: None,
            interval_seconds=0,
            timeout_seconds=1,
        )

    with pytest.raises(ValueError, match="timeout_seconds"):
        looping_jobs.start_threaded_looping_job(
            job_name="job",
            work=lambda: None,
            interval_seconds=1,
            timeout_seconds=0,
        )


def test_start_threaded_looping_job_starts_looping_call(fake_runtime):
    looping_task, looping_task_done = looping_jobs.start_threaded_looping_job(
        job_name="job",
        work=lambda: None,
        interval_seconds=30,
        timeout_seconds=5,
        now=True,
    )

    assert len(fake_runtime["loop_calls"]) == 1
    assert fake_runtime["loop_calls"][0].started_with == (30, True)
    assert looping_task is fake_runtime["loop_calls"][0]
    assert looping_task_done is fake_runtime["loop_calls"][0].done
    assert len(looping_task_done.errbacks) == 1


def test_non_overlapping_run_skips_if_previous_is_active(fake_runtime):
    looping_task, _ = looping_jobs.start_threaded_looping_job(
        job_name="job",
        work=lambda: None,
        interval_seconds=30,
        timeout_seconds=5,
    )

    first_gate = looping_task.func()
    second_gate = looping_task.func()

    assert first_gate is not None
    assert second_gate is None
    assert len(fake_runtime["worker_deferreds"]) == 1
    assert any(
        "previous run is still active" in message
        for message, _ in fake_runtime["log"].warn_calls
    )


def test_timeout_unblocks_scheduler_wait_but_keeps_non_overlap(fake_runtime):
    looping_task, _ = looping_jobs.start_threaded_looping_job(
        job_name="cleanup",
        work=lambda: None,
        interval_seconds=30,
        timeout_seconds=5,
    )

    first_gate = looping_task.func()
    assert first_gate.called is False

    fake_runtime["delayed_calls"][0].fire()
    assert first_gate.called is True

    still_blocked_gate = looping_task.func()
    assert still_blocked_gate is None

    fake_runtime["worker_deferreds"][0].fire_success(123)

    next_gate = looping_task.func()
    assert next_gate is not None
    assert len(fake_runtime["worker_deferreds"]) == 2
    assert any(
        "exceeded timeout" in message for message, _ in fake_runtime["log"].warn_calls
    )


def test_worker_failure_is_logged_and_gate_finishes(fake_runtime):
    looping_task, _ = looping_jobs.start_threaded_looping_job(
        job_name="cleanup",
        work=lambda: None,
        interval_seconds=30,
        timeout_seconds=5,
    )

    gate = looping_task.func()
    fake_runtime["worker_deferreds"][0].fire_failure("boom")

    assert gate.called is True
    assert any("run failed" in message for message, _ in fake_runtime["log"].failure_calls)
