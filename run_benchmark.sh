#!/bin/bash
# MuseTalk GPU Benchmark - Linux/Mac Script

echo "========================================"
echo "MuseTalk GPU Benchmark"
echo "========================================"
echo ""

# Check if audio directory exists
if [ ! -d "test_assets/benchmark_audio" ]; then
    echo "Creating benchmark audio directory..."
    mkdir -p test_assets/benchmark_audio
    echo ""
    echo "Please add MP3 files to test_assets/benchmark_audio"
    echo "Then run this script again."
    exit 1
fi

# Run benchmark
echo "Running benchmark..."
echo ""
uv run python scripts/benchmark.py --audio-dir test_assets/benchmark_audio --output-dir results/benchmarks

echo ""
echo "Benchmark complete! Check results/benchmarks/ for output."
