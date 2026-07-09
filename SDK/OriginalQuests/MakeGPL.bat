@echo off
rem A batch file to compile the GPL source from Majesty and Majesty Expantion
rem The resulting byte code will be put in the local directories, Data and DataMX
rem When mking modifications to the original GPL source for a new Quest, 
rem do NOT copy the resulting .bcd files over the original files in the Majesty install
rem directory. Copy them into your quest's data directory and use the Quest
rem definition file (.mqxml) to load the modified .bcd files and to unload the orginal files.

rem Set to non-zero if some error occurred
set ERROR_OCCURRED=0

set GPLBCC=""
rem Is the compiler in the Quest's source directory?
if EXIST gplbcc.exe (
 set GPLBCC="%CD%\gplbcc.exe"
 goto foundCompiler
)

rem How about one up from where this file is?
if EXIST ..\gplbcc.exe (
 set GPLBCC="%CD%\..\gplbcc.exe"
 goto foundCompiler
)

rem Is the Majesty SDK installed?
if NOT "%MAJESTYSDK%"=="" (
 set GPLBCC="%MAJESTYSDK%\gplbcc.exe"
)

rem Check to make sure the compiler is available
if NOT EXIST %GPLBCC% goto missingCompiler

:foundCompiler

echo Using GPL compiler at %GPLBCC%

rem Original Majesty GPL
call :buildit GPL Path bytecode.bcd Data

rem Majesty Expansion GPL
call :buildit GPLMx Path_Data MX_Data.bcd DataMX
call :buildit GPLMx Path_Build MX_Build.bcd DataMX
call :buildit GPLMx Path_Task MX_Task.bcd DataMX
call :buildit GPLMx Path_Decision MX_Decision.bcd DataMX
call :buildit GPLMx Path_MajMisc MX_Compatibility.bcd DataMX

if %ERROR_OCCURRED%==1 (
 echo ERROR: One or more modules failed to compile.
)

goto :EOF

rem ************************************************
:buildit

pushd %1
if EXIST %3 del %3
echo Building %2.gplproj, output as %3
%GPLBCC% -in %2.gplproj -out %3 -stdout
popd

if NOT EXIST "%1\%3" goto buildFailed

if NOT EXIST "%4" mkdir "%4"

echo Copying  %1\%3 to %4
copy /y "%1\%3" "%4"
del "%1\%3"
goto :EOF

:buildFailed
echo ERROR: Compile failed.
set ERROR_OCCURRED=1

goto :EOF

rem ************************************************
:missingCompiler
echo ERROR: Unable to find the GPL compiler.  Set the MAJESTYSDK environment variable to point to the SDK path.
goto :EOF
