@echo off
echo 🚀 Setting up GitHub repository for automatic deployment
echo.

REM Check if remote origin exists
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git remote 'origin' already exists
    for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
    echo Current remote URL: %REMOTE_URL%
    echo.
    set /p update_remote="Do you want to update the remote URL? (y/n): "
    if /i "%update_remote%"=="y" (
        set /p repo_url="Enter your GitHub repository URL: "
        git remote set-url origin %repo_url%
        echo ✅ Remote URL updated
    )
) else (
    set /p repo_url="Enter your GitHub repository URL: "
    git remote add origin %repo_url%
    echo ✅ Remote 'origin' added
)

echo.
echo 📤 Pushing code to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo 🎉 Success! Your code has been pushed to GitHub
    echo.
    echo 📋 Next steps:
    echo 1. Go to your GitHub repository
    echo 2. Navigate to Settings → Secrets and variables → Actions
    echo 3. Add the required secrets (see DEPLOYMENT_README.md)
    echo 4. Push more changes to trigger automatic deployment!
    echo.
    echo 📖 For detailed instructions, see: DEPLOYMENT_README.md
) else (
    echo.
    echo ❌ Push failed. This might be because:
    echo 1. The repository doesn't exist yet on GitHub
    echo 2. You don't have push permissions
    echo 3. The branch name is different (try 'master' instead of 'main')
    echo.
    echo 🔧 Troubleshooting:
    echo - Create the repository on GitHub first
    echo - Make sure you have push access
    echo - Check if the default branch is 'main' or 'master'
)

pause
