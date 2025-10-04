@echo off
REM MuseTalk Dependencies Installation Script for Windows
REM This script installs all required dependencies using uv pip install

echo 🚀 MuseTalk Dependencies Installation (Windows)
echo ==================================================

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ UV not found. Please install UV first:
    echo    winget install --id=astral-sh.uv -e
    echo    or download from https://astral.sh/uv/install/
    pause
    exit /b 1
)

echo ✅ UV found
echo.

REM Install main requirements
echo 🔧 Installing main requirements.txt...
uv pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install main requirements
    pause
    exit /b 1
)
echo ✅ Main requirements installed

REM Install API requirements
echo 🔧 Installing API requirements.txt...
uv pip install -r api/requirements.txt  
if errorlevel 1 (
    echo ❌ Failed to install API requirements
    pause
    exit /b 1
)
echo ✅ API requirements installed

REM Install current project
echo 🔧 Installing current project in editable mode...
uv pip install -e .
if errorlevel 1 (
    echo ❌ Failed to install current project
    pause
    exit /b 1
)
echo ✅ Project installed in editable mode

REM Install OpenMIM and MMlab packages
echo 🔧 Installing OpenMIM and MMlab packages...
uv pip install openmim
if errorlevel 1 (
    echo ❌ Failed to install OpenMIM
    pause
    exit /b 1
)
echo ✅ OpenMIM installed

REM Install MMlab packages using mim
echo 🔧 Installing MMlab packages...
mim install mmcv-full mmdet mmpose
if errorlevel 1 (
    echo ❌ Failed to install MMlab packages
    pause
    exit /b 1
)
echo ✅ MMlab packages installed

REM Install additional development dependencies
echo 🔧 Installing additional dependencies...
uv pip install aiohttp websockets pytest black
if errorlevel 1 (
    echo ❌ Failed to install additional dependencies
    pause
    exit /b 1
)
echo ✅ Additional dependencies installed

echo.
echo 🎉 All dependencies installed successfully!
echo.
echo 💡 You can now:
echo    • Run the API: python api/musetalk_native_api.py
echo    • Test streaming: python test_streaming_api.py  
echo    • Run realtime inference: python scripts/realtime_inference.py
echo.
echo 📦 Verifying key packages...
uv pip show torch numpy fastapi gradio transformers 2>nul

echo.
REM Download models
echo 📥 Downloading required models...
echo 🔧 Creating models directory...
if not exist "models" mkdir models

REM Download MuseTalk models
echo 📥 Downloading MuseTalk models...
if exist "download_weights.bat" (
    echo 🔧 Running download_weights.bat...
    call download_weights.bat
    if errorlevel 1 (
        echo ❌ Failed to download MuseTalk models
        echo 💡 You can run 'download_weights.bat' manually later
    ) else (
        echo ✅ MuseTalk models downloaded
    )
) else (
    echo ❌ download_weights.bat not found
    echo 💡 Please download models manually or check the repository
)

REM Download face detection and pose models
echo 📥 Downloading additional models...
python -c "
try:
    import gdown
    import os
    os.makedirs('models/face_detection', exist_ok=True)
    os.makedirs('models/dwpose', exist_ok=True)
    print('📥 Downloading face detection models...')
    gdown.download('https://drive.google.com/uc?id=1FWJOICz8tu5Q5z9A48OUWuFT5r6gI9VV', 'models/face_detection/s3fd.pth', quiet=False)
    print('📥 Downloading DWPose models...')
    gdown.download('https://drive.google.com/uc?id=1bqJEy6u2y0pP-L0IaosuDFy9w9cu_P-2', 'models/dwpose/dw-ll_ucoco_384.pth', quiet=False)
    print('✅ Additional models downloaded')
except Exception as e:
    print(f'❌ Failed to download some models: {e}')
    print('💡 You may need to download them manually')
"

echo.
echo 🏁 Installation completed!
pause