from canarytokens.utils import (
    coerce_to_float,
    get_deployed_commit_sha,
    get_src_ip_continent,
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


def test_get_src_ip_continent():
    assert "AF" == get_src_ip_continent("ZA")
    assert "AN" == get_src_ip_continent("AQ")
    assert "AS" == get_src_ip_continent("CN")
    assert "EU" == get_src_ip_continent("GB")
    assert "NA" == get_src_ip_continent("US")
    assert "OC" == get_src_ip_continent("AU")
    assert "SA" == get_src_ip_continent("AR")
    assert "NO_CONTINENT" == get_src_ip_continent("1234")
