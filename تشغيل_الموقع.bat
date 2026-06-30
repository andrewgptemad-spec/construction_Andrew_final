@echo off
chcp 65001 > nul
title نظام إدارة تكاليف البناء

echo.
echo  =============================================
echo   نظام إدارة تكاليف البناء
echo  =============================================
echo.

cd /d "%~dp0"

python --version > nul 2>&1
if errorlevel 1 (
    echo  [خطأ] Python غير مثبت. يرجى تثبيته من: https://www.python.org
    pause
    exit /b
)

if not exist "venv\Scripts\activate.bat" (
    echo  اول مرة - جاري الاعداد، انتظر دقيقة...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install django pillow --quiet
    python manage.py migrate > nul 2>&1
    python manage.py seed_data > nul 2>&1
    echo  تم الاعداد بنجاح!
    echo.
) else (
    call venv\Scripts\activate.bat
)

echo  جاري فتح الموقع في المتصفح...
echo.

powershell -command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"

echo  =============================================
echo   الموقع يعمل - لا تغلق هذه النافذة
echo   http://127.0.0.1:8000
echo  =============================================
echo.
echo  لايقاف الموقع: اغلق هذه النافذة
echo.

python manage.py runserver 127.0.0.1:8000

pause
