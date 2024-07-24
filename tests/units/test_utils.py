import pytest

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


@pytest.mark.parametrize(
    "additional_data, continent",
    [
        ({"geo_info": {"country": "ZA"}}, "AF"),
        ({"geo_info": {"country": "AQ"}}, "AN"),
        ({"geo_info": {"country": "CN"}}, "AS"),
        ({"geo_info": {"country": "GB"}}, "EU"),
        ({"geo_info": {"country": "US"}}, "NA"),
        ({"geo_info": {"country": "AU"}}, "OC"),
        ({"geo_info": {"country": "AR"}}, "SA"),
        ({"geo_info": {"country": "Mordor"}}, "NO_CONTINENT"),
        ({"geo_info": {"bogon": True}}, "NO_CONTINENT"),
        ({"geo_info": {}}, "NO_CONTINENT"),
    ],
)
def test_get_src_ip_continent(additional_data, continent):
    assert continent == get_src_ip_continent(additional_data)
