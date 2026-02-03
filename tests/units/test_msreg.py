import pytest

from canarytokens import msreg


@pytest.mark.parametrize(
    "process_name,token_hostname",
    [
        ("klist.exe", "qwer12334.canarytokens.org"),
        ("klist", "qwer12334.canarytokens.org"),
    ],
)
def test_make_canary_msreg(process_name, token_hostname):
    reg_file_info = msreg.make_canary_msreg(
        token_hostname=token_hostname, process_name=process_name
    )
    assert ".exe" in reg_file_info
    assert process_name in reg_file_info
    assert f"1..{msreg.INVOCATION_ID_LENGTH}" in reg_file_info
    assert "$c.UN.$u.CMD.$id." in reg_file_info
