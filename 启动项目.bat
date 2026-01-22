@echo off
cd /d "%~dp0"  # 切换到脚本所在目录

:: 检查是否存在虚拟环境，如果存在则激活它
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Warning: No virtual environment found, using system Python
)

:: 运行Streamlit应用
python -m streamlit run app.py --server.port 8503

:: 如果出错，暂停以便查看错误信息
if %errorlevel% neq 0 (
    pause
)