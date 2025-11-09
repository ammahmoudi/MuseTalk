#!/usr/bin/env python
"""
GPU Benchmarking Script for MuseTalk
Tests audio-to-video generation performance across different GPUs using the API as a black box
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
import psutil
import GPUtil

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available - GPU info will be limited")


class MuseTalkBenchmark:
    def __init__(self, audio_dir: str, output_dir: str, avatar_id: str = None, api_url: str = "http://localhost:8000"):
        """
        Initialize benchmark system
        
        Args:
            audio_dir: Directory containing MP3 files to test
            output_dir: Directory to save benchmark results and generated videos
            avatar_id: Avatar ID to use (optional, will use default avatar if not provided)
            api_url: Base URL of the MuseTalk API
        """
        self.audio_dir = Path(audio_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.avatar_id = avatar_id
        self.api_url = api_url.rstrip('/')
        self.results = []
        
        # System info
        self.system_info = self._get_system_info()
        
    def _get_system_info(self):
        """Collect system information"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "model": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            }
        }
        
        # GPU info
        if TORCH_AVAILABLE and torch.cuda.is_available():
            info["device"] = "cuda"
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info["gpu"] = {
                        "name": gpu.name,
                        "driver": gpu.driver,
                        "memory_total_mb": gpu.memoryTotal,
                        "cuda_version": torch.version.cuda
                    }
                else:
                    info["gpu"] = {
                        "name": torch.cuda.get_device_name(0),
                        "memory_total_mb": torch.cuda.get_device_properties(0).total_memory / (1024**2),
                        "cuda_version": torch.version.cuda
                    }
            except:
                info["gpu"] = {
                    "name": torch.cuda.get_device_name(0),
                    "cuda_version": torch.version.cuda
                }
        else:
            info["device"] = "cpu"
            info["gpu"] = None
        
        return info
    
    def _get_or_create_avatar(self):
        """Get default avatar or use provided avatar_id"""
        if self.avatar_id:
            # Check if avatar exists
            response = requests.get(f"{self.api_url}/avatars")
            if response.status_code == 200:
                avatars = response.json()
                if any(a['avatar_id'] == self.avatar_id for a in avatars):
                    print(f"✅ Using avatar: {self.avatar_id}")
                    return self.avatar_id
                else:
                    raise ValueError(f"Avatar {self.avatar_id} not found")
            else:
                raise Exception(f"Failed to fetch avatars: {response.text}")
        else:
            # Check if we have any ready avatars
            response = requests.get(f"{self.api_url}/avatars")
            if response.status_code == 200:
                avatars = response.json()
                ready_avatars = [a for a in avatars if a['status'] == 'ready']
                if ready_avatars:
                    self.avatar_id = ready_avatars[0]['avatar_id']
                    print(f"✅ Using default avatar: {self.avatar_id}")
                    return self.avatar_id
            
            # No avatars available - need to create one
            print("⚠️ No avatars available. Please create an avatar first using:")
            print(f"   POST {self.api_url}/avatar/upload")
            raise Exception("No avatars available")
    
    def process_audio(self, audio_path: Path):
        """Process single audio file by calling the API"""
        print(f"\n🎵 Processing: {audio_path.name}")
        
        result = {
            "audio_file": audio_path.name,
            "audio_path": str(audio_path),
            "success": False
        }
        
        try:
            # Submit generation request
            print("   Submitting to API...")
            submit_start = time.time()
            
            with open(audio_path, 'rb') as f:
                files = {'audio': (audio_path.name, f, 'audio/mpeg')}
                data = {
                    'use_realtime': 'true',
                    'fps': '25',
                    'batch_size': '20'
                }
                
                response = requests.post(
                    f"{self.api_url}/avatar/{self.avatar_id}/generate",
                    files=files,
                    data=data
                )
            
            if response.status_code != 200:
                raise Exception(f"API returned {response.status_code}: {response.text}")
            
            task_info = response.json()
            task_id = task_info['task_id']
            submit_time = time.time() - submit_start
            
            result["task_id"] = task_id
            result["submit_time"] = submit_time
            
            # Poll for completion
            print(f"   Task ID: {task_id}")
            print("   Waiting for completion...")
            
            poll_start = time.time()
            max_wait = 600  # 10 minutes timeout
            poll_interval = 2  # Check every 2 seconds
            
            while True:
                elapsed = time.time() - poll_start
                if elapsed > max_wait:
                    raise Exception(f"Timeout waiting for task completion (>{max_wait}s)")
                
                # Check task status
                status_response = requests.get(f"{self.api_url}/task/{task_id}")
                if status_response.status_code != 200:
                    raise Exception(f"Failed to get task status: {status_response.text}")
                
                status_data = status_response.json()
                status = status_data['status']
                
                if status == 'completed':
                    total_time = time.time() - submit_start
                    result["generation_time"] = status_data.get('total_time_seconds', 0)
                    result["total_time"] = total_time
                    result["task_status"] = status_data
                    result["success"] = True
                    
                    # Download the result
                    output_file = self.output_dir / f"{audio_path.stem}_output.mp4"
                    download_response = requests.get(f"{self.api_url}/task/{task_id}/download")
                    if download_response.status_code == 200:
                        with open(output_file, 'wb') as f:
                            f.write(download_response.content)
                        result["output_file"] = str(output_file)
                        print(f"   ✅ Completed in {total_time:.2f}s (generation: {result['generation_time']:.2f}s)")
                    else:
                        print(f"   ⚠️ Completed but failed to download result")
                    
                    break
                    
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    raise Exception(f"Task failed: {error}")
                
                # Still processing, wait and retry
                time.sleep(poll_interval)
            
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    def run_benchmark(self):
        """Run full benchmark on all audio files"""
        print("=" * 60)
        print("🚀 MuseTalk GPU Benchmark (API Mode)")
        print("=" * 60)
        print(f"\nSystem Info:")
        print(f"  Device: {self.system_info['device']}")
        print(f"  CPU: {self.system_info['cpu']['model']} ({self.system_info['cpu']['cores']} cores)")
        if self.system_info.get('gpu'):
            print(f"  GPU: {self.system_info['gpu']['name']}")
            print(f"  CUDA: {self.system_info['gpu'].get('cuda_version', 'N/A')}")
        print(f"\nAPI URL: {self.api_url}")
        print("=" * 60)
        
        # Get or create avatar
        try:
            self._get_or_create_avatar()
        except Exception as e:
            print(f"\n❌ Avatar setup failed: {e}")
            return
        
        # Get all MP3 files
        audio_files = sorted(self.audio_dir.glob("*.mp3"))
        
        if not audio_files:
            print(f"\n❌ No MP3 files found in {self.audio_dir}")
            return
        
        print(f"\n📁 Found {len(audio_files)} audio files")
        
        # Process each audio file
        for audio_path in audio_files:
            result = self.process_audio(audio_path)
            self.results.append(result)
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        self._save_results()
    
    def _generate_summary(self):
        """Generate and print benchmark summary"""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        print(f"\n✅ Successful: {len(successful)}/{len(self.results)}")
        if failed:
            print(f"❌ Failed: {len(failed)}/{len(self.results)}")
            for r in failed:
                print(f"   • {r['audio_file']}: {r.get('error', 'Unknown error')}")
        
        if successful:
            avg_total = sum(r['total_time'] for r in successful) / len(successful)
            avg_gen = sum(r['generation_time'] for r in successful) / len(successful)
            
            print(f"\n⏱️  Average Timings:")
            print(f"   Total per Audio: {avg_total:.2f}s")
            print(f"   Generation Time: {avg_gen:.2f}s")
            print(f"   API Overhead: {avg_total - avg_gen:.2f}s")
        
        print("=" * 60)
    
    def _save_results(self):
        """Save benchmark results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"benchmark_{timestamp}.json"
        
        report = {
            "system_info": self.system_info,
            "api_url": self.api_url,
            "avatar_id": self.avatar_id,
            "audio_results": self.results,
            "summary": {
                "total_tests": len(self.results),
                "successful": len([r for r in self.results if r['success']]),
                "failed": len([r for r in self.results if not r['success']])
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="MuseTalk GPU Benchmark Tool (API Mode)")
    parser.add_argument(
        "--audio-dir",
        type=str,
        default="test_assets/benchmark_audio",
        help="Directory containing MP3 files (default: test_assets/benchmark_audio)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/benchmarks",
        help="Directory to save results (default: results/benchmarks)"
    )
    parser.add_argument(
        "--avatar-id",
        type=str,
        default=None,
        help="Avatar ID to use (optional, uses default avatar if not provided)"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the MuseTalk API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    # Create benchmark instance
    benchmark = MuseTalkBenchmark(
        audio_dir=args.audio_dir,
        output_dir=args.output_dir,
        avatar_id=args.avatar_id,
        api_url=args.api_url
    )
    
    # Run benchmark
    benchmark.run_benchmark()


if __name__ == "__main__":
    main()

    def __init__(self, audio_dir: str, output_dir: str, avatar_path: str = None):
        """
        Initialize benchmark system
        
        Args:
            audio_dir: Directory containing MP3 files to test
            output_dir: Directory to save benchmark results
            avatar_path: Path to avatar video (optional, uses default if not provided)
        """
        self.audio_dir = Path(audio_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default avatar path
        if avatar_path:
            self.avatar_path = Path(avatar_path)
        else:
            self.avatar_path = Path("assets/demo/yongen/yongen.mp4")
        
        self.results = []
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # System info
        self.system_info = self._get_system_info()
        
    def _get_system_info(self):
        """Collect system information"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "device": self.device,
            "cpu": {
                "model": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            }
        }
        
        if self.device == "cuda":
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info["gpu"] = {
                        "name": gpu.name,
                        "driver": gpu.driver,
                        "memory_total_mb": gpu.memoryTotal,
                        "cuda_version": torch.version.cuda
                    }
                else:
                    info["gpu"] = {
                        "name": torch.cuda.get_device_name(0),
                        "memory_total_mb": torch.cuda.get_device_properties(0).total_memory / (1024**2),
                        "cuda_version": torch.version.cuda
                    }
            except:
                info["gpu"] = {
                    "name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Unknown",
                    "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A"
                }
        
        return info
    
    def _get_gpu_memory(self):
        """Get current GPU memory usage"""
        if self.device == "cuda":
            return {
                "allocated_mb": round(torch.cuda.memory_allocated() / (1024**2), 2),
                "reserved_mb": round(torch.cuda.memory_reserved() / (1024**2), 2)
            }
        return None
    
    def load_models(self):
        """Load MuseTalk models"""
        print("🤖 Loading MuseTalk models...")
        start_time = time.time()
        
        self.vae, self.unet, self.pe = load_all_model(device=self.device)
        self.audio_processor = Audio2Feature(model_path="models/whisper/tiny.pt", device=self.device)
        
        load_time = time.time() - start_time
        print(f"✅ Models loaded in {load_time:.2f} seconds")
        
        return {
            "model_load_time": load_time,
            "gpu_memory_after_load": self._get_gpu_memory()
        }
    
    def prepare_avatar(self):
        """Prepare avatar video"""
        print(f"🎭 Preparing avatar from {self.avatar_path}...")
        start_time = time.time()
        
        # Read and process avatar
        input_img_list = read_imgs(str(self.avatar_path))
        coord_list, frame_list = get_landmark_and_bbox(input_img_list, bbox_shift=0)
        
        # Get VAE latents
        input_latent_list = []
        for frame in frame_list:
            latents = self.vae.get_latents_for_unet(frame)
            input_latent_list.append(latents)
        
        prep_time = time.time() - start_time
        print(f"✅ Avatar prepared in {prep_time:.2f} seconds")
        
        self.coord_list = coord_list
        self.frame_list = frame_list
        self.input_latent_list = input_latent_list
        
        return {
            "avatar_prep_time": prep_time,
            "num_frames": len(frame_list),
            "gpu_memory_after_prep": self._get_gpu_memory()
        }
    
    def process_audio(self, audio_path: Path):
        """Process single audio file and generate video"""
        print(f"\n🎵 Processing: {audio_path.name}")
        
        result = {
            "audio_file": audio_path.name,
            "audio_path": str(audio_path),
            "success": False
        }
        
        try:
            # Extract audio features
            print("   Extracting audio features...")
            feature_start = time.time()
            whisper_chunks = self.audio_processor.audio2feat(str(audio_path))
            feature_time = time.time() - feature_start
            
            result["feature_extraction_time"] = feature_time
            result["num_audio_chunks"] = len(whisper_chunks)
            
            # Generate video frames
            print("   Generating video frames...")
            gen_start = time.time()
            
            gen = datagen(
                whisper_chunks,
                self.input_latent_list,
                self.coord_list,
                self.frame_list
            )
            
            output_frames = []
            frame_count = 0
            
            for audio_frame, latent_frame, coord_frame, source_frame in gen:
                # Generate frame using UNet
                pred_latents = self.unet.model(
                    latent_frame,
                    timesteps=0,
                    context=audio_frame
                )
                
                # Decode latents
                recon = self.vae.decode_latents(pred_latents)
                
                # Blend with original
                frame = get_image(source_frame, recon, coord_frame)
                output_frames.append(frame)
                frame_count += 1
            
            gen_time = time.time() - gen_start
            
            result["generation_time"] = gen_time
            result["num_frames_generated"] = frame_count
            result["fps"] = frame_count / gen_time if gen_time > 0 else 0
            result["gpu_memory_peak"] = self._get_gpu_memory()
            result["success"] = True
            
            # Calculate total time
            total_time = feature_time + gen_time
            result["total_time"] = total_time
            
            print(f"   ✅ Completed in {total_time:.2f}s ({result['fps']:.2f} fps)")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    def run_benchmark(self):
        """Run full benchmark on all audio files"""
        print("=" * 60)
        print("🚀 MuseTalk GPU Benchmark")
        print("=" * 60)
        print(f"\nSystem Info:")
        print(f"  Device: {self.system_info['device']}")
        print(f"  CPU: {self.system_info['cpu']['model']} ({self.system_info['cpu']['cores']} cores)")
        if 'gpu' in self.system_info:
            print(f"  GPU: {self.system_info['gpu']['name']}")
            print(f"  CUDA: {self.system_info['gpu'].get('cuda_version', 'N/A')}")
        print("=" * 60)
        
        # Load models
        model_metrics = self.load_models()
        
        # Prepare avatar
        avatar_metrics = self.prepare_avatar()
        
        # Get all MP3 files
        audio_files = sorted(self.audio_dir.glob("*.mp3"))
        
        if not audio_files:
            print(f"\n❌ No MP3 files found in {self.audio_dir}")
            return
        
        print(f"\n📁 Found {len(audio_files)} audio files")
        
        # Process each audio file
        for audio_path in audio_files:
            result = self.process_audio(audio_path)
            self.results.append(result)
        
        # Generate summary
        self._generate_summary(model_metrics, avatar_metrics)
        
        # Save results
        self._save_results(model_metrics, avatar_metrics)
    
    def _generate_summary(self, model_metrics, avatar_metrics):
        """Generate and print benchmark summary"""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        print(f"\n✅ Successful: {len(successful)}/{len(self.results)}")
        if failed:
            print(f"❌ Failed: {len(failed)}/{len(self.results)}")
        
        if successful:
            avg_total = sum(r['total_time'] for r in successful) / len(successful)
            avg_fps = sum(r['fps'] for r in successful) / len(successful)
            avg_feature = sum(r['feature_extraction_time'] for r in successful) / len(successful)
            avg_gen = sum(r['generation_time'] for r in successful) / len(successful)
            
            print(f"\n⏱️  Average Timings:")
            print(f"   Model Load: {model_metrics['model_load_time']:.2f}s")
            print(f"   Avatar Prep: {avatar_metrics['avatar_prep_time']:.2f}s")
            print(f"   Feature Extraction: {avg_feature:.2f}s")
            print(f"   Frame Generation: {avg_gen:.2f}s")
            print(f"   Total per Audio: {avg_total:.2f}s")
            print(f"\n🎬 Performance:")
            print(f"   Average FPS: {avg_fps:.2f}")
            
            if self.device == "cuda" and successful[0].get('gpu_memory_peak'):
                avg_mem = sum(r['gpu_memory_peak']['allocated_mb'] for r in successful) / len(successful)
                print(f"\n💾 GPU Memory:")
                print(f"   Average Peak: {avg_mem:.2f} MB")
        
        print("=" * 60)
    
    def _save_results(self, model_metrics, avatar_metrics):
        """Save benchmark results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"benchmark_{timestamp}.json"
        
        report = {
            "system_info": self.system_info,
            "model_metrics": model_metrics,
            "avatar_metrics": avatar_metrics,
            "audio_results": self.results,
            "summary": {
                "total_tests": len(self.results),
                "successful": len([r for r in self.results if r['success']]),
                "failed": len([r for r in self.results if not r['success']])
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="MuseTalk GPU Benchmark Tool")
    parser.add_argument(
        "--audio-dir",
        type=str,
        default="test_assets/benchmark_audio",
        help="Directory containing MP3 files (default: test_assets/benchmark_audio)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/benchmarks",
        help="Directory to save results (default: results/benchmarks)"
    )
    parser.add_argument(
        "--avatar",
        type=str,
        default=None,
        help="Path to avatar video (optional, uses default if not provided)"
    )
    
    args = parser.parse_args()
    
    # Create benchmark instance
    benchmark = MuseTalkBenchmark(
        audio_dir=args.audio_dir,
        output_dir=args.output_dir,
        avatar_path=args.avatar
    )
    
    # Run benchmark
    benchmark.run_benchmark()


if __name__ == "__main__":
    main()
