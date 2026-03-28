; ─────────────────────────────────────────────────────────────────────────────
; KALOYA PDF CRACKER v1.0 — PROFESSIONAL INSTALLER
; ─────────────────────────────────────────────────────────────────────────────

#define AppName      "Kaloya PDF Cracker"
#define AppVersion   "1.0.0"
#define AppPublisher "Haseeb Kaloya"
#define AppURL       "https://github.com/haseebkaloya/kaloya-pdf-cracker"
#define AppExeName   "KaloyaPDFCracker.exe"
#define SourceDir    "..\dist\KaloyaPDFCracker"

[Setup]
; App Identity
AppId                        = {{A7F3C1D2-9E4B-4F8A-B2C6-3D5E7F1A0B9C}
AppName                      = {#AppName}
AppVersion                   = {#AppVersion}
AppPublisher                 = {#AppPublisher}
AppPublisherURL               = {#AppURL}
AppSupportURL                = {#AppURL}/issues
AppUpdatesURL                = {#AppURL}
AppCopyright                 = Copyright (C) 2026 {#AppPublisher}

; Destination
DefaultDirName               = {autopf}\{#AppName}
DefaultGroupName             = {#AppName}
AllowNoIcons                 = yes
PrivilegesRequired           = admin

; Branding & Images (Fixes "Black Box" issue)
SetupIconFile                = ..\gui\logo.ico
WizardStyle                  = modern
WizardResizable              = no
WizardImageFile              = wizard_sidebar.bmp
WizardSmallImageFile         = wizard_header.bmp
WizardImageStretch           = no

; License/Disclaimer (Crucial: This shows the 2026 Disclaimer page)
LicenseFile                  = ..\DISCLAIMER.txt

; Output Folder
OutputDir                    = Output
OutputBaseFilename           = KaloyaPDFCracker_Setup_v{#AppVersion}
Compression                  = lzma2/ultra64
SolidCompression             = yes

; Minimum system requirements
MinVersion                   = 10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "launchafter"; Description: "&Launch {#AppName} after installation"; GroupDescription: "Post-installation:"; Flags: checkedonce

[Files]
; IMPORTANT: Copy all files from dist/ (No _internal folder as requested)
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";             Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";   Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent; Tasks: launchafter

[UninstallDelete]
; Clean up runtime files
Type: files;    Name: "{app}\hash.txt"
Type: files;    Name: "{app}\result.txt"
Type: files;    Name: "{app}\john\run\john.pot"
Type: files;    Name: "{app}\john\run\john.log"
Type: dirifempty; Name: "{app}"

[Code]
// ─── Upgrade detection & Silent uninstallation of old version ────────────────
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
    if (IsUpgrade()) then
      UnInstallOldVersion();
  end;
end;
