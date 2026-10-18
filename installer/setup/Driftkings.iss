; Build only through build_tools/build_installer.py. Payload is never conditional.
#if VER < EncodeVer(6, 7, 1)
  #error Inno Setup 6.7.1 or later is required
#endif
#ifndef InputDir
  #error Run build_tools/build_installer.py --artifacts <build> --compile
#endif
#include InputDir + "\metadata.generated.iss"

[Setup]
AppId=Driftkings.Modpack
AppName=Driftkings
AppVersion={#BuildVersion}
AppPublisher=DriftKingsMods
AppPublisherURL=https://github.com/dkruben/Driftkings_SettingsLab
DefaultDirName={sd}\Games\World_of_Tanks
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
UsePreviousSetupType=no
UsePreviousTasks=no
PrivilegesRequired=lowest
MinVersion=10.0
WizardStyle=modern
LicenseFile={#RepoRoot}\LICENCE
OutputDir={#InstallerOutput}
OutputBaseFilename=Driftkings-{#BuildVersion}-WoT-{#GameVersion}-Setup
UninstallFilesDir={app}\mods\configs\Driftkings\installer
UninstallDisplayName=Driftkings {#BuildVersion}
CloseApplications=no
RestartApplications=no
Compression=lzma2
SolidCompression=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "pt"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Dirs]
Name: "{app}\mods\configs\Driftkings\SixthSense"; Flags: uninsneveruninstall
Name: "{app}\mods\configs\Driftkings\images"; Flags: uninsneveruninstall

[CustomMessages]
en.Recommended=Recommended (author defaults)
en.Customized=Custom
en.WrongClient=Select the World of Tanks {#GameVersion} game folder (supported realms: {#SupportedRealmsText}).
en.CloseGame=Close World of Tanks before installing.
en.ProcessCheckFailed=Cannot verify whether World of Tanks is running. Installation stopped.
en.PreserveSettings=An existing profile was found. All existing JSON settings will be preserved.
//PT
pt.Recommended=Recomendado (predefinições do autor)
pt.Customized=Personalizado
pt.WrongClient=Seleciona a pasta do World of Tanks {#GameVersion} (realms suportados: {#SupportedRealmsText}).
pt.CloseGame=Fecha o World of Tanks antes de instalar.
pt.ProcessCheckFailed=Não foi possível verificar se o World of Tanks está aberto. Instalação interrompida.
pt.PreserveSettings=Foi encontrado um perfil existente. Todos os JSON de configuração serão preservados.

#include InputDir + "\branding.generated.iss"
#include InputDir + "\payload.generated.iss"
#include InputDir + "\previews.generated.iss"
#include InputDir + "\components.generated.iss"

[Code]
#include "wizard.iss"
