@echo off

SET PYTHON=C:\Python25\python.exe
SET APPNAME=Iamdoing
SET CAPBLS=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment
SET SRCDIR=src
SET TMPDIR=src.tmp
SET TMPEXTRAS=extras
SET VER=0.0.8
IF NOT EXIST %TMPDIR% mkdir %TMPDIR%
IF NOT EXIST %TMPDIR%\graphics mkdir %TMPDIR%\graphics

copy  %SRCDIR%\*.py  %TMPDIR%
copy  %SRCDIR%\graphics\*.png %TMPDIR%\graphics\
copy  %SRCDIR%\graphics\icon.svg %TMPDIR%\graphics\

%PYTHON% ensymble.py py2sis --verbose --version="%VER%" --icon="%TMPDIR%\graphics\icon.svg" --appname="%APPNAME%" --caps="%CAPBLS%" "%TMPDIR%" "%APPNAME%-%VER%.sis"
