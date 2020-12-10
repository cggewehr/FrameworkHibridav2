set HIBRIDA_NAME=hibrida
set HIBRIDA_PATH=/home/usr/cgewehr/Desktop/FrameworkHibrida
set PATH=%PATH%;%HIBRIDA_PATH%/scripts
doskey hibrida=(python /home/usr/cgewehr/Desktop/FrameworkHibrida\scripts\mainScript.py $*)
set HIBRIDA_CONFIG_FILE=%HIBRIDA_PATH%/data/config.json
set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_PATH%/src/software/AppComposer
set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_PATH%/src/software/PlatformComposer
