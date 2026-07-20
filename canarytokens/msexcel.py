from __future__ import absolute_import

import datetime
import random
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from canarytokens.ziplib import (
    MODE_DIRECTORY,
    format_time_for_doc,
    zipinfo_contents_replace,
)


def _add_plaintext_snippet(sheet_xml: str, text_snippet: str) -> str:
    sheet_data = "<sheetData/>"
    if sheet_data not in sheet_xml:
        raise ValueError("Microsoft Excel template has no empty sheet data")
    cell = (
        '<sheetData><row r="1"><c r="A1" t="inlineStr"><is><t xml:space="preserve">'
        f"{escape(text_snippet, quote=False)}"
        "</t></is></c></row></sheetData>"
    )
    return sheet_xml.replace(sheet_data, cell, 1)


def make_canary_msexcel(
    url: str,
    template: Path,
    text_snippet: Optional[str] = None,
):
    with open(template, "rb") as f:
        input_buf = BytesIO(f.read())
    output_buf = BytesIO()
    output_zip = ZipFile(output_buf, "w")
    now = datetime.datetime.now()
    now_ts = format_time_for_doc(now)
    created_ts = format_time_for_doc(
        now
        - datetime.timedelta(
            days=random.randint(1, 25),
            hours=random.randint(1, 24),
            seconds=random.randint(1, 60),
        )
    )
    with ZipFile(input_buf, "r") as doc:
        for entry in doc.filelist:
            if entry.external_attr & MODE_DIRECTORY:
                continue

            contents = zipinfo_contents_replace(
                zipfile=doc, zipinfo=entry, search="HONEYDROP_TOKEN_URL", replace=url
            )
            contents = contents.replace("aaaaaaaaaaaaaaaaaaaa", created_ts)
            contents = contents.replace("bbbbbbbbbbbbbbbbbbbb", now_ts)
            if entry.filename == "xl/worksheets/sheet1.xml" and text_snippet:
                contents = _add_plaintext_snippet(contents, text_snippet)
            output_zip.writestr(entry, contents)
    output_zip.close()
    return output_buf.getvalue()


if __name__ == "__main__":  # pragma: no cover
    with open("testdoc.xlsx", "wb") as f:
        f.write(make_canary_msexcel(url="http://iamatesturlforcanarys.net/blah.png"))
