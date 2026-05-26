@echo off
chcp 65001 >nul
setlocal

echo ==============================
echo   Movie Diary - 启动脚本
echo ==============================

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

:: 检查后端依赖
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 正在安装后端依赖...
    pip install -r "%~dp0requirements.txt"
    pip install fastapi uvicorn sqlalchemy httpx pydantic
)

:: 检查前端依赖
if not exist "%~dp0frontend\node_modules" (
    echo [提示] 正在安装前端依赖...
    cd /d "%~dp0frontend" && npm install
)

echo.
echo [1/2] 启动后端 (FastAPI)...
start "Backend" /D "%~dp0backend" cmd /k "python -m uvicorn main:app --reload --port 8000"

echo [2/2] 启动前端 (Vue)...
start "Frontend" /D "%~dp0frontend" cmd /k "npm run dev"

echo.
echo 启动完成！
echo 前端: http://localhost:5173
echo 后端: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
pause
