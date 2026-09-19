; Inno Setup 6 安装包脚本（Windows 上用 Inno Setup 打开本文件点 Compile 即可）
; 下载：https://jrsoftware.org/isdl.php （安装时选中文语言）
#define MyAppName "委托文件生成器"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "河北禄存律师事务所"

[Setup]
AppId={{8E2B4F1A-7C3D-4A5B-9E0F-委托文件生成器}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist-installer
OutputBaseFilename=委托文件生成器_安装包_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\委托文件生成器.exe

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "dist\委托文件生成器\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\委托文件生成器.exe"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\委托文件生成器.exe"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: unchecked

[Run]
Filename: "{app}\委托文件生成器.exe"; Description: "现在运行{#MyAppName}"; Flags: nowait postinstall skipifsilent
