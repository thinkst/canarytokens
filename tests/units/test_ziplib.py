import datetime

from canarytokens import ziplib
from canarytokens.ziplib import format_time_for_doc, make_canary_zip, make_dir_entry


def test_make_canary_zip():
    hostname = "a.b.c"
    # The zip file contains a timestamp, so the final file will be different every time,
    # but we can make sure that the file path we expect is in there.
    assert b"My Documents/desktop.ini" in make_canary_zip(hostname)


def test_make_dir_entry_fail():
    try:
        make_dir_entry("", datetime.datetime.utcnow())
        raise AssertionError("make_dir_entry should fail on empty name")
    except ValueError:
        pass


def test_make_dir_entry():
    zipinfo = make_dir_entry("filename", datetime.datetime.utcnow())
    assert zipinfo.filename == "filename/"
    assert zipinfo.external_attr == ziplib.MODE_DIRECTORY


def test_format_time_for_doc():
    time = datetime.datetime(2013, 4, 5, 16, 57, 58)
    assert format_time_for_doc(time) == "2013-04-05T16:57:58Z"
