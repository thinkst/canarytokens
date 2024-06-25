import gzip
import random
import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZipInfo

from canarytokens.ziplib import MODE_DIRECTORY

DATABASE_NAMES = [
    "db397638123",
    "cw",
    "dwq",
    "employees",
    "staff",
    "db01",
    "db02",
    "db03",
    "db",
    "data",
]

DUMP_HEADER = f"""-- MySQL dump 10.13  Distrib 8.0.26, for Linux (x86_64)
--
-- Host: localhost    Database: {random.choice(DATABASE_NAMES)}
-- ------------------------------------------------------
-- Server version	8.0.26

""".encode()


def zipinfo_contents(zipfile: ZipFile, zipinfo: ZipInfo) -> bytes:
    """Given an entry in a zip file, extract the file and perform a search
    and replace on the contents. Returns the contents as a string."""
    dirname = tempfile.mkdtemp()
    fname = zipfile.extract(zipinfo, dirname)
    with open(fname, "r") as fd:
        contents = fd.read().encode()
    shutil.rmtree(dirname)
    return contents


def make_canary_mysql_dump(mysql_usage: str, template: Path) -> bytes:
    sql_statement = mysql_usage.encode()

    with open(template, "rb") as f:
        template_buf = BytesIO(f.read())
    output_buf = BytesIO()
    output_zip = gzip.GzipFile(fileobj=output_buf, mode="wb")
    file_build_start = True
    table_counter = 0
    with ZipFile(template_buf, "r") as doc:
        doc_list = doc.filelist
        table_list = [
            f.filename
            for f in filter(
                lambda f: (
                    f.filename.startswith("dw_") and f.filename.endswith(".sql")
                ),
                doc_list,
            )
        ]
        min_table_count = len(table_list) // 2
        table_count = random.choice(list(range(min_table_count, len(table_list) + 1)))
        tables = random.sample(table_list, table_count)
        random.shuffle(doc_list)
        for entry in doc_list:
            if entry.external_attr & MODE_DIRECTORY or entry.filename not in tables:
                continue

            if file_build_start:
                output_zip.write(DUMP_HEADER)
                file_build_start = False

            # insert the token somewhere in the middle
            if table_counter == min_table_count // 2:
                output_zip.write(sql_statement)

            contents = zipinfo_contents(zipfile=doc, zipinfo=entry)
            output_zip.write(contents)

            table_counter += 1

    output_zip.write(b"-- Dump completed on 2021-08-11 18:47:51")
    output_zip.close()
    return output_buf.getvalue()


if __name__ == "__main__":

    class CanarydropTest:
        def get_hostname(self):
            return "w9fxd0qkpilgaesjzgohkfsmc.ssl-secure-srv.com"

        @property
        def canarytoken(self):
            return "w9fxd0qkpilgaesjzgohkfsmc"

    c = CanarydropTest()

    magic_sauce = (
        "SET @bb = CONCAT(\"CHANGE REPLICATION SOURCE TO SOURCE_PASSWORD='my-secret-pw', SOURCE_RETRY_COUNT=1, SOURCE_PORT=3306,"
        + f"SOURCE_HOST='{c.get_hostname()}', SOURCE_USER='{c.canarytoken()}\", @@lc_time_names, @@hostname, \"';\");"
    )

    with open("mysql_dump.sql.gz", "wb+") as f:
        f.write(
            make_canary_mysql_dump(
                mysql_usage=magic_sauce, template=Path("../templates/mysql_tables.zip")
            )
        )
