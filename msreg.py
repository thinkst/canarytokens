from cStringIO import StringIO

REG_TEMPLATE = """Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{PROCESS}]
"GlobalFlag"=dword:00000200

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\{PROCESS}]
"ReportingMode"=dword:00000001
"MonitorProcess"="cmd.exe /c start /min powershell.exe -windowstyle hidden -command \"&{{Resolve-DnsName -Name \\\"$env:computername.$env:username.CMD.{TOKEN_DNS}\\\"}}\""
"""

def make_canary_msreg(url=None, process_name='klist.exe'):
    output_buf = StringIO(REG_TEMPLATE.format(TOKEN_DNS=url, PROCESS=process_name))
    # TODO add registry file generation code
    return output_buf.getvalue()

