from canarytokens.utils import (
    coerce_to_float,
    get_deployed_commit_sha,
)


def test_get_deployed_commit_sha(tmpdir):
    sha_dir = tmpdir / "base"
    sha_dir.mkdir()
    sha_file = sha_dir / "COMMIT_SHA"
    example_sha = "comecommitsha"
    sha_file.write_text(example_sha, "utf-8")
    sha_file.is_file = lambda: True
    reported_sha = get_deployed_commit_sha(commit_sha_file=sha_file)
    assert reported_sha == example_sha


def test_coerce_to_float():
    assert 10.3 == coerce_to_float("10.3")
    assert 10 == coerce_to_float("10")
    assert not coerce_to_float("notafloat")
