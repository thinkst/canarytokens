param(
    [string]$TaskName = "Microsoft_DataProcessor",
    [string]$ScriptPath = "$env:USERPROFILE\Scripts\Process-Data.ps1",
    [string]$TaskDescription = "Process data files in specified directory",
    [string]$RootPath = "REPLACE_ROOT_DIR",
    [switch]$Remove = $false
)

function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-ProjFSSupport {
    $osVersion = [System.Environment]::OSVersion.Version
    return $osVersion.Build -ge 17763
}

function Test-ProjFSEnabled {
    $feature = Get-WindowsOptionalFeature -Online -FeatureName "Client-ProjFS"
    return $feature.State -eq "Enabled"
}

function Install-ProjFS {
    Write-Host "Installing Projected File System..." -ForegroundColor Yellow

    if (-not (Test-Administrator)) {
        Write-Host "Administrator privileges required for Projected File System installation." -ForegroundColor Yellow
        exit
    }

    if (-not (Test-ProjFSSupport)) {
        Write-Host "Your Windows version does not support Projected File System. Minimum requirement is Windows 10 version 1809 (build 17763)." -ForegroundColor Yellow
        exit
    }

    if (Test-ProjFSEnabled) {
        Write-Host "Projected File System is already enabled." -ForegroundColor Green
        return
    }

    try {
        Enable-WindowsOptionalFeature -Online -FeatureName "Client-ProjFS" -NoRestart | Out-Null
        Write-Host "Successfully enabled Projected File System." -ForegroundColor Green
        return
    }
    catch {
        Write-Error "Failed to install Projected File System: $_"
        exit
    }
}

function New-ScheduledTask {
    Write-Host "Creating Windows Fake File System Token scheduled task..." -ForegroundColor Yellow

    if ((Test-Path -Path $RootPath -PathType Container) -and
        ($null -ne (Get-ChildItem -Path $RootPath -Force))) {
        Write-Host "Warning: Target folder '$RootPath' is not empty. Deployment cancelled." -ForegroundColor Red
        exit
    }

    $scriptsDir = "$env:USERPROFILE\Scripts"
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir | Out-Null
    }

    try {
        $processScript = @'
REPLACE_SCHEDULED_TASK
'@
        $processScript = $processScript + " -RootPath $RootPath"
        $processScript | Out-File -FilePath $ScriptPath -Force
        $FullUsername = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        $taskXml = @"
REPLACE_SCHEDULED_TASK_XML
"@

        $xmlPath = "$env:TEMP\task.xml"
        $taskXml | Out-File -FilePath $xmlPath -Encoding Unicode

        schtasks /create /tn $TaskName /xml $xmlPath /f | Out-Null

        if ($LastExitCode -eq 0) {
            Write-Host "Successfully deployed Windows Fake File System Token" -ForegroundColor Green
            return
        }
        else {
            Write-Error "Failed to deploy Windows Fake File System Token. Error code: $LastExitCode"
            exit
        }
    }
    catch {
        Write-Error "Failed to deploy Windows Fake File System Token: $_"
        exit
    }
    finally {
        if (Test-Path $xmlPath) {
            Remove-Item $xmlPath -Force
        }
    }
}

function Invoke-Step {
    param($Message, [scriptblock]$Action)
    try {
        & $Action
        Write-Host "++ $Message" -ForegroundColor Green
    }
    catch {
        Write-Host "-- $Message - Error: $_" -ForegroundColor Red
    }
}

function Remove-ProjFS {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RootPath,
        [Parameter(Mandatory = $true)]
        [string]$ScriptPath,
        [Parameter(Mandatory = $true)]
        [string]$TaskName
    )
    $ErrorActionPreference = "Stop"

    if (-not (Test-Administrator)) {
        Write-Host "Administrator privileges required to disable Projected File System." -ForegroundColor Yellow
        return $false
    }

    $projFSProcesses = Get-Process -Name powershell* | Where-Object {
        $_.Modules | Where-Object { $_.ModuleName -eq "ProjectedFSLib.dll" }
    }
    if ($projFSProcesses) {
        Write-Host "Found PowerShell processes using Projected File System Providers:"
        $projFSProcesses | ForEach-Object { Write-Host "PID: $($_.Id) - Path: $($_.Path)" }
        if ((Read-Host "Kill these processes? (Y/N)").ToUpper() -eq "Y") {
            Invoke-Step "Terminating Projected File System processes" {
                $projFSProcesses | Stop-Process -Force
            }
        }
    }

    Invoke-Step "Deleting script file" {
        if (Test-Path $ScriptPath) { Remove-Item $ScriptPath -Force }

        $ParentFolder = Split-Path -Parent $ScriptPath
        if (Test-Path -Path $ParentFolder -PathType Container) {
            $FolderContents = Get-ChildItem -Path $ParentFolder -Force

            if ($null -eq $FolderContents) {
                Remove-Item -Path $ParentFolder -Force
                Write-Host "Empty folder removed: $ParentFolder"
            }
            else {
                Write-Host "Warning: Folder '$ParentFolder' is not empty. Leaving in place." -ForegroundColor Yellow
            }
        }
    }

    Invoke-Step "Removing Projected File System feature" {
        Disable-WindowsOptionalFeature -Online -FeatureName "Client-ProjFS" -NoRestart | Out-Null
    }

    Invoke-Step "Removing folder" {
        cmd /c rmdir /s /q "$RootPath"
    }

    if ((Test-Path -Path $RootPath -PathType Container) -and
        ($null -ne (Get-ChildItem -Path $RootPath -Force))) {
        Write-Host "The target folder '$RootPath' could not be emptied as a file was still open. Please remove it manually" -ForegroundColor Yellow
    }

    Write-Host "NOTE: System reboot required to complete Projected File System removal." -ForegroundColor Yellow
    Write-Host "Windows Fake File System Token remove completed." -ForegroundColor Green
}

if ($Remove) {
    if ((Read-Host "Remove Windows Fake File System Token? (Y/N)") -notmatch '^[Yy]$') {
        exit
    }

    Remove-ProjFS -RootPath $RootPath -ScriptPath $ScriptPath -TaskName $TaskName
    exit
}

if ((Read-Host "Deploy Windows Fake File System Token? (Y/N)") -notmatch '^[Yy]$') {
    exit
}

Install-ProjFS
New-ScheduledTask
Start-ScheduledTask -TaskName $TaskName
