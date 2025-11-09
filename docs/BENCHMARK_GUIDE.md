# MuseTalk GPU Benchmark System

Test and compare MuseTalk performance across different GPUs and systems.

## Quick Start

### 1. Prepare Test Audio Files

Place your MP3 test files in the benchmark directory:

```bash
mkdir -p test_assets/benchmark_audio
# Copy your MP3 files here
```

### 2. Run Benchmark

**Windows:**
```bash
run_benchmark.bat
```

**Linux/Mac:**
```bash
chmod +x run_benchmark.sh
./run_benchmark.sh
```

**Or directly:**
```bash
uv run python scripts/benchmark.py --audio-dir test_assets/benchmark_audio
```

## Advanced Usage

### Custom Avatar

Use a specific avatar video:

```bash
uv run python scripts/benchmark.py \
    --audio-dir test_assets/benchmark_audio \
    --avatar path/to/your/avatar.mp4 \
    --output-dir results/my_benchmark
```

### Options

- `--audio-dir`: Directory containing MP3 files (default: `test_assets/benchmark_audio`)
- `--output-dir`: Directory to save results (default: `results/benchmarks`)
- `--avatar`: Path to avatar video (optional, uses default if not provided)

## What Gets Measured

The benchmark captures:

### System Information
- CPU model, cores, RAM
- GPU name, driver version, memory
- CUDA version

### Performance Metrics
- **Model Load Time**: Time to load VAE, UNet, and Whisper models
- **Avatar Prep Time**: Time to process avatar video
- **Feature Extraction Time**: Time to extract audio features per file
- **Frame Generation Time**: Time to generate video frames
- **FPS**: Frames per second during generation
- **GPU Memory Usage**: Peak GPU memory allocation

### Results Format

Results are saved as JSON in `results/benchmarks/benchmark_TIMESTAMP.json`:

```json
{
  "system_info": {
    "device": "cuda",
    "cpu": { ... },
    "gpu": {
      "name": "NVIDIA GeForce RTX 4060",
      "cuda_version": "13.0"
    }
  },
  "model_metrics": {
    "model_load_time": 5.23,
    "gpu_memory_after_load": { ... }
  },
  "audio_results": [
    {
      "audio_file": "test1.mp3",
      "feature_extraction_time": 1.2,
      "generation_time": 8.5,
      "total_time": 9.7,
      "fps": 25.3,
      "gpu_memory_peak": { ... }
    }
  ]
}
```

## Comparing GPUs

To compare different GPUs:

1. Run benchmark on System A
2. Copy results JSON to a shared location
3. Run benchmark on System B
4. Compare the JSON files

### Key Metrics for Comparison

- **FPS**: Higher is better
- **Total Time**: Lower is better
- **GPU Memory**: Lower means you can run larger batches
- **Model Load Time**: One-time cost, lower is better

## Example Workflow

```bash
# GPU 1: RTX 4060
./run_benchmark.sh
# Results saved to results/benchmarks/benchmark_20250109_123456.json

# GPU 2: RTX 4090
./run_benchmark.sh
# Results saved to results/benchmarks/benchmark_20250109_124567.json

# Compare the two JSON files to see performance differences
```

## Tips

1. **Use identical audio files** across all tests for fair comparison
2. **Close other GPU-intensive applications** before benchmarking
3. **Run multiple times** and average results for accuracy
4. **Test with different audio lengths** (short, medium, long)

## Troubleshooting

### No MP3 files found
```
❌ No MP3 files found in test_assets/benchmark_audio
```
**Solution**: Add MP3 files to the benchmark_audio directory

### CUDA out of memory
**Solution**: Close other GPU applications or use a shorter audio file

### Import errors
**Solution**: Make sure all dependencies are installed:
```bash
uv pip install -r requirements.txt
```

## Output Example

```
============================================================
🚀 MuseTalk GPU Benchmark
============================================================

System Info:
  Device: cuda
  CPU: 2400.0 (8 cores)
  GPU: NVIDIA GeForce RTX 4060 Laptop GPU
  CUDA: 13.0
============================================================
🤖 Loading MuseTalk models...
✅ Models loaded in 5.23 seconds
🎭 Preparing avatar from assets/demo/yongen/yongen.mp4...
✅ Avatar prepared in 2.15 seconds

📁 Found 3 audio files

🎵 Processing: test1.mp3
   Extracting audio features...
   Generating video frames...
   ✅ Completed in 9.70s (25.30 fps)

============================================================
📊 BENCHMARK SUMMARY
============================================================

✅ Successful: 3/3

⏱️  Average Timings:
   Model Load: 5.23s
   Avatar Prep: 2.15s
   Feature Extraction: 1.20s
   Frame Generation: 8.50s
   Total per Audio: 9.70s

🎬 Performance:
   Average FPS: 25.30

💾 GPU Memory:
   Average Peak: 2048.50 MB
============================================================

💾 Results saved to: results/benchmarks/benchmark_20250109_123456.json
```
