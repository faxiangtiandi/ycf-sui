@echo off
chcp 65001 >nul  & rem 解决中文乱码问题
cd /d "%~dp0"    & rem 切换到脚本所在目录

:: ====================== 1. 激活虚拟环境 ======================
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Info: Activated .venv virtual environment
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Info: Activated venv virtual environment
) else (
    echo Warning: No virtual environment found, using system Python
)

:: ====================== 2. 自动检测可用端口 ======================
:: 初始端口（你原来的8503）、最大尝试端口（可自行修改）
set "start_port=8503"
set "max_port=8510"
set "available_port="

:: 循环检测端口是否被占用
echo Info: Detecting available ports from %start_port% to %max_port%...
for /l %%p in (%start_port%,1,%max_port%) do (
    :: 检测端口%%p是否被占用（netstat + findstr）
    netstat -ano | findstr /r /c:":%%p " >nul
    if errorlevel 1 (
        set "available_port=%%p"
        goto :run_application  & rem 找到可用端口，跳转到运行逻辑
    )
)

:: 如果所有端口都被占用
echo Error: All ports from %start_port% to %max_port% are occupied!
echo Tip: Please close the program occupying the port, or modify the "max_port" in this script
pause
exit /b 1

:: ====================== 3. 运行Streamlit应用 ======================
:run_application
echo Info: Found available port: %available_port%
echo Info: Starting Streamlit app...
python -m streamlit run app.py --server.port=%available_port%

:: 暂停以便查看错误信息
pause