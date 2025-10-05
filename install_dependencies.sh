#!/bin/bash
# MuseTalk Dependencies Installation Script
# This script installs all required dependencies using UV package manager

set -e  # Exit on any error

echo "🚀 MuseTalk Dependencies Installation"
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

# Install current project
echo "🔧 Installing current project in editable mode..."
if uv pip install -e .; then
    echo "✅ Project installed in editable mode"
else
    echo "❌ Failed to install current project"
    exit 1
fi

# Install OpenMIM and MMlab packages
echo "🔧 Installing OpenMIM and MMlab packages..."
if uv pip install openmim; then
    echo "✅ OpenMIM installed"
    
    # Install MMlab packages using mim
    echo "🔧 Installing MMlab packages..."
    if mim install mmcv-full mmdet mmpose; then
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
if [ -f "download_weights.sh" ]; then
    chmod +x download_weights.sh
    if ./download_weights.sh; then
        echo "✅ Models downloaded successfully!"
    else
        echo "⚠️ Some models may have failed to download. Check manually if needed."
    fi
else
    echo "⚠️ download_weights.sh not found. Please download models manually."
fi

echo
echo "🏁 Installation completed!"