@echo off
REM MuseTalk GPU Benchmark - Windows Batch Script

echo ========================================
echo MuseTalk GPU Benchmark
echo ========================================
echo.

REM Check if audio directory exists
if not exist "test_assets\benchmark_audio" (
    echo Creating benchmark audio directory...
    mkdir test_assets\benchmark_audio
    echo.
    echo Please add MP3 files to test_assets\benchmark_audio
    echo Then run this script again.
    pause
    exit /b
)

REM Run benchmark
echo Running benchmark...
echo.
uv run python scripts\benchmark.py --audio-dir test_assets\benchmark_audio --output-dir results\benchmarks

echo.
echo Benchmark complete! Check results\benchmarks\ for output.
pause
