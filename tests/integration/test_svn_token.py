import subprocess
from contextlib import contextmanager
from typing import Union

import pytest

from canarytokens.models import (
    V2,
    V3,
    Memo,
    SvnTokenHistory,
    SvnTokenRequest,
    SvnTokenResponse,
    TokenTypes,
)
from canarytokens.webhook_formatting import TokenAlertDetailGeneric
from tests.utils import (
    create_token,
    get_stats_from_webhook,
    get_token_history,
    plain_fire_token,
    run_or_skip,
    v2,
    v3,
)


@contextmanager
def managed_svn_server(tmpdir_repo):

    # run svn server
    server_output = subprocess.check_output(
        [
            "svnserve",
            "-d",
            "-r",
            "{tmpdir}".format(tmpdir=tmpdir_repo),
            "--pid-file",
            "/tmp/svn.pid",
        ]
    )
    try:
        yield server_output
    finally:
        # kill the server
        server_pid = (
            subprocess.check_output(["cat /tmp/svn.pid"], shell=True).decode().strip()
        )
        server_output = subprocess.check_output(["kill", server_pid])


@pytest.mark.parametrize(
    "version",
    [
        v2,
        v3,
    ],
)
def test_svn_token(tmpdir, version: Union[V2, V3], webhook_receiver, runv2, runv3):
    run_or_skip(version, runv2=runv2, runv3=runv3)
    # create temp dir for the repo and client
    tmpdir_repo = tmpdir.mkdir("SVN")
    tmpdir_client = tmpdir.mkdir("SVN_ClIENT")

    # initialize SVN token request
    memo = "svn token memo!"
    token_request = SvnTokenRequest(
        token_type=TokenTypes.SVN,
        webhook_url=webhook_receiver,
        memo=Memo(memo),
    )

    # Create Svn token
    resp = create_token(token_request=token_request, version=version)
    token_info = SvnTokenResponse(**resp)

    # create svn repo
    repo_output = subprocess.check_output(
        ["svnadmin", "create", "{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_repo)],
    )

    with managed_svn_server(tmpdir_repo):
        # import svn repo
        import_output = subprocess.check_output(
            [
                "svn",
                "import",
                "{tmpdir}".format(tmpdir=tmpdir_client),
                "file://{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_repo),
                "-m",
                '"Import commit"',
            ],
        )

        # initial checkout, to create working directory
        checkout_output = subprocess.check_output(
            [
                "svn",
                "checkout",
                "file://{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_repo),
                "{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_client),
            ],
        )

        url = f"http://{token_info.hostname}"
        # set svn extras to token
        propset_output = subprocess.check_output(
            [
                'svn propset svn:externals "extras {url}" {tmpdir}/SVN_REPO'.format(
                    url=url, tmpdir=tmpdir_client
                ),
            ],
            shell=True,
        )

        # create commit
        commit_output = subprocess.check_output(
            [
                "svn",
                "commit",
                "-m",
                '"required commit"',
                "{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_client),
            ],
        )

        # checkout again , to trigger alert
        subprocess.Popen(
            [
                "svn",
                "checkout",
                "file://{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_repo),
                "{tmpdir}/SVN_REPO".format(tmpdir=tmpdir_client),
            ],
        )
        if not version.live:
            # locally switchboard is not handling dns. Trigger manually.
            plain_fire_token(token_info=token_info, version=version)

    assert repo_output == b""
    assert import_output == b""
    assert "property 'svn:externals' set on" in propset_output.decode()
    assert checkout_output == b"Checked out revision 0.\n"
    assert "Sending" in commit_output.decode()

    # Check that the returned history has a at least a single hit
    stats = get_stats_from_webhook(webhook_receiver, token=token_info.token)
    if stats:
        assert len(stats) >= 1
        assert stats[0]["memo"] == memo
        _ = TokenAlertDetailGeneric(**stats[0])

    resp = get_token_history(token_info=token_info, version=version)
    token_history = SvnTokenHistory(**resp)
    assert len(token_history.hits) >= 1
    token_hit = token_history.hits[0]
    assert token_hit.input_channel == "DNS"
