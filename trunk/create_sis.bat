@echo off

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Iamdoing
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET TMPDIR=src.tmp
SET VER=0.0.1
IF NOT EXIST %TMPDIR% mkdir %TMPDIR%

copy  %SRCDIR%\*.py  %TMPDIR%

%PYTHON% ensymble.py py2sis --verbose --version="%VER%" --appname="%APPNAME%" --caps="%CAPBLS%" "%TMPDIR%" "%APPNAME%-%VER%.sis"
