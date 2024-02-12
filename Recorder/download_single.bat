@ECHO OFF

:DOWNLOAD_MODEL
@REM Download function, receives model link as parameter
streamlink %1 best
TIMEOUT /T 15
GOTO :DOWNLOAD_MODEL