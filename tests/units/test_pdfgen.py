from pathlib import Path
import pytest

from canarytokens.pdfgen import make_canary_pdf
from canarytokens.settings import FrontendSettings


@pytest.mark.skip()
@pytest.mark.parametrize("_", range(1000))
def test_make_canary_pdf(frontend_settings: FrontendSettings, _: int):
    try:
        _ = make_canary_pdf(
            hostname=frontend_settings.NXDOMAINS[0].encode(),
            template=Path(frontend_settings.TEMPLATES_PATH) / "template.pdf",
        )
    except Exception:
        pytest.xfail()
