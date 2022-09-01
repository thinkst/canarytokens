from __future__ import absolute_import, print_function

import datetime
import shutil
import tempfile
from os import close, unlink
from zipfile import ZipFile, ZipInfo

MODE_READONLY = 0x01
MODE_HIDDEN = 0x02
MODE_SYSTEM = 0x04
MODE_DIRECTORY = 0x10
MODE_ARCHIVE = 0x20
MODE_FILE = 0x80


# def printzip(zip):
#     print(
#         "\t{extattr:b}\t{extattr:02x}\t{intattr:b}\t-\t{name}".format(
#             extattr=zip.external_attr, intattr=zip.internal_attr, name=zip.filename
#         )
#     )


def make_canary_desktop_ini(hostname: str, dummyfile: str = "resource.dll") -> bytes:
    return (
        "\r\n[.ShellClassInfo]\r\nIconResource=\\\\%USERNAME%.%COMPUTERNAME%.%USERDOMAIN%.INI."
        + hostname
        + "\\"
        + dummyfile
        + "\r\n"
    ).encode("utf-16")


def make_dir_entry(
    name: str, date_time: datetime.datetime, mode: int = MODE_DIRECTORY
) -> ZipInfo:
    tt = date_time.timetuple()
    dir = ZipInfo()
    if len(name) == 0:
        raise ValueError("make_dir_entry: name cannot be empty")
    dir.filename = name + ("/" if name[-1] != "/" else "")
    dir.orig_filename = dir.filename
    dir.date_time = date_time.isocalendar() + (tt.tm_hour, tt.tm_min, tt.tm_sec)
    dir.compress_type = 0
    dir.create_system = 0
    dir.create_version = 20
    dir.extract_version = 10
    dir.external_attr = mode

    return dir


def make_file_entry(
    name: str, date_time: datetime.datetime, mode: int = MODE_FILE | MODE_ARCHIVE
) -> ZipInfo:
    tt = date_time.timetuple()
    file = ZipInfo()

    file.filename = name
    file.orig_filename = file.filename
    file.date_time = date_time.isocalendar() + (tt.tm_hour, tt.tm_min, tt.tm_sec)
    file.compress_type = 8
    file.create_system = 0
    file.create_version = 20
    file.extract_version = 20
    file.flag_bits = 2
    file.external_attr = mode

    return file


def create_zip(name: str):
    return ZipFile(name, "w")


def write_file(
    zip: ZipFile,
    name: str,
    system: bool = False,
    hidden: bool = False,
    readonly: bool = False,
    archive: bool = True,
    date_time=datetime.datetime.utcnow(),
    contents: bytes = b"",
):
    mode = MODE_FILE
    mode |= MODE_HIDDEN if hidden else 0
    mode |= MODE_SYSTEM if system else 0
    mode |= MODE_READONLY if readonly else 0
    mode |= MODE_ARCHIVE if archive else 0
    entry = make_file_entry(name=name, mode=mode, date_time=date_time)
    zip.writestr(zinfo_or_arcname=entry, data=contents)


def write_dir(
    zip: ZipFile,
    name: str,
    system: bool = False,
    hidden: bool = False,
    readonly: bool = False,
    archive: bool = False,
    date_time=datetime.datetime.utcnow(),
) -> None:
    mode = MODE_DIRECTORY
    mode |= MODE_HIDDEN if hidden else 0
    mode |= MODE_SYSTEM if system else 0
    mode |= MODE_READONLY if readonly else 0
    mode |= MODE_ARCHIVE if archive else 0
    entry = make_dir_entry(name=name, mode=mode, date_time=date_time)
    zip.writestr(entry, "")


# def write_weird(
#     zip=None,
#     name=None,
#     system=False,
#     hidden=False,
#     readonly=False,
#     archive=False,
#     directory=False,
#     date_time=datetime.datetime.utcnow(),
#     file=False,
#     contents="",
# ):
#     mode = 0
#     mode |= MODE_HIDDEN if hidden else 0
#     mode |= MODE_SYSTEM if system else 0
#     mode |= MODE_READONLY if readonly else 0
#     mode |= MODE_ARCHIVE if archive else 0
#     mode |= MODE_DIRECTORY if directory else 0
#     mode |= MODE_FILE if file else 0
#     entry = make_file_entry(name=name, mode=mode, date_time=date_time)
#     zip.writestr(entry, contents)


def make_canary_zip(hostname: str) -> bytes:
    (fd, fname) = tempfile.mkstemp()
    archive = create_zip(name=fname)
    write_dir(zip=archive, name="My Documents/", system=True)
    write_file(
        zip=archive,
        name="My Documents/desktop.ini",
        contents=make_canary_desktop_ini(hostname=hostname),
        system=True,
        hidden=True,
    )
    archive.close()
    close(fd)

    with open(fname, "rb") as f:
        contents = f.read()
    unlink(fname)

    return contents


def zipinfo_contents_replace(
    zipfile: ZipFile, zipinfo: ZipInfo, search: str, replace: str
):
    """Given an entry in a zip file, extract the file and perform a search
    and replace on the contents. Returns the contents as a string."""
    dirname = tempfile.mkdtemp()
    fname = zipfile.extract(zipinfo, dirname)
    with open(fname, "r") as fd:
        contents = fd.read().replace(search, replace)
    shutil.rmtree(dirname)
    return contents


def format_time_for_doc(time):
    return time.strftime("%Y-%m-%d") + "T" + time.strftime("%H:%M:%S") + "Z"


# if __name__ == "__main__": # pragma: no cover
#     archive = create_zip(name="test1.zip")
#     write_dir(zip=archive, name="test")
#     write_dir(zip=archive, name="test/normal-dir")
#     write_file(zip=archive, name="test/normal-dir/file1.txt", contents="hello!")
#     write_dir(zip=archive, name="test/sysdir")
#     write_file(
#         zip=archive,
#         name="test/sysdir/file1.txt",
#         contents="i am system!",
#         system=True,
#         hidden=True,
#     )
#     write_dir(zip=archive, name="test/weirddir/")
#     write_weird(
#         zip=archive,
#         name="test/weirddir/file2.txt",
#         contents="i am weird!",
#         system=True,
#         hidden=True,
#         archive=True,
#         readonly=True,
#         directory=True,
#         file=True,
#     )
#     write_weird(
#         zip=archive,
#         name="test/weirddir/file2.txt/fooo.txt",
#         contents="i am weird 2!",
#         system=True,
#         hidden=True,
#         archive=True,
#         readonly=True,
#         directory=True,
#         file=True,
#     )
#     archive.close()

#     archive = create_zip(name="test1.zip")
#     write_dir(zip=archive, name="test/", system=True)
#     write_file(
#         zip=archive,
#         name="test/desktop.ini",
#         contents=make_canary_desktop_ini(hostname="xxxx5.canarydrops.net"),
#         system=True,
#         hidden=True,
#     )
#     archive.close()
