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
; ── App Identity ─────────────────────────────────────────────────────────────
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
VersionInfoDescription       = Kaloya PDF Cracker Installer
VersionInfoCopyright         = Copyright (C) 2026 Haseeb Kaloya

; ── Destination & Privileges ─────────────────────────────────────────────────
DefaultDirName               = {autopf}\{#AppName}
DefaultGroupName             = {#AppName}
AllowNoIcons                 = yes
PrivilegesRequired           = admin
PrivilegesRequiredOverridesAllowed = dialog

; ── Branding & Visual Style ───────────────────────────────────────────────────
SetupIconFile                = ..\gui\logo.ico
UninstallDisplayIcon         = {app}\{#AppExeName}
UninstallDisplayName         = {#AppName} v{#AppVersion}
WizardStyle                  = modern
WizardImageFile              = wizard_sidebar.bmp
WizardSmallImageFile         = wizard_header.bmp
WizardImageStretch           = no
WizardImageAlphaFormat       = none


; ── License/Disclaimer ───────────────────────────────────────────────────────
LicenseFile                  = ..\DISCLAIMER.txt

; ── Output Configuration ─────────────────────────────────────────────────────
OutputDir                    = Output
OutputBaseFilename           = KaloyaPDFCracker_Setup_v{#AppVersion}
Compression                  = lzma2/ultra64
SolidCompression             = yes
InternalCompressLevel        = ultra64

; ── System Requirements ───────────────────────────────────────────────────────
MinVersion                   = 10.0
ArchitecturesAllowed         = x64compatible
ArchitecturesInstallIn64BitMode = x64compatible

; ── Installer Behavior ───────────────────────────────────────────────────────
DisableProgramGroupPage      = yes
DisableWelcomePage           = no
ShowLanguageDialog           = no
CloseApplications            = yes
RestartApplications          = no
SetupLogging                 = yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.WelcomeLabel1=Welcome to the [name] Setup Wizard
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nKaloya PDF Cracker is a high-performance PDF password recovery tool powered locally by John the Ripper. No cloud. No telemetry. Pure local processing power.%n%nClick Next to continue.
english.FinishedLabel=Setup has finished installing [name] on your computer.%n%nThe application runs with Administrator privileges automatically — no right-click required.%n%nClick Finish to exit Setup.

[Tasks]
Name: "desktopicon";   Description: "Create a &Desktop shortcut";          GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "quicklaunch";   Description: "Pin to &Taskbar (Windows 10/11)";     GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "launchafter";   Description: "&Launch {#AppName} after installation"; GroupDescription: "Post-install:"; Flags: checkedonce

[Files]
; Main application bundle (all files from dist, including john/ binaries)
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Ensure write access so john.pot / result.txt can be created at runtime
Name: "{app}"; Permissions: users-modify

[Icons]
; Start Menu
Name: "{group}\{#AppName}";             Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Launch Kaloya PDF Cracker"
Name: "{group}\Uninstall {#AppName}";   Filename: "{uninstallexe}"; Comment: "Remove Kaloya PDF Cracker"
; Desktop shortcut (optional task)
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon; Comment: "Launch Kaloya PDF Cracker"

[Run]
; Launch after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} v{#AppVersion}"; \
  Flags: nowait postinstall skipifsilent runasoriginaluser; Tasks: launchafter

[UninstallRun]
; Kill any running instances before uninstall
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; Flags: runhidden; RunOnceId: "KillApp"

[UninstallDelete]
; Clean up runtime-generated files
Type: files;       Name: "{app}\hash.txt"
Type: files;       Name: "{app}\result.txt"
Type: files;       Name: "{app}\john\run\john.pot"
Type: files;       Name: "{app}\john\run\john.log"
Type: files;       Name: "{app}\*.log"
Type: dirifempty;  Name: "{app}"

[Registry]
; Register app in "Apps & Features" with extra metadata
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; \
  ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#AppVersion}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; \
  ValueType: string; ValueName: "Publisher"; ValueData: "{#AppPublisher}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting('AppId')}_is1"; \
  ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#AppURL}"; Flags: uninsdeletevalue

[Code]
// ─── Upgrade Detection & Silent Removal of Old Version ──────────────────────
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

// ─── Pre-Install: Warn if running on 32-bit OS ───────────────────────────────
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not Is64BitInstallMode() then begin
    MsgBox(
      'Kaloya PDF Cracker requires a 64-bit version of Windows 10 or later.' + #13#10 +
      'Your system does not meet this requirement.',
      mbCriticalError, MB_OK
    );
    Result := False;
  end;
end;
