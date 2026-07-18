from __future__ import absolute_import

import base64
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


def _add_text_snippet(document_xml: str, text_snippet: str) -> str:
    paragraphs = []
    normalized_snippet = text_snippet.replace("\r\n", "\n").replace("\r", "\n")
    for line in normalized_snippet.split("\n"):
        if line:
            paragraphs.append(
                '<w:p><w:r><w:t xml:space="preserve">'
                f"{escape(line, quote=False)}"
                "</w:t></w:r></w:p>"
            )
        else:
            paragraphs.append("<w:p/>")

    section_properties = "<w:sectPr"
    if section_properties not in document_xml:
        raise ValueError("Microsoft Word template has no section properties")
    return document_xml.replace(
        section_properties, "".join(paragraphs) + section_properties, 1
    )


def make_canary_msword(
    url: str,
    template: Path,
    text_snippet: Optional[str] = None,
    text_snippet_base64: bool = False,
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
                if text_snippet_base64:
                    text_snippet = base64.b64encode(text_snippet.encode()).decode()
                contents = _add_text_snippet(contents, text_snippet)
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
