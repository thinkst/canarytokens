from tempfile import SpooledTemporaryFile

import pytest

from canarytokens.models import UploadedExe, UploadedImage


@pytest.mark.parametrize(
    ("model", "content_type", "filename"),
    [
        (UploadedExe, "application/octet-stream", "token.exe"),
        (UploadedImage, "image/png", "token.png"),
    ],
)
def test_uploaded_file_serialization_excludes_file(model, content_type, filename):
    with SpooledTemporaryFile() as file:
        uploaded_file = model(
            content_type=content_type,
            filename=filename,
            file=file,
        )

        assert uploaded_file.model_dump(mode="json") == {
            "content_type": content_type,
            "filename": filename,
        }
