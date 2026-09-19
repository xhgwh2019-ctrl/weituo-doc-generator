@echo off
chcp 65001 >nul
cd /d %~dp0
where py >nul 2>nul && set PY=py || set PY=python
%PY% --version || (echo 未找到 Python，请先安装 https://www.python.org/downloads/ 并勾选 Add to PATH & pause & exit /b 1)
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt pyinstaller
%PY% -m PyInstaller --clean --noconfirm app.spec
echo.
echo 构建完成：dist\委托文件生成器\委托文件生成器.exe
echo 可直接把 dist\委托文件生成器 文件夹拷到其他电脑运行；要安装包继续用 Inno Setup 打开 installer.iss 编译。
pause
