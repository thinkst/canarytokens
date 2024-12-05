function Invoke-WindowsFakeFileSystem {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$RootPath,
        [Parameter(Mandatory = $false)]
        [bool]$DebugMode = $false
    )
    $alertDomain = "REPLACE_TOKEN_DOMAIN"
    $csharpCode = @"REPLACE_CSHARP_PROVIDER_CODE"@
    $filecsv = @"REPLACE_CSV_DIR_STRUCTURE"@

    try {
        if (-not ([System.Management.Automation.PSTypeName]'ProjectedFileSystemProvider.Program').Type) {
            Add-Type -TypeDefinition $csharpCode -Language CSharp
        }

        $args = @($RootPath, $filecsv, $alertDomain, $DebugMode.ToString())
        [ProjectedFileSystemProvider.Program]::Main($args)
    }
    catch {
        Write-Error "Error in Invoke-WindowsFakeFileSystem: $_"
        throw
    }
}

Invoke-WindowsFakeFileSystem
