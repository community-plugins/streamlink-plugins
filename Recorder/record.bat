@ECHO OFF
SETLOCAL EnableDelayedExpansion

@REM Read the model list
SET n=0
FOR /F "tokens=*" %%A IN (model.txt) DO (
    SET /A n+=1
    SET "model!n!=%%A"
    ECHO !n! %%A
)

@REM Call download_single.bat to download
FOR /L %%i IN (1, 1, %n%) DO (
    FOR /F "tokens=3 delims=/" %%B IN ("!model%%i!") DO (
        SET "title=%%B"
    )
    START "!title!" CMD /C download_single.bat !model%%i!
)

ENDLOCAL