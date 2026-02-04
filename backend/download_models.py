"""
Script to download face recognition models.

Usage:
    python download_models.py --all
    python download_models.py --model mobilefacenet
    python download_models.py --model insightface
    python download_models.py --model facenet
    python download_models.py --model yunet
"""
import argparse
import os
import sys
import urllib.request
from pathlib import Path

# Model URLs (these are example URLs - users should get from official sources)
MODEL_URLS = {
    "mobilefacenet": {
        "url": "https://github.com/deepinsight/insightface/raw/master/model_zoo/buffalo_l/mobilefacenet.onnx",
        "path": "models/mobilefacenet/mobilefacenet.onnx",
        "size_mb": 4,
    },
    "insightface": {
        "url": "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        "path": "models/insightface/w600k_r50.onnx",
        "size_mb": 250,
        "note": "Download from InsightFace Model Zoo and extract w600k_r50.onnx",
    },
    "facenet": {
        "url": "https://huggingface.co/edtrain/FaceNet-ONNX/resolve/main/facenet.onnx",
        "path": "models/facenet/facenet.onnx",
        "size_mb": 95,
    },
    "yunet": {
        "url": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "path": "models/detection/face_detection_yunet_2023mar.onnx",
        "size_mb": 0.23,
    },
}

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file with progress indicator."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Downloading: {url}")
        print(f"To: {dest_path}")
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 // total_size)
                bar = '=' * (percent // 2) + '>' + ' ' * (50 - percent // 2)
                sys.stdout.write(f"\r[{bar}] {percent}%")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print("\n✓ Download complete!")
        return True
        
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False


def download_model(model_name: str, base_path: Path) -> bool:
    """Download a specific model."""
    if model_name not in MODEL_URLS:
        print(f"Unknown model: {model_name}")
        print(f"Available models: {', '.join(MODEL_URLS.keys())}")
        return False
    
    model_info = MODEL_URLS[model_name]
    dest_path = base_path / model_info["path"]
    
    if dest_path.exists():
        print(f"✓ {model_name} already exists at {dest_path}")
        return True
    
    print(f"\n{'='*60}")
    print(f"Model: {model_name}")
    print(f"Size: ~{model_info['size_mb']} MB")
    
    if "note" in model_info:
        print(f"Note: {model_info['note']}")
        print(f"\nPlease download manually from:")
        print(f"  {model_info['url']}")
        print(f"And place in: {dest_path}")
        return False
    
    return download_file(model_info["url"], dest_path)


def main():
    parser = argparse.ArgumentParser(description="Download face recognition models")
    parser.add_argument("--all", action="store_true", help="Download all models")
    parser.add_argument("--model", type=str, help="Download specific model")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    # Get backend directory
    script_dir = Path(__file__).parent
    base_path = script_dir
    
    if args.list:
        print("Available models:")
        for name, info in MODEL_URLS.items():
            path = base_path / info["path"]
            status = "✓ installed" if path.exists() else "✗ not installed"
            print(f"  - {name} (~{info['size_mb']} MB) [{status}]")
        return
    
    if args.all:
        print("Downloading all models...")
        success = 0
        for model_name in MODEL_URLS:
            if download_model(model_name, base_path):
                success += 1
        print(f"\n{'='*60}")
        print(f"Downloaded {success}/{len(MODEL_URLS)} models")
        
    elif args.model:
        download_model(args.model, base_path)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
