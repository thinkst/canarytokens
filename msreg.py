import tempfile
import shutil
import datetime
import random
import base64
from zipfile import ZipFile, ZipInfo
from ziplib import MODE_DIRECTORY
from cStringIO import StringIO

import settings

REG_TEMPLATE = """
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{PROCESS}]
"GlobalFlag"=dword:00000200

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\{PROCESS}]
"ReportingMode"=dword:00000001
"MonitorProcess"="cmd.exe /c start /min powershell.exe -windowstyle hidden -command \"&{Resolve-DnsName -Name \\\"$env:computername.$env:username.CMD.{TOKEN_DNS}}\\\"}\""
"""

def make_canary_msreg(url=None):
    output_buf = StringIO()
    # TODO add registry file generation code
    return output_buf.getvalue()

def format_time_for_doc(time):
    return time.strftime('%Y-%m-%d')+'T'+ time.strftime('%H:%M:%S')+'Z'

if __name__ == '__main__':
    print REG_TEMPLATE.format(PROCESS='klist.exe', TOKEN_DNS='blah.canarytokens.com')
