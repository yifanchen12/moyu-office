#define AppVersion "0.1.0"
#define SourceRoot ".."

[Setup]
AppId={{A8190831-0425-46D3-B39F-035E1BE86E62}
AppName=Moyu Office / 摸鱼事务所
AppVersion={#AppVersion}
AppPublisher=yifanchen12
AppPublisherURL=https://github.com/yifanchen12/moyu-office
AppSupportURL=https://github.com/yifanchen12/moyu-office/issues
DefaultDirName={localappdata}\Programs\MoyuOffice
DefaultGroupName=Moyu Office
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#SourceRoot}\release
OutputBaseFilename=MoyuOffice-Setup-{#AppVersion}-windows-x64
LicenseFile={#SourceRoot}\LICENSE
InfoBeforeFile={#SourceRoot}\packaging\installer-notice.txt
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\MoyuOffice.exe
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut / 创建桌面快捷方式"; Flags: unchecked

[Files]
Source: "{#SourceRoot}\dist\MoyuOffice\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Moyu Office"; Filename: "{app}\MoyuOffice.exe"
Name: "{group}\Moyu Office - Browser"; Filename: "{app}\MoyuOffice.exe"; Parameters: "--browser"
Name: "{group}\Stop Moyu Office Service"; Filename: "{app}\MoyuOffice.exe"; Parameters: "--stop"
Name: "{group}\Uninstall Moyu Office"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Moyu Office"; Filename: "{app}\MoyuOffice.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MoyuOffice.exe"; Description: "Launch Moyu Office / 启动摸鱼事务所"; Flags: nowait postinstall skipifsilent unchecked

[UninstallRun]
Filename: "{app}\MoyuOffice.exe"; Parameters: "--stop"; RunOnceId: "StopMoyuOfficeService"; Flags: runhidden waituntilterminated skipifdoesntexist
