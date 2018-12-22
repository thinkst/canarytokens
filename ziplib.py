import sys
import tempfile
import datetime
from os import unlink, close
from zipfile import ZipFile, ZipInfo

def printzip(zip):
    print '\t{extattr:b}\t{extattr:02x}\t{intattr:b}\t-\t{name}'.format(extattr=zip.external_attr,intattr=zip.internal_attr,name=zip.filename)

MODE_READONLY  = 0x01
MODE_HIDDEN    = 0x02
MODE_SYSTEM    = 0x04
MODE_DIRECTORY = 0x10
MODE_ARCHIVE   = 0x20
MODE_FILE      = 0x80

def make_canary_desktop_ini(hostname=None,dummyfile='resource.dll'):
    return (u'\r\n[.ShellClassInfo]\r\nIconResource=\\\\%USERNAME%.%COMPUTERNAME%.%DOMAIN%.INI.'\
           +unicode(hostname)\
           +unicode('\\'+dummyfile+'\r\n')).encode('utf16')

def make_dir_entry(name=None, date_time=None, mode=MODE_DIRECTORY):
    tt = date_time.timetuple()
    dir = ZipInfo()

    dir.filename        = name+('/' if name[-1] != '/' else '')
    dir.orig_filename   = dir.filename
    dir.date_time        = date_time.isocalendar() + (tt.tm_hour,
                                                tt.tm_min, tt.tm_sec)
    dir.compress_type   = 0
    dir.create_system   = 0
    dir.create_version  = 20
    dir.extract_version = 10
    dir.external_attr   = mode

    return dir

def make_file_entry(name=None, date_time=None, mode=MODE_FILE | MODE_ARCHIVE):
    tt = date_time.timetuple()
    file = ZipInfo()

    file.filename        = name
    file.orig_filename   = file.filename
    file.date_time        = date_time.isocalendar() + (tt.tm_hour,
                                                tt.tm_min, tt.tm_sec)
    file.compress_type   = 8
    file.create_system   = 0
    file.create_version  = 20
    file.extract_version = 20
    file.flag_bits       = 2
    file.external_attr   = mode

    return file

def create_zip(name=None):
    return ZipFile(name, 'w')

def write_file(zip=None, name=None, system=False, hidden=False, readonly=False,
                archive=True, date_time=datetime.datetime.utcnow(), contents='', ):
    mode = MODE_FILE
    mode |= MODE_HIDDEN if hidden else 0
    mode |= MODE_SYSTEM if system else 0
    mode |= MODE_READONLY if readonly else 0
    mode |= MODE_ARCHIVE if archive else 0
    entry = make_file_entry(name=name, mode=mode, date_time=date_time)
    zip.writestr(entry, contents)

def write_dir(zip=None, name=None, system=False, hidden=False, readonly=False,
                archive=False, date_time=datetime.datetime.utcnow()):
    mode = MODE_DIRECTORY
    mode |= MODE_HIDDEN if hidden else 0
    mode |= MODE_SYSTEM if system else 0
    mode |= MODE_READONLY if readonly else 0
    mode |= MODE_ARCHIVE if archive else 0
    entry = make_dir_entry(name=name, mode=mode, date_time=date_time)
    zip.writestr(entry, '')

def write_weird(zip=None, name=None, system=False, hidden=False, readonly=False,
                archive=False, directory=False, date_time=datetime.datetime.utcnow(),
                file=False, contents=''):
    mode = 0
    mode |= MODE_HIDDEN if hidden else 0
    mode |= MODE_SYSTEM if system else 0
    mode |= MODE_READONLY if readonly else 0
    mode |= MODE_ARCHIVE if archive else 0
    mode |= MODE_DIRECTORY if directory else 0
    mode |= MODE_FILE      if file else 0
    entry = make_file_entry(name=name, mode=mode, date_time=date_time)
    zip.writestr(entry, contents)

def make_canary_zip(hostname=None):
    (fd, fname) = tempfile.mkstemp()
    archive = create_zip(name=fname)
    write_dir(zip=archive,   name='My Documents/', system=True)
    write_file(zip=archive,  name='My Documents/desktop.ini',
                   contents=make_canary_desktop_ini(hostname=hostname),
                   system=True, hidden=True)
    archive.close()
    close(fd)

    with open(fname, 'r') as f:
        contents = f.read()
    unlink(fname)

    return contents

if __name__ == '__main__':
    archive = create_zip(name='test1.zip')
    write_dir(zip=archive,   name='test')
    write_dir(zip=archive,   name='test/normal-dir')
    write_file(zip=archive,  name='test/normal-dir/file1.txt', contents='hello!')
    write_dir(zip=archive,   name='test/sysdir')
    write_file(zip=archive,  name='test/sysdir/file1.txt', contents='i am system!', system=True, hidden=True)
    write_dir(zip=archive,   name='test/weirddir/')
    write_weird(zip=archive, name='test/weirddir/file2.txt', contents='i am weird!', system=True, hidden=True, archive=True, readonly=True, directory=True, file=True)
    write_weird(zip=archive, name='test/weirddir/file2.txt/fooo.txt', contents='i am weird 2!', system=True, hidden=True, archive=True, readonly=True, directory=True, file=True)
    archive.close()



    archive = create_zip(name='test1.zip')
    write_dir(zip=archive,   name='test/', system=True)
    write_file(zip=archive,  name='test/desktop.ini', contents=make_canary_desktop_ini(hostname='xxxx5.canarydrops.net'), system=True, hidden=True)
    archive.close()
