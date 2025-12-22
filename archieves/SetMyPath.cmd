@echo off
set dir=%*
setlocal EnableDelayedExpansion
for /f "delims=" %%i in ('dir /s /ad /o:d /b "%dir:"=%"') do set path=%%i;!path!
cmd