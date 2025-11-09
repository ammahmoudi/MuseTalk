#!/bin/bash
# MuseTalk Dependencies Installation Script for Linux/Mac
# This script installs all required dependencies using uv pip install

set -e  # Exit on error

# Set longer timeout for downloads (5 minutes)
export UV_HTTP_TIMEOUT=300

echo "🚀 MuseTalk Dependencies Installation (Linux/Mac)"
echo "=================================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV found: $(uv --version)"
echo

# Check if requirements files exist
if [ ! -f "requirements.txt" ]; then
    echo "❌ Main requirements.txt not found"
    exit 1
fi

if [ ! -f "api/requirements.txt" ]; then
    echo "❌ API requirements.txt not found"
    exit 1
fi

echo "📋 Found requirements files:"
echo "   • Main: requirements.txt"
echo "   • API:  api/requirements.txt"
echo

# Install PyTorch with CUDA first
echo "🔥 Installing PyTorch with CUDA 13.0..."
if uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130; then
    echo "✅ PyTorch with CUDA installed"
else
    echo "❌ Failed to install PyTorch"
    exit 1
fi

# Install main requirements
echo "🔧 Installing main requirements.txt..."
if uv pip install -r requirements.txt; then
    echo "✅ Main requirements installed"
else
    echo "❌ Failed to install main requirements"
    exit 1
fi

# Install API requirements
echo "🔧 Installing API requirements.txt..."
if uv pip install -r api/requirements.txt; then
    echo "✅ API requirements installed"
else
    echo "❌ Failed to install API requirements"
    exit 1
fi

# Pre-install numpy and pandas to avoid timeout issues with OpenMIM
echo "🔧 Pre-installing numpy and pandas..."
if uv pip install numpy pandas; then
    echo "✅ numpy and pandas installed"
else
    echo "⚠️ Warning: Failed to pre-install numpy/pandas, continuing anyway..."
fi

# Install OpenMIM and MMlab packages
echo "🔧 Installing OpenMIM and MMlab packages..."
echo "⏱️ Using 5-minute timeout for large downloads..."
if uv pip install --no-cache-dir -U openmim; then
    echo "✅ OpenMIM installed"
    
    # Install MMlab packages using mim command directly
    echo "🔧 Installing mmengine..."
    if mim install mmengine; then
        echo "✅ mmengine installed"
    else
        echo "❌ Failed to install mmengine"
        exit 1
    fi
    
    echo "🔧 Installing MMlab packages..."
    if mim install "mmcv==2.0.1" "mmdet==3.1.0" "mmpose==1.1.0"; then
        echo "✅ MMlab packages installed"
    else
        echo "❌ Failed to install MMlab packages"
        exit 1
    fi
else
    echo "❌ Failed to install OpenMIM"
    exit 1
fi

# Install additional development dependencies
echo "🔧 Installing additional dependencies..."
if uv pip install aiohttp websockets pytest black; then
    echo "✅ Additional dependencies installed"
else
    echo "❌ Failed to install additional dependencies"
    exit 1
fi

echo
echo "🎉 All dependencies installed successfully!"
echo
echo "💡 You can now:"
echo "   • Run the API: python api/musetalk_native_api.py"
echo "   • Test streaming: python test_streaming_api.py"
echo "   • Run realtime inference: python scripts/realtime_inference.py"
echo

echo "📦 Verifying key packages..."
for package in torch numpy fastapi gradio transformers; do
    if uv pip show "$package" &>/dev/null; then
        version=$(uv pip show "$package" | grep "Version:" | cut -d' ' -f2)
        echo "   ✅ $package: $version"
    else
        echo "   ❌ $package: Not found"
    fi
done

echo
# Download models using official script
echo "📥 Downloading MuseTalk models..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/download_weights.sh" ]; then
    chmod +x "$SCRIPT_DIR/download_weights.sh"
    if "$SCRIPT_DIR/download_weights.sh"; then
        echo "✅ Models downloaded successfully!"
    else
        echo "⚠️ Some models may have failed to download. Check manually if needed."
    fi
else
    echo "⚠️ download_weights.sh not found in scripts folder. Please download models manually."
fi

echo
echo "🏁 Installation completed!"