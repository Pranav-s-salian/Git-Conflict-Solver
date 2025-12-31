@echo off
echo ========================================
echo Installing Git Conflict Solver...
echo ========================================
echo.

pip install -e "%~dp0"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run "git-conflict-solver" from anywhere!
echo.
pause
