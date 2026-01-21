@echo off
:: 切换到项目根目录（替换成你的项目实际路径）
cd /d F:\ycf-sui

:: 激活虚拟环境（如果用了虚拟环境，没有的话可以删除这一行）
call .venv\Scripts\activate.bat

:: 运行Streamlit项目
streamlit run app.py

:: 防止窗口运行后自动关闭（可选）
pause