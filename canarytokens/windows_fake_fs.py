from datetime import datetime
import random
from math import floor
from io import StringIO
from csv import DictWriter

from canarytokens.models import Hostname

PS_TEMPLATE = r"""
# CanaryFS-Wrapper.ps1
param(
    [string]$TaskName = "Microsoft_DataProcessor",
    [string]$ScriptPath = "$env:USERPROFILE\Scripts\Process-Data.ps1",
    [string]$TaskDescription = "Process data files in specified directory",
    [string]$RootPath = "{ROOT_DIR}"
)

# Function Definitions
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
    Write-Host "`nInstalling Projected File System..." -ForegroundColor Yellow

    if (-not (Test-Administrator)) {
        Write-Host "Administrator privileges required for ProjFS installation." -ForegroundColor Yellow
        return $false
    }

    if (-not (Test-ProjFSSupport)) {
        Write-Host "Your Windows version does not support Projected File System. Minimum requirement is Windows 10 version 1809 (build 17763)." -ForegroundColor Yellow
        return $false
    }

    if (Test-ProjFSEnabled) {
        Write-Host "Projected File System is already enabled." -ForegroundColor Green
        return $true
    }

    try {
        Enable-WindowsOptionalFeature -Online -FeatureName "Client-ProjFS" -NoRestart
        return $true
    }
    catch {
        Write-Error "Failed to install ProjFS: $_"
        return $false
    }
}

function Create-ScheduledTask {
    Write-Host "`nCreating Scheduled Task..." -ForegroundColor Yellow

    # Verify Scripts directory and root path
    $scriptsDir = "$env:USERPROFILE\Scripts"
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir
    }

    if ((Test-Path -Path $RootPath -PathType Container) -and
        ($null -ne (Get-ChildItem -Path $RootPath -Force))) {
        Write-Host "Warning: Target folder '$RootPath' is not empty. Task creation cancelled." -ForegroundColor Red
        return $false
    }

    try {
        $processScript = @'
        function Invoke-CanaryFS {
            [CmdletBinding()]
            param (
                [Parameter(Mandatory = $true)]
                [ValidateNotNullOrEmpty()]
                [string]$RootPath,

                [Parameter(Mandatory = $false)]
                [bool]$DebugMode = $false
            )
            $alertDomain = "{TOKEN_DOMAIN}"
            $csharpCode = @"
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Net;
using System.Threading.Tasks;

namespace ProjectedFileSystemProvider
{
    public class Program
    {
        public static void Main(string[] args)
        {

            // Expecting parameters in the format: rootPath debugMode csvFileName
            if (args.Length != 4)
            {
                Console.WriteLine("Usage: CanaryFS.exe <rootPath> <fileCsv> <alertDomain> <debugMode>");
                return;
            }

            string rootPath = args[0];
            bool enableDebug = bool.Parse(args[3]);
            string alertDomain = args[2];
            string csvStr = args[1];
            Guid _guid = Guid.NewGuid();

            Console.WriteLine("Virtual Folder: " + rootPath);
            Console.WriteLine("Debug Mode: " + enableDebug);

            try
            {
                // Check if the root directory exists, create it if it doesn't
                if (!Directory.Exists(rootPath) )
                {
                    Directory.CreateDirectory(rootPath);
                    Console.WriteLine("Created directory: " + rootPath);
                }

                // Check available disk space
                DriveInfo drive = new DriveInfo(Path.GetPathRoot(rootPath));
                Console.WriteLine("Available free space: " + drive.AvailableFreeSpace + " bytes");

                var provider = new ProjFSProvider(rootPath, csvStr, alertDomain, enableDebug);

                int result = ProjFSNative.PrjMarkDirectoryAsPlaceholder(rootPath, null, IntPtr.Zero, ref _guid);

                provider.StartVirtualizing();

                Console.WriteLine("Projected File System Provider started. Press any key to exit.");
                Console.ReadKey();

                provider.StopVirtualizing();
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: " + ex.Message);
                if (ex is System.ComponentModel.Win32Exception)
                {
                    Console.WriteLine("Win32 Error Code: " + ((System.ComponentModel.Win32Exception)ex).NativeErrorCode);
                }
            }

        }
    }

    class ProjFSProvider
    {
        private readonly string rootPath;
        private readonly Dictionary<string, List<FileEntry>> fileSystem = new Dictionary<string, List<FileEntry>>();
        private IntPtr instanceHandle;
        private readonly bool enableDebug;

        private readonly string alertDomain;

        private static string BytesToBase32(byte[] bytes) {
            const string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
            string output = "";
            for (int bitIndex = 0; bitIndex < bytes.Length * 8; bitIndex += 5) {
                int dualbyte = bytes[bitIndex / 8] << 8;
                if (bitIndex / 8 + 1 < bytes.Length)
                    dualbyte |= bytes[bitIndex / 8 + 1];
                dualbyte = 0x1f & (dualbyte >> (16 - bitIndex % 8 - 5));
                output += alphabet[dualbyte];
            }

            return output;
        }

        private void AlertOnFileAccess(string filePath, string imgFileName)
        {
            string filename = filePath.Split('\\')[filePath.Split('\\').Length - 1];
            string imgname = imgFileName.Split('\\')[imgFileName.Split('\\').Length - 1];
            string fnb32 = BytesToBase32(Encoding.UTF8.GetBytes(filename));
            string inb32 = BytesToBase32(Encoding.UTF8.GetBytes(imgname));
            Random rnd = new Random();
            string uniqueval = "u" + rnd.Next(1000, 10000).ToString() + ".";

            try {
                // Resolve the DNS
                Task.Run(() => Dns.GetHostEntry(uniqueval + "f" + fnb32 + ".i" + inb32 + "." + alertDomain));
            } catch (Exception ex) {
                Console.WriteLine("Error: " + ex.Message);
            }
        }

        public ProjFSProvider(string rootPath, string csvStr, string alertDomain, bool enableDebug)
        {
            this.rootPath = rootPath;
            this.enableDebug = enableDebug;
            this.alertDomain = alertDomain;
            LoadFileSystemFromCsvString(csvStr);
        }

        private void LoadFileSystemFromCsvString(string csvStr)
        {
            foreach (var line in csvStr.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None))
            {
                var parts = line.Split(',');
                if (parts.Length != 4) continue;

                string path = parts[0].TrimStart('\\');
                string name = Path.GetFileName(path);
                string parentPath = Path.GetDirectoryName(path);
                bool isDirectory = bool.Parse(parts[1]);
                long fileSize = long.Parse(parts[2]);

                // Parse Unix timestamp
                long unixTimestamp = long.Parse(parts[3]);
                DateTime lastWriteTime = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddSeconds(unixTimestamp);

                if (string.IsNullOrEmpty(parentPath))
                {
                    parentPath = "\\";
                }

                if (!fileSystem.ContainsKey(parentPath))
                {
                    fileSystem[parentPath] = new List<FileEntry>();
                }

                fileSystem[parentPath].Add(new FileEntry
                {
                    Name = name,
                    IsDirectory = isDirectory,
                    FileSize = fileSize,
                    LastWriteTime = lastWriteTime,
                    Opened = false,
                    LastAlert = 0
                });
            }
        }

        public void StartVirtualizing()
        {
            ProjFSNative.PrjCallbacks callbacks = new ProjFSNative.PrjCallbacks
            {
                StartDirectoryEnumerationCallback = StartDirectoryEnumeration,
                EndDirectoryEnumerationCallback = EndDirectoryEnumeration,
                GetDirectoryEnumerationCallback = GetDirectoryEnumeration,
                GetPlaceholderInfoCallback = GetPlaceholderInfo,
                NotificationCallback = NotificationCB,
                GetFileDataCallback = GetFileData
            };

            ProjFSNative.PrjStartVirutalizingOptions options = new ProjFSNative.PrjStartVirutalizingOptions
            {
                flags = ProjFSNative.PrjStartVirutalizingFlags.PrjFlagNone,
                PoolThreadCount = 1,
                ConcurrentThreadCount = 1,
                NotificationMappings = new ProjFSNative.PrjNotificationMapping(),
                NotificationMappingCount = 0
            };

            Console.WriteLine("Attempting to start virtualization...");
            int hr = ProjFSNative.PrjStartVirtualizing(rootPath, ref callbacks, IntPtr.Zero, IntPtr.Zero, ref instanceHandle);
            if (hr != 0)
            {
                Console.WriteLine("PrjStartVirtualizing failed. HRESULT: " + hr);
                throw new System.ComponentModel.Win32Exception(hr);
            }
            Console.WriteLine("Virtualization started successfully.");
        }

        public void StopVirtualizing()
        {
            if (instanceHandle != IntPtr.Zero)
            {
                Console.WriteLine("Stopping virtualization...");

                ProjFSNative.PrjStopVirtualizing(instanceHandle);
                instanceHandle = IntPtr.Zero;

                // This is ugly to remove any hydrated files/folders.
                DirectoryInfo di = new DirectoryInfo(rootPath);
                foreach (FileInfo file in di.GetFiles())
                {
                    file.Delete();
                }
                foreach (DirectoryInfo dir in di.GetDirectories())
                {
                    dir.Delete(true);
                }

                Console.WriteLine("Virtualization stopped.");
            }
        }

        private long GetUnixTimeStamp()
        {
            long ticks = DateTime.UtcNow.Ticks - DateTime.Parse("01/01/1970 00:00:00").Ticks;
            ticks /= 10000000; //Convert windows ticks to seconds
            return ticks;
        }

        private int NotificationCB(ProjFSNative.PrjCallbackData callbackData, bool isDirectory, ProjFSNative.PrjNotification notification, string destinationFileName, ref ProjFSNative.PrjNotificationParameters operationParameters)
        {
            if (notification != ProjFSNative.PrjNotification.FileOpened || isDirectory)
                return 0;

            string parentPath = Path.GetDirectoryName(callbackData.FilePathName);
            if (string.IsNullOrEmpty(parentPath))
            {
                parentPath = "\\";
            }
            string fileName = Path.GetFileName(callbackData.FilePathName);

            List<FileEntry> entries;
            if (!fileSystem.TryGetValue(parentPath, out entries))
            {
                return 0; // FILE_NOT_FOUND
            }

            var entry = entries.Find(e => e.Name == fileName.ToLower());
            if (entry == null || entry.IsDirectory)
            {
                DebugWrite("File is a dir?!");
                return 0; // ERROR_FILE_NOT_FOUND
            }
            if (entry.Opened && (GetUnixTimeStamp() - entry.LastAlert) > 5)
            {
                entry.LastAlert = GetUnixTimeStamp();
                AlertOnFileAccess(callbackData.FilePathName.ToLower(), callbackData.TriggeringProcessImageFileName);
            }

            //DebugWrite(string.Format("Got {0} as a notification for {1}!", notification, callbackData.FilePathName.ToLower()));
            return 0;
        }

        private int StartDirectoryEnumeration(ProjFSNative.PrjCallbackData callbackData, ref Guid enumerationId)
        {
            DebugWrite(string.Format("StartDirectoryEnumeration: {0}", callbackData.FilePathName ?? "\\"));
            return 0;
        }

        private int EndDirectoryEnumeration(ProjFSNative.PrjCallbackData callbackData, ref Guid enumerationId)
        {
            DebugWrite("EndDirectoryEnumeration");
            if (enumerationIndices.ContainsKey(enumerationId)) {
                enumerationIndices.Remove(enumerationId);
            }
            return 0;
        }

        private Dictionary<Guid, int> enumerationIndices = new Dictionary<Guid, int>();

        private int GetDirectoryEnumeration(ProjFSNative.PrjCallbackData callbackData, ref Guid enumerationId, string searchExpression, IntPtr dirEntryBufferHandle)
        {
            string directoryPath = callbackData.FilePathName ?? "";
            bool single = false;
            DebugWrite(string.Format("GetDirectoryEnumeration: {0}, {1}, EnumerationId: {2}", directoryPath, searchExpression, enumerationId));

            // Handle root directory
            if (string.IsNullOrEmpty(directoryPath))
            {
                directoryPath = "\\";
            }

            List<FileEntry> entries;
            if (!fileSystem.TryGetValue(directoryPath, out entries))
            {
                DebugWrite(string.Format("Directory not found: {0}", directoryPath));
                return ProjFSNative.ERROR_FILE_NOT_FOUND;
            }

            int currentIndex;
            if (!enumerationIndices.TryGetValue(enumerationId, out currentIndex))
            {
                currentIndex = 0;
                enumerationIndices[enumerationId] = currentIndex;
            }

            if (callbackData.Flags == ProjFSNative.PrjCallbackDataFlags.RestartScan) {
                currentIndex = 0;
                enumerationIndices[enumerationId] = 0;
            } else if (callbackData.Flags == ProjFSNative.PrjCallbackDataFlags.ReturnSingleEntry) {
                single = true;
            }

            entries.Sort(delegate(FileEntry a, FileEntry b) { return ProjFSNative.PrjFileNameCompare(a.Name, b.Name); });

            for (; currentIndex < entries.Count; currentIndex++)
            {
                if (currentIndex >= entries.Count)
                {
                    DebugWrite(string.Format("Enumeration complete for session: {0}", enumerationId));
                    return ProjFSNative.S_OK;
                }

                var entry = entries[currentIndex];
                DebugWrite(string.Format("Processing entry: {0}", entry.Name));

                if (!ProjFSNative.PrjFileNameMatch(entry.Name, searchExpression)) // Skip if any don't match
                {
                    enumerationIndices[enumerationId] = currentIndex + 1;
                    continue;
                }

                ProjFSNative.PrjFileBasicInfo fileInfo = new ProjFSNative.PrjFileBasicInfo
                {
                    IsDirectory = entry.IsDirectory,
                    FileSize = entry.FileSize,
                    CreationTime = entry.LastWriteTime.ToFileTime(),
                    LastAccessTime = entry.LastWriteTime.ToFileTime(),
                    LastWriteTime = entry.LastWriteTime.ToFileTime(),
                    ChangeTime = entry.LastWriteTime.ToFileTime(),
                    FileAttributes = entry.IsDirectory ? FileAttributes.Directory : FileAttributes.Normal
                };

                int result = ProjFSNative.PrjFillDirEntryBuffer(entry.Name, ref fileInfo, dirEntryBufferHandle);
                if (result != ProjFSNative.S_OK)
                {
                    DebugWrite(string.Format("PrjFillDirEntryBuffer failed for {0}. Result: {1}", entry.Name, result));
                    return ProjFSNative.S_OK;
                }

                enumerationIndices[enumerationId] = currentIndex + 1;
                if (single)
                    return ProjFSNative.S_OK;
            }

            return ProjFSNative.S_OK;
        }

        private int GetPlaceholderInfo(ProjFSNative.PrjCallbackData callbackData)
        {

            string filePath = callbackData.FilePathName ?? "";
            DebugWrite(string.Format("GetPlaceholderInfo: {0}", filePath));

            if (string.IsNullOrEmpty(filePath))
            {
                return ProjFSNative.ERROR_FILE_NOT_FOUND;
            }

            string parentPath = Path.GetDirectoryName(filePath);
            string fileName = Path.GetFileName(filePath);

            if (string.IsNullOrEmpty(parentPath))
            {
                parentPath = "\\";
            }

            List<FileEntry> entries;
            if (!fileSystem.TryGetValue(parentPath, out entries))
            {
                DebugWrite(string.Format("Parent directory not found: {0}", parentPath));
                return ProjFSNative.ERROR_FILE_NOT_FOUND;
            }

            FileEntry entry = null;
            foreach (var e in entries)
            {
                if (string.Equals(e.Name, fileName, StringComparison.OrdinalIgnoreCase))
                {
                    entry = e;
                    break;
                }
            }

            if (entry == null)
            {
                DebugWrite(string.Format("File not found: {0}", filePath));
                return ProjFSNative.ERROR_FILE_NOT_FOUND;
            }

            entries.Sort(delegate(FileEntry a, FileEntry b) { return ProjFSNative.PrjFileNameCompare(a.Name, b.Name); });

            ProjFSNative.PrjPlaceholderInfo placeholderInfo = new ProjFSNative.PrjPlaceholderInfo
            {
                FileBasicInfo = new ProjFSNative.PrjFileBasicInfo
                {
                    IsDirectory = entry.IsDirectory,
                    FileSize = entry.FileSize,
                    CreationTime = entry.LastWriteTime.ToFileTime(),
                    LastAccessTime = entry.LastWriteTime.ToFileTime(),
                    LastWriteTime = entry.LastWriteTime.ToFileTime(),
                    ChangeTime = entry.LastWriteTime.ToFileTime(),
                    FileAttributes = entry.IsDirectory ? FileAttributes.Directory : FileAttributes.Normal
                }
            };

            int result = ProjFSNative.PrjWritePlaceholderInfo(
                callbackData.NamespaceVirtualizationContext,
                filePath,
                ref placeholderInfo,
                (uint)Marshal.SizeOf(placeholderInfo));

            if (result != ProjFSNative.S_OK)
            {
                DebugWrite(string.Format("PrjWritePlaceholderInfo failed for {0}. Result: {1}", filePath, result));
            }

            return result;
        }

        private int GetFileData(ProjFSNative.PrjCallbackData callbackData, ulong byteOffset, uint length)
        {
            string parentPath = Path.GetDirectoryName(callbackData.FilePathName);
            if (string.IsNullOrEmpty(parentPath))
            {
                parentPath = "\\";
            }
            string fileName = Path.GetFileName(callbackData.FilePathName);

            AlertOnFileAccess(callbackData.FilePathName, callbackData.TriggeringProcessImageFileName);

            List<FileEntry> entries;
            if (!fileSystem.TryGetValue(parentPath, out entries))
            {
                DebugWrite("File not found!");
                return 2; // ERROR_FILE_NOT_FOUND
            }

            var entry = entries.Find(e => string.Equals(e.Name, fileName, StringComparison.OrdinalIgnoreCase));
            if (entry == null || entry.IsDirectory)
            {
                DebugWrite("File is a dir?!");
                return 2; // ERROR_FILE_NOT_FOUND
            }

            entry.Opened = true;
            entry.LastAlert = GetUnixTimeStamp();

            byte[] bom = {0xEF, 0xBB, 0xBF}; // UTF-8 Byte order mark
            byte[] textBytes = Encoding.UTF8.GetBytes(string.Format("This is the content of {0}", fileName));
            byte[] fileContent = new byte[bom.Length + textBytes.Length];
            System.Buffer.BlockCopy(bom, 0, fileContent, 0, bom.Length);
            System.Buffer.BlockCopy(textBytes, 0, fileContent, bom.Length, textBytes.Length);

            if (byteOffset >= (ulong)fileContent.Length)
            {
                return 0;
            }

            uint bytesToWrite = Math.Min(length, (uint)(fileContent.Length - (int)byteOffset));
            IntPtr buffer = ProjFSNative.PrjAllocateAlignedBuffer(instanceHandle, bytesToWrite);
            try
            {
                Marshal.Copy(fileContent, (int)byteOffset, buffer, (int)bytesToWrite);
                return ProjFSNative.PrjWriteFileData(instanceHandle, ref callbackData.DataStreamId, buffer, byteOffset, bytesToWrite);
            }
            finally
            {
                ProjFSNative.PrjFreeAlignedBuffer(buffer);
            }
        }

        private void DebugWrite(string message)
        {
            if (enableDebug)
            {
                Console.WriteLine("[DEBUG] " + message);
            }
        }
    }

    class FileEntry
    {
        public string Name { get; set; }
        public bool IsDirectory { get; set; }
        public long FileSize { get; set; }
        public DateTime LastWriteTime { get; set; }
        public bool Opened { get; set; }
        public long LastAlert { get; set; }
    }

    static class ProjFSNative
    {
        public const int S_OK = 0;
        public const int ERROR_INSUFFICIENT_BUFFER = 122;
        public const int ERROR_FILE_NOT_FOUND = 2;

        [DllImport("ProjectedFSLib.dll")]
        public static extern IntPtr PrjAllocateAlignedBuffer(IntPtr namespaceVirtualizationContext, uint size);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern bool PrjDoesNameContainWildCards(string fileName);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern int PrjFileNameCompare(string fileName1, string fileName2);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern bool PrjFileNameMatch(string fileNameToCheck, string pattern);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern int PrjFillDirEntryBuffer(string fileName, ref PrjFileBasicInfo fileBasicInfo,
            IntPtr dirEntryBufferHandle);

        [DllImport("ProjectedFSLib.dll")]
        public static extern void PrjFreeAlignedBuffer(IntPtr buffer);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern int PrjMarkDirectoryAsPlaceholder(string rootPathName, string targetPathName,
            IntPtr versionInfo, ref Guid virtualizationInstanceID);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern int PrjStartVirtualizing(string virtualizationRootPath, ref PrjCallbacks callbacks,
            IntPtr instanceContext, IntPtr options, ref IntPtr namespaceVirtualizationContext);

        [DllImport("ProjectedFSLib.dll")]
        public static extern void PrjStopVirtualizing(IntPtr namespaceVirtualizationContext);

        [DllImport("ProjectedFSLib.dll")]
        public static extern int PrjDeleteFile(IntPtr namespaceVirtualizationContext, string destinationFileName, int updateFlags, ref int failureReason);

        [DllImport("ProjectedFSLib.dll")]
        public static extern int PrjWriteFileData(IntPtr namespaceVirtualizationContext, ref Guid dataStreamId,
            IntPtr buffer, ulong byteOffset, uint length);

        [DllImport("ProjectedFSLib.dll", CharSet = CharSet.Unicode)]
        public static extern int PrjWritePlaceholderInfo(IntPtr namespaceVirtualizationContext,
            string destinationFileName, ref PrjPlaceholderInfo placeholderInfo, uint placeholderInfoSize);

        // Structs and enums as provided
        [StructLayout(LayoutKind.Sequential)]
        public struct PrjFileEntry
        {
            public string Name;
            public PrjFileBasicInfo FileBasicInfo;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjCallbacks
        {
            public PrjStartDirectoryEnumerationCb StartDirectoryEnumerationCallback;
            public PrjEndDirectoryEnumerationCb EndDirectoryEnumerationCallback;
            public PrjGetDirectoryEnumerationCb GetDirectoryEnumerationCallback;
            public PrjGetPlaceholderInfoCb GetPlaceholderInfoCallback;
            public PrjGetFileDataCb GetFileDataCallback;
            public PrjQueryFileNameCb QueryFileNameCallback;
            public PrjNotificationCb NotificationCallback;
            public PrjCancelCommandCb CancelCommandCallback;
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct PrjCallbackData
        {
            public uint Size;
            public PrjCallbackDataFlags Flags;
            public IntPtr NamespaceVirtualizationContext;
            public int CommandId;
            public Guid FileId;
            public Guid DataStreamId;
            public string FilePathName;
            public IntPtr VersionInfo;
            public uint TriggeringProcessId;
            public string TriggeringProcessImageFileName;
            public IntPtr InstanceContext;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjFileBasicInfo
        {
            public bool IsDirectory;
            public long FileSize;
            public long CreationTime;
            public long LastAccessTime;
            public long LastWriteTime;
            public long ChangeTime;
            public FileAttributes FileAttributes;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjNotificationParameters
        {
            public PrjNotifyTypes PostCreateNotificationMask;
            public PrjNotifyTypes FileRenamedNotificationMask;
            public bool FileDeletedOnHandleCloseIsFileModified;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjPlaceholderInfo
        {
            public PrjFileBasicInfo FileBasicInfo;
            public uint EaBufferSize;
            public uint OffsetToFirstEa;
            public uint SecurityBufferSize;
            public uint OffsetToSecurityDescriptor;
            public uint StreamsInfoBufferSize;
            public uint OffsetToFirstStreamInfo;
            public PrjPlaceholderVersionInfo VersionInfo;
            [MarshalAs(UnmanagedType.ByValArray, SizeConst = 1)] public byte[] VariableData;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjStartVirutalizingOptions
        {
            public PrjStartVirutalizingFlags flags;
            public uint PoolThreadCount;
            public uint ConcurrentThreadCount;
            public PrjNotificationMapping NotificationMappings;
            public uint NotificationMappingCount;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjNotificationMapping
        {
            public PrjNotifyTypes NotificationBitMask;
            public string NotifcationRoot;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PrjPlaceholderVersionInfo
        {
            [MarshalAs(UnmanagedType.ByValArray, SizeConst = (int)PrjPlaceholderID.Length)] public byte[] ProviderID;
            [MarshalAs(UnmanagedType.ByValArray, SizeConst = (int)PrjPlaceholderID.Length)] public byte[] ContentID;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct EnumerationState
        {
            public string SessionID;
            public bool IsComplete;
            public int CurrentIndex;
        }

        [Flags]
        public enum PrjCallbackDataFlags : uint
        {
            RestartScan = 1,
            ReturnSingleEntry = 2
        }

        public enum PrjNotification : uint
        {
            FileOpened = 0x2,
            NewFileCreated = 0x4,
            FileOverwritten = 0x8,
            PreDelete = 0x10,
            PreRename = 0x20,
            PreSetHardlink = 0x40,
            FileRename = 0x80,
            HardlinkCreated = 0x100,
            FileHandleClosedNoModification = 0x200,
            FileHandleClosedFileModified = 0x400,
            FileHandleClosedFileDeleted = 0x800,
            FilePreConvertToFull = 0x1000
        }

        public enum PrjNotifyTypes : uint
        {
            None,
            SuppressNotifications,
            FileOpened,
            NewFileCreated,
            FileOverwritten,
            PreDelete,
            PreRename,
            PreSetHardlink,
            FileRenamed,
            HardlinkCreated,
            FileHandleClosedNoModification,
            FileHandleClosedFileModified,
            FileHandleClosedFileDeleted,
            FilePreConvertToFull,
            UseExistingMask
        }

        public enum PrjPlaceholderID : uint
        {
            Length = 128
        }

        public enum PrjStartVirutalizingFlags : uint
        {
            PrjFlagNone,
            PrjFlagUseNegativePathCache
        }

        public delegate int PrjCancelCommandCb(IntPtr callbackData);

        public delegate int PrjEndDirectoryEnumerationCb(PrjCallbackData callbackData, ref Guid enumerationId);

        [UnmanagedFunctionPointer(CallingConvention.StdCall, CharSet = CharSet.Unicode)]
        public delegate int PrjGetDirectoryEnumerationCb(PrjCallbackData callbackData, ref Guid enumerationId,
            string searchExpression, IntPtr dirEntryBufferHandle);

        public delegate int PrjGetFileDataCb(PrjCallbackData callbackData, ulong byteOffset, uint length);

        public delegate int PrjGetPlaceholderInfoCb(PrjCallbackData callbackData);

        [UnmanagedFunctionPointer(CallingConvention.StdCall, CharSet = CharSet.Unicode)]
        public delegate int PrjNotificationCb(PrjCallbackData callbackData, bool isDirectory, PrjNotification notification,
            string destinationFileName, ref PrjNotificationParameters operationParameters);

        public delegate int PrjStartDirectoryEnumerationCb(PrjCallbackData callbackData, ref Guid enumerationId);

        public delegate int PrjQueryFileNameCb(IntPtr callbackData);
    }
}
"@

    $filecsv = @"
{CSV_DATA}
"@

    try {
        # Check if the type is already loaded
        if (-not ([System.Management.Automation.PSTypeName]'ProjectedFileSystemProvider.Program').Type) {
            Add-Type -TypeDefinition $csharpCode -Language CSharp
        }

        # Create args array for Main method
        $args = @($RootPath, $filecsv, $alertDomain, $DebugMode.ToString())

        # Call the Main method
        [ProjectedFileSystemProvider.Program]::Main($args)
    }
    catch {
        Write-Error "Error in Invoke-CanaryFS: $_"
        throw
    }
}

Invoke-CanaryFS
'@

        #Append Root Path

        $processScript =  $processScript + " -RootPath $RootPath"
        # Save the process script (using the existing $processScript variable)
        $processScript | Out-File -FilePath $ScriptPath -Force

        # Create task XML
        $FullUsername = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        $taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
    <RegistrationInfo>
        <Description>$TaskDescription</Description>
    </RegistrationInfo>
    <Triggers>
        <LogonTrigger>
            <Enabled>true</Enabled>
            <UserId>$FullUsername</UserId>
        </LogonTrigger>
    </Triggers>
    <Principals>
        <Principal id="Author">
            <UserId>$FullUsername</UserId>
            <LogonType>InteractiveToken</LogonType>
            <RunLevel>LeastPrivilege</RunLevel>
        </Principal>
    </Principals>
    <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
        <AllowHardTerminate>true</AllowHardTerminate>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
            <StopOnIdleEnd>false</StopOnIdleEnd>
            <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
        <Priority>7</Priority>
    </Settings>
    <Actions Context="Author">
        <Exec>
            <Command>cmd.exe</Command>
            <Arguments>/c start /min powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File "$ScriptPath" -RootFolder "$RootPath" </Arguments>
        </Exec>
    </Actions>
</Task>
"@

        $xmlPath = "$env:TEMP\task.xml"
        $taskXml | Out-File -FilePath $xmlPath -Encoding Unicode

        $result = schtasks /create /tn $TaskName /xml $xmlPath /f

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Task '$TaskName' created successfully." -ForegroundColor Green
            Write-Host "Process script saved to: $ScriptPath" -ForegroundColor Green
            return $true
        } else {
            Write-Error "Failed to create task. Error code: $LASTEXITCODE"
            return $false
        }
    }
    catch {
        Write-Error "Error creating scheduled task: $_"
        return $false
    }
    finally {
        if (Test-Path $xmlPath) {
            Remove-Item $xmlPath -Force
        }
    }
}

# Main execution
if ((Read-Host "Preparing to Install Canary ProjFS. Do you want to continue? (Y/N)") -notmatch '^[Yy]$') { exit }

$projfsResult = Install-ProjFS

if ($projfsResult) {
    $taskResult = Create-ScheduledTask

    # Final results
    if ($taskResult) {
        Start-ScheduledTask -TaskName $TaskName

        Write-Host "`nParameter Values:" -ForegroundColor Cyan
        Write-Host "=================" -ForegroundColor Cyan

        # Print each parameter directly in green
        Write-Host "TaskName        : " -NoNewline
        Write-Host $TaskName -ForegroundColor Green

        Write-Host "ScriptPath      : " -NoNewline
        Write-Host $ScriptPath -ForegroundColor Green

        Write-Host "TaskDescription : " -NoNewline
        Write-Host $TaskDescription -ForegroundColor Green

        Write-Host "RootPath        : " -NoNewline
        Write-Host $RootPath -ForegroundColor Green

        Write-Host " IMPORTANT: Scheduled task has started and will launch on future logons" -ForegroundColor Yellow
    }
    else {
        Write-Host "`nScheduled task creation failed." -ForegroundColor Yellow
    }
}
else {
    Write-Host "`nOperation Failed." -ForegroundColor Yellow
}
"""

