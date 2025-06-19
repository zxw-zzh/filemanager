@echo off
REM Windows自启动脚本
cd /d %~dp0

REM 如果有虚拟环境则激活
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python app.py
pause 