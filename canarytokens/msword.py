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


def _add_plaintext_snippet(document_xml: str, text_snippet: str) -> str:
    section_properties = "<w:sectPr"
    if section_properties not in document_xml:
        raise ValueError("Microsoft Word template has no section properties")

    lines = text_snippet.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    snippet_runs = []
    for index, line in enumerate(lines):
        if index:
            snippet_runs.append("<w:r><w:br/></w:r>")
        snippet_runs.append(
            f'<w:r><w:t xml:space="preserve">{escape(line, quote=False)}</w:t></w:r>'
        )
    snippet_paragraph = f"<w:p>{''.join(snippet_runs)}</w:p>"
    return document_xml.replace(
        section_properties, snippet_paragraph + section_properties, 1
    )


def make_canary_msword(
    url: str,
    template: Path,
    text_snippet: Optional[str] = None,
) -> bytes:
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
            if entry.filename == "word/document.xml" and text_snippet:
                contents = _add_plaintext_snippet(contents, text_snippet)
            output_zip.writestr(entry, contents)
    output_zip.close()
    return output_buf.getvalue()


if __name__ == "__main__":  # pragma: no cover
    with open("testdoc.docx", "wb") as f:
        f.write(
            make_canary_msword(
                url="http://iamatesturlforcanarys.net/blah.png",
                template="/workspace/templates/template.docx",
            )
        )
