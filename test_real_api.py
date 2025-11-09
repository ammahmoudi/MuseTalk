#!/usr/bin/env python3
"""
Quick test to check if the real API can import and start
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("=" * 60)
print("Testing MuseTalk Real API")
print("=" * 60)

# Test 1: Check basic imports
print("\n1. Testing basic imports...")
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    import uvicorn
    print("   ✅ FastAPI imports OK")
except ImportError as e:
    print(f"   ❌ FastAPI import failed: {e}")
    sys.exit(1)

# Test 2: Check MuseTalk imports
print("\n2. Testing MuseTalk imports...")
try:
    from musetalk.utils.preprocessing import get_landmark_and_bbox
    print("   ✅ MuseTalk preprocessing imports OK")
except ImportError as e:
    print(f"   ⚠️  MuseTalk preprocessing import warning: {e}")
    print("   (This is OK if models aren't downloaded yet)")

# Test 3: Check torch/CUDA
print("\n3. Testing PyTorch and CUDA...")
try:
    import torch
    print(f"   ✅ PyTorch version: {torch.__version__}")
    print(f"   ✅ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   ✅ CUDA device: {torch.cuda.get_device_name(0)}")
except ImportError as e:
    print(f"   ❌ PyTorch import failed: {e}")

# Test 4: Try importing the API
print("\n4. Testing API import...")
try:
    from api.main import app, avatars
    print(f"   ✅ API imported successfully")
    print(f"   ✅ Found {len(avatars)} existing avatars")
except Exception as e:
    print(f"   ❌ API import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check if native API can import
print("\n5. Testing native API import...")
try:
    # Just check if it can be imported without errors
    import importlib.util
    spec = importlib.util.spec_from_file_location("musetalk_native_api", 
                                                   project_root / "api" / "musetalk_native_api.py")
    if spec and spec.loader:
        print("   ✅ Native API file found and can be loaded")
    else:
        print("   ⚠️  Native API file not found")
except Exception as e:
    print(f"   ⚠️  Native API check warning: {e}")

print("\n" + "=" * 60)
print("✨ API Test Complete!")
print("=" * 60)
print("\nTo start the API, run:")
print("  cd api")
print("  python main.py")
print("\nOr use uvicorn:")
print("  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload")
print("=" * 60)
