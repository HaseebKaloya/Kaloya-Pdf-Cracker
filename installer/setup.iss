; ─────────────────────────────────────────────────────────────────────────────
; KALOYA PDF CRACKER v1.0 — PROFESSIONAL INSTALLER SCRIPT
; Built with Inno Setup 6 | By Haseeb Kaloya
; ─────────────────────────────────────────────────────────────────────────────

#define AppName      "Kaloya PDF Cracker"
#define AppVersion   "1.0.0"
#define AppPublisher "Haseeb Kaloya"
#define AppURL       "https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker"
#define AppExeName   "KaloyaPDFCracker.exe"
#define SourceDir    "..\dist\KaloyaPDFCracker"

[Setup]
AppId                        = {{A7F3C1D2-9E4B-4F8A-B2C6-3D5E7F1A0B9C}
AppName                      = {#AppName}
AppVersion                   = {#AppVersion}
AppVerName                   = {#AppName} v{#AppVersion}
AppPublisher                 = {#AppPublisher}
AppPublisherURL               = {#AppURL}
AppSupportURL                = {#AppURL}/issues
AppUpdatesURL                = {#AppURL}/releases
AppCopyright                 = Copyright (C) 2026 {#AppPublisher}. All rights reserved.
VersionInfoVersion           = 1.0.0.0
VersionInfoCompany           = Haseeb Kaloya
VersionInfoDescription       = Kaloya PDF Cracker - PDF Password Recovery Tool
VersionInfoCopyright         = Copyright (C) 2026 Haseeb Kaloya
DefaultDirName               = {autopf}\{#AppName}
DefaultGroupName             = {#AppName}
AllowNoIcons                 = yes
PrivilegesRequired           = admin
PrivilegesRequiredOverridesAllowed = dialog
SetupIconFile                = ..\gui\logo.ico
UninstallDisplayIcon         = {app}\{#AppExeName}
UninstallDisplayName         = {#AppName} v{#AppVersion}
WizardStyle                  = modern
WizardImageFile              = wizard_sidebar.bmp
WizardSmallImageFile         = wizard_header.bmp
WizardImageStretch           = no
WizardImageAlphaFormat       = none
LicenseFile                  = ..\DISCLAIMER.txt
OutputDir                    = Output
OutputBaseFilename           = KaloyaPDFCracker_Setup_v{#AppVersion}
Compression                  = lzma2/ultra64
SolidCompression             = yes
InternalCompressLevel        = ultra64
MinVersion                   = 10.0
ArchitecturesAllowed         = x64compatible
ArchitecturesInstallIn64BitMode = x64compatible
DisableProgramGroupPage      = yes
DisableWelcomePage           = no
ShowLanguageDialog           = no
CloseApplications            = yes
RestartApplications          = no
SetupLogging                 = yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.WelcomeLabel1=Welcome to [name] Setup
english.WelcomeLabel2=This wizard will install [name/ver] on your computer.%n%n[name] is a high-performance PDF password recovery tool powered by John the Ripper — 100%% local, no internet, no telemetry.%n%nIMPORTANT: This tool requires Administrator access to function. Windows will automatically show a UAC prompt on each launch.%n%nClick Next to continue.
english.FinishedLabel=Installation of [name] v[ver] is complete!%n%nA UAC prompt will appear each time you launch the application — this is intentional and required for full functionality.%n%nTo pin to your Taskbar: right-click the shortcut and choose "Pin to taskbar".%n%nClick Finish to exit Setup.

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "startupicon"; Description: "Launch {#AppName} when Windows &starts"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "launchafter"; Description: "&Launch {#AppName} after installation finishes"; GroupDescription: "After install:"; Flags: checkedonce

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}"; Permissions: users-modify

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Launch Kaloya PDF Cracker (runs as Administrator)"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"; Comment: "Remove Kaloya PDF Cracker from this computer"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Launch Kaloya PDF Cracker (runs as Administrator)"; Tasks: desktopicon
Name: "{commonstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Tasks: startupicon

[Run]
; FIX: Removed "runasoriginaluser" — it conflicts with requireAdministrator manifest
;      causing an error dialog after install. Using shellexec instead which
;      correctly triggers UAC elevation via ShellExecuteEx.
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} v{#AppVersion} now"; Flags: nowait postinstall skipifsilent shellexec; Tasks: launchafter

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; Flags: runhidden; RunOnceId: "KillBeforeUninstall"

[UninstallDelete]
Type: files;      Name: "{app}\hash.txt"
Type: files;      Name: "{app}\result.txt"
Type: files;      Name: "{app}\john\run\john.pot"
Type: files;      Name: "{app}\john\run\john.log"
Type: files;      Name: "{app}\*.log"
Type: dirifempty; Name: "{app}"

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#AppVersion}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "{#AppPublisher}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#AppURL}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; ValueType: dword; ValueName: "EstimatedSize"; ValueData: "150000"; Flags: uninsdeletevalue

[Code]
// ─── Upgrade Detection & Silent Removal ──────────────────────────────────────
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := iResultCode
    else
      Result := 1;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssInstall) then begin
    if IsUpgrade() then
      UnInstallOldVersion();
  end;
end;

// ─── Pre-Install: Enforce 64-bit OS ──────────────────────────────────────────
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not Is64BitInstallMode() then begin
    MsgBox(
      'Kaloya PDF Cracker requires a 64-bit version of Windows 10 or later.' + #13#10 + 'Your system does not meet this requirement.',
      mbCriticalError, MB_OK
    );
    Result := False;
  end;
end;
