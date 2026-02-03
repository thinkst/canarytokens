from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
import pytest

from canarytokens.pdfgen import make_canary_pdf
from canarytokens.settings import FrontendSettings


# change to >=1000 for statistical testing
@pytest.mark.parametrize("_", range(1))
def test_make_canary_pdf(frontend_settings: FrontendSettings, _: int):
    hostname = frontend_settings.NXDOMAINS[0].encode()
    pdf = PdfReader(
        BytesIO(
            make_canary_pdf(
                hostname=hostname,
                template=Path(frontend_settings.TEMPLATES_PATH) / "template.pdf",
            )
        )
    )
    assert pdf.pdf_header == "%PDF-1.6"
    assert pdf.get_num_pages() == 1
    assert pdf.get_object(16)["/URI"].startswith(f"http://{hostname.decode()}")
