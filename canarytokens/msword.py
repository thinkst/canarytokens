from __future__ import absolute_import

import datetime
import random
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from canarytokens.ziplib import (
    MODE_DIRECTORY,
    format_time_for_doc,
    zipinfo_contents_replace,
)


def make_canary_msword(url: str, template: Path):
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
