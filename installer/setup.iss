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
AppPublisherURL              = {#AppURL}
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
PrivilegesRequired           = lowest
PrivilegesRequiredOverridesAllowed = commandline dialog
SetupIconFile                = ..\gui\logo.ico
UninstallDisplayIcon         = {app}\{#AppExeName}
UninstallDisplayName         = {#AppName} v{#AppVersion}
WizardStyle                  = modern dark
WizardImageFile              = wizard_sidebar.bmp
WizardSmallImageFile         = wizard_header.bmp
WizardImageStretch           = yes
WizardImageBackColor         = #080C0E
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
english.WelcomeLabel2=This wizard will install [name/ver] on your computer.%n%nDeveloped by Haseeb Kaloya (Lead Developer)%nGitHub: https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker%n%n[name] is a high-performance PDF password recovery tool powered by John the Ripper — 100%% local, no internet, no telemetry.%n%nClick Next to continue.
english.FinishedLabel=Installation of [name] v[ver] is complete!%n%nDeveloped by Haseeb Kaloya.%nGitHub: https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker%n%nTo pin to your Taskbar: right-click the shortcut and choose "Pin to taskbar".%n%nClick Finish to exit Setup.

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "startupicon"; Description: "Launch {#AppName} when Windows &starts"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}"; Permissions: users-modify

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Launch Kaloya PDF Cracker"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"; Comment: "Remove Kaloya PDF Cracker from this computer"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Launch Kaloya PDF Cracker"; Tasks: desktopicon
Name: "{commonstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} v{#AppVersion} now"; Flags: nowait postinstall skipifsilent shellexec

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; Flags: runhidden; RunOnceId: "KillAppBeforeUninstall"
Filename: "taskkill.exe"; Parameters: "/F /IM john.exe"; Flags: runhidden; RunOnceId: "KillJohnBeforeUninstall"

[UninstallDelete]
Type: files;      Name: "{app}\hash.txt"
Type: files;      Name: "{app}\john\run\john.log"
Type: files;      Name: "{app}\*.log"
Type: dirifempty; Name: "{app}\john\run"
Type: dirifempty; Name: "{app}\john"
Type: dirifempty; Name: "{app}"

[Code]
// ─── Clickable Developer Links & Verification ───────────────────────────────
procedure OpenUrl(Url: String);
var
  ErrorCode: Integer;
begin
  ShellExec('open', Url, '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

procedure GitHubLinkClick(Sender: TObject);
begin
  OpenUrl('https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker');
end;

procedure InitializeWizard();
var
  DevLabel: TLabel;
  GitHubLink: TLabel;
begin
  // Developer Credit & Clickable GitHub link on the Finished Page
  DevLabel := TLabel.Create(WizardForm);
  DevLabel.Parent := WizardForm.FinishedPage;
  DevLabel.Caption := 'Lead Developer: Haseeb Kaloya';
  DevLabel.Left := WizardForm.RunList.Left;
  DevLabel.Top := WizardForm.RunList.Top + WizardForm.RunList.Height + 14;
  DevLabel.Font.Style := [fsBold];

  GitHubLink := TLabel.Create(WizardForm);
  GitHubLink.Parent := WizardForm.FinishedPage;
  GitHubLink.Caption := 'Visit Project GitHub: HaseebKaloya/Kaloya-Pdf-Cracker';
  GitHubLink.Left := WizardForm.RunList.Left;
  GitHubLink.Top := DevLabel.Top + 18;
  GitHubLink.Cursor := crHand;
  GitHubLink.Font.Color := $0041FF00;
  GitHubLink.Font.Style := [fsUnderline];
  GitHubLink.OnClick := @GitHubLinkClick;
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
