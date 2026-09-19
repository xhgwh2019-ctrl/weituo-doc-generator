@echo off
chcp 65001 >nul
cd /d %~dp0
if exist "dist\委托文件生成器\委托文件生成器.exe" (
  start "" "dist\委托文件生成器\委托文件生成器.exe"
  exit /b 0
)
py app.py 2>nul
if errorlevel 1 (
  python app.py 2>nul
)
if errorlevel 1 (
  echo.
  echo 启动失败：未找到 Python，请先安装 Python 3.10+（官网 python.org，安装时勾选 Add python.exe to PATH）
  echo 然后双击 build_windows.bat 生成免安装版本。
  pause
)
