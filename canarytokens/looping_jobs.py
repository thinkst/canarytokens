from __future__ import annotations

from collections.abc import Callable
from typing import Any

from twisted.application import internet
from twisted.internet import defer, reactor, threads
from twisted.logger import Logger


log = Logger(namespace="LoopingJob")


def start_threaded_looping_job(
    *,
    job_name: str,
    work: Callable[[], Any],
    interval_seconds: float,
    timeout_seconds: float,
    now: bool = False,
):
    """
    Schedule a recurring job that runs in a worker thread with non-overlap and timeout gating.

    The timeout bounds how long the scheduler waits for a run before allowing the next cycle.
    It does not terminate the worker thread.
    """
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be > 0")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be > 0")

    state = {"running": False}

    def _run_nonblocking():
        if state["running"]:
            log.warn(
                "Skipping {job_name} run because previous run is still active",
                job_name=job_name,
            )
            return None

        state["running"] = True
        log.info("{job_name} job started", job_name=job_name)
        run_gate = defer.Deferred()

        def _finish_gate():
            if not run_gate.called:
                run_gate.callback(None)

        def _on_timeout():
            log.warn(
                "{job_name} run exceeded timeout of {timeout_seconds}s; scheduling continues",
                job_name=job_name,
                timeout_seconds=timeout_seconds,
            )
            _finish_gate()

        timeout_call = reactor.callLater(timeout_seconds, _on_timeout)

        def _on_complete(result):
            state["running"] = False
            if timeout_call.active():
                timeout_call.cancel()
            log.info("{job_name} job ended", job_name=job_name)
            _finish_gate()
            return result

        def _on_error(failure):
            log.failure("{job_name} run failed", failure=failure, job_name=job_name)
            return failure

        worker_deferred = threads.deferToThread(work)
        worker_deferred.addErrback(_on_error)
        worker_deferred.addBoth(_on_complete)
        return run_gate

    looping_task = internet.task.LoopingCall(_run_nonblocking)
    looping_task_done = looping_task.start(interval_seconds, now=now)
    looping_task_done.addErrback(
        lambda failure: log.failure(
            "{job_name} LoopingCall stopped unexpectedly",
            failure=failure,
            job_name=job_name,
        )
    )
    return looping_task, looping_task_done
