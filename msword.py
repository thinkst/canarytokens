import tempfile
import shutil
import datetime
import random
from zipfile import ZipFile, ZipInfo
from ziplib import MODE_DIRECTORY
from cStringIO import StringIO

import settings

WORD_TEMPLATE=settings.CANARY_WORD_TEMPLATE

def zipinfo_contents_replace(zipfile=None, zipinfo=None, 
                             search=None, replace=None):
    """Given an entry in a zip file, extract the file and perform a search
       and replace on the contents. Returns the contents as a string."""
    dirname = tempfile.mkdtemp()
    fname = zipfile.extract(zipinfo, dirname)
    with open(fname, 'r') as fd:
        contents = fd.read().replace(search, replace)
    shutil.rmtree(dirname)
    return contents

def make_canary_msword(url=None, template=WORD_TEMPLATE):
    with open(template, 'r') as f:
        input_buf = StringIO(f.read())
    output_buf = StringIO()
    output_zip = ZipFile(output_buf, 'w')
    now = datetime.datetime.now()
    now_ts = format_time_for_doc(now)
    created_ts = format_time_for_doc(now - datetime.timedelta(
        days=random.randint(1,25),
        hours=random.randint(1,24),
        seconds=random.randint(1,60)))
    with ZipFile(input_buf, 'r') as doc:
        for entry in doc.filelist:
            if entry.external_attr & MODE_DIRECTORY:
                continue

            contents = zipinfo_contents_replace(zipfile=doc, zipinfo=entry,
                                        search="HONEYDROP_TOKEN_URL", replace=url)
            contents = contents.replace("aaaaaaaaaaaaaaaaaaaa", created_ts)
            contents = contents.replace("bbbbbbbbbbbbbbbbbbbb", now_ts)
            output_zip.writestr(entry, contents)
    output_zip.close()
    return output_buf.getvalue()

def format_time_for_doc(time):
    return time.strftime('%Y-%m-%d')+'T'+ time.strftime('%H:%M:%S')+'Z'

if __name__ == '__main__':
    with open('testdoc.docx', 'w+') as f:
        f.write(make_canary_msword(url="http://iamatesturlforcanarys.net/blah.png"))