DUMMY_FOLDER_STRUCTURE = [
    {
        "name": "Projects",
        "type": "folder",
        "children": [
            {
                "name": "Project A",
                "type": "folder",
                "children": [
                    {"name": "Doc1.pdf", "type": "pdf"},
                    {"name": "Doc2.docx", "type": "docx"},
                    {"name": "Doc3.xls", "type": "xls"},
                    {"name": "Doc4.doc", "type": "doc"},
                ],
            },
            {
                "name": "Project B",
                "type": "folder",
                "children": [
                    {"name": "Doc A.pdf", "type": "pdf"},
                    {"name": "Doc B.docx", "type": "docx"},
                    {"name": "Doc C.xls", "type": "xls"},
                    {"name": "Doc D.doc", "type": "doc"},
                ],
            },
        ],
    },
    {
        "name": "Testing",
        "type": "folder",
        "children": [
            {"name": "Doc1.pdf", "type": "pdf"},
            {"name": "Doc2.xlsx", "type": "xls"},
            {"name": "Doc3.doc", "type": "doc"},
        ],
    },
    {
        "name": "Deployment",
        "type": "folder",
        "children": [
            {"name": "doc a.pdf", "type": "pdf"},
            {"name": "doc b.docx", "type": "docx"},
            {"name": "doc c.xls", "type": "xls"},
            {"name": "doc d.doc", "type": "doc"},
        ],
    },
    {
        "name": "Invoicing",
        "type": "folder",
        "children": [
            {"name": "Invoice A.pdf", "type": "pdf"},
            {"name": "Invoice B.xlsx", "type": "xls"},
            {"name": "Invoice C.docx", "type": "docx"},
            {"name": "Invoice D.doc", "type": "doc"},
        ],
    },
]


