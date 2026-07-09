set DESTROOT=%HOMEDRIVE%%HOMEPATH%\Documents\My Games\MajestyHD\Mods
set DEST=%DESTROOT%\SDK\Adjust Guardhouse Mod

mkdir "%DEST%"
mkdir "%DEST%\Data"
mkdir "%DEST%\GPL"

xcopy /d /y *.mmxml "%DEST%"
xcopy /d /y MakeGPL.bat "%DEST%"
xcopy /d /y Data\*.* "%DEST%\Data"
xcopy /d /y GPL\*.* "%DEST%\GPL"
xcopy /d /y *.txt "%DEST%"



