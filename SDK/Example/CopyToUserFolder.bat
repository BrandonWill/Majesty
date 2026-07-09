set DESTROOT=%HOMEDRIVE%%HOMEPATH%\Documents\My Games\MajestyHD\Quests
set DEST=%DESTROOT%\SDK\Example

mkdir "%DEST%"
mkdir "%DEST%\Quests"
mkdir "%DEST%\Data"
mkdir "%DEST%\GPL"

xcopy /d /y *.mqxml "%DEST%"
xcopy /d /y MakeGPL.bat "%DEST%"
xcopy /d /y Quests\*.* "%DEST%\Quests"
xcopy /d /y Data\*.* "%DEST%\Data"
xcopy /d /y GPL\*.* "%DEST%\GPL"