def _gen_ts() -> str:
    """
    Generates a random timestamp in the near past
    """
    now = floor(datetime.now().timestamp())
    random_hours = random.randint(1, 10000)
    return str(now - (random_hours * 60 * 60))


def _new_item(path: str, is_folder: bool, size: int = 0) -> dict:
    isdir = "false"
    if is_folder:
        isdir = "true"
    return {"path": path, "isdir": isdir, "size": size, "timestamp": _gen_ts()}


def _process_item(item: dict, path: str) -> str:
    out = []
    if item["type"] == "folder":
        out.append(_new_item(path=path + "\\" + item["name"], is_folder=True))
        for c in item["children"]:
            out += _process_item(c, path + "\\" + item["name"])
    else:
        out.append(
            _new_item(
                path=path + "\\" + item["name"],
                is_folder=False,
                size=random.randint(1024, 51200),
            )
        )
    return out


def _json_to_csv(fake_file_structure: list[dict]) -> str:
    """
    Converts a JSON-based dict of a file system structure to the CSV format used by the ProjFS provider
    """

    fieldnames = ["path", "isdir", "size", "timestamp"]
    out = []
    for item in fake_file_structure:
        out += _process_item(item, "")

    out_csv = StringIO()
    writer = DictWriter(out_csv, fieldnames=fieldnames)
    writer.writerows(out)
    return out_csv.getvalue().strip()


def make_windows_fake_fs(
    token_hostname: Hostname, root_dir: str, fake_file_structure: list[dict]
) -> str:
    """Returns a Powershell script file which has the steps to deploy a
    Windows Folder Token embedded in it.
    The token is in a 'hostname' eg: {some}.{thing}.CMD.{token}.{canarytoken_hostname}

    Args:
        token_hostname (Hostname): {token}.{canarytoken_server_hostname} eg: 1234dsaa.canarytokens.com
        root_dir (str): Path (e.g., 'C:\\vfs') where the folder should be created.
        fake_file_structure list[dict]: The fake file structure to use when the token is deployed.

    Returns:
        str: A valid powershell file that is to be loaded on a windows machine.
    """
    fs_csv = _json_to_csv(fake_file_structure)

    # .format does not work because of certain characters in the template
    # that cause and escape issue so we use replace
    return (
        PS_TEMPLATE.replace("{CSV_DATA}", fs_csv)
        .replace("{TOKEN_DOMAIN}", token_hostname)
        .replace("{ROOT_DIR}", root_dir)
    )
