import tempfile
from os import unlink

from canarytokens.sign_file import authenticode_sign_binary


def make_canary_authenticode_binary(  # pragma: no cover
    nxdomain_token_url: str, filebody: bytes
) -> bytes:
    """Takes in a nxdomain url (eg: http://{token}.nxdomain.tools) and bytes string (some binary to sign)
    and returns bytes (the signed binary).

    Args:
        nxdomain_token_url (str): The NXDOMAIN that will be looked up when binary is run/loaded triggering the token.
        filebody (bytes): Raw bytes of the binary to sign.

    Raises:
        Exception: Raises an exception if signing fails.

    Returns:
        bytes: Signed binary as bytes.
    """
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as unsigned_file:
        unsigned_file.write(filebody)

    tempdir = tempfile.TemporaryDirectory()
    signed_file_name = "{dir}/signed_file".format(dir=tempdir.name)

    authenticode_sign_binary(
        nxdomain_token_url=nxdomain_token_url,
        inputfile=unsigned_file.name,
        outputfile=signed_file_name,
    )
    with open(signed_file_name, "rb") as fp:
        contents = fp.read()

    unlink(unsigned_file.name)

    if len(contents) == 0:
        raise Exception("Could not sign this file.")
    return contents
