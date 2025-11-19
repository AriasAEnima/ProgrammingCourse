#!/usr/bin/env python3
"""
🐳 Universal Docker Build Script
Cross-platform builder for the Image Processing Project

Usage:
    python build.py              # Build production images
    python build.py --dev        # Build development images  
    python build.py --clean      # Clean up old images first
"""

import subprocess
import sys
import argparse
import platform

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n> {description}")
    print(f"Running: {cmd}")
    
    try:
        # Use utf-8 encoding to avoid Windows cp1252 issues
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'  # Ignore problematic characters
        )
        print(f"Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is available"""
    print("Checking Docker...")
    if not run_command("docker --version", "Verify Docker installation"):
        print("ERROR: Docker not found! Please install Docker Desktop")
        sys.exit(1)

def clean_images():
    """Clean up old images"""
    print("\nCleaning up old images...")
    
    # Remove old project images
    old_images = [
        "projects-api", "projects-api-1", "projects-api-2",
        "projects-worker", "projects-worker-1", "projects-worker-2",
        "projects-api-optimized", "projects-worker-optimized",
        "projects-api-minimal", "projects-worker-minimal"
    ]
    
    for image in old_images:
        run_command(f"docker rmi {image}:latest", f"Remove {image}")
    
    # Clean up dangling images
    run_command("docker image prune -f", "Remove dangling images")

def build_images(dev_mode=False):
    """Build the final production images"""
    print(f"\nBuilding {'development' if dev_mode else 'production'} images...")
    
    dockerfile_suffix = "" if not dev_mode else ".dev"
    tag_suffix = "-final" if not dev_mode else "-dev"
    
    # Build API image
    api_cmd = f"docker build -f docker/Dockerfile.api.final{dockerfile_suffix} -t projects-api{tag_suffix}:latest ."
    if not run_command(api_cmd, f"Build API image"):
        return False
    
    # Build Worker image  
    worker_cmd = f"docker build -f docker/Dockerfile.worker.final{dockerfile_suffix} -t projects-worker{tag_suffix}:latest ."
    if not run_command(worker_cmd, f"Build Worker image"):
        return False
    
    return True

def show_images():
    """Show built images"""
    print("\nBuilt images:")
    # Cross-platform: use docker images with filter instead of grep
    run_command("docker images projects*", "List project images")

def main():
    parser = argparse.ArgumentParser(description="Universal Docker Build Script")
    parser.add_argument("--dev", action="store_true", help="Build development images")
    parser.add_argument("--clean", action="store_true", help="Clean old images first")
    
    args = parser.parse_args()
    
    print("UNIVERSAL DOCKER BUILD SCRIPT")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print("="*50)
    
    # Check prerequisites
    check_docker()
    
    # Clean if requested
    if args.clean:
        clean_images()
    
    # Build images
    if build_images(dev_mode=args.dev):
        show_images()
        
        print(f"\nSUCCESS! Images built successfully!")
        print(f"Next steps:")
        if args.dev:
            print(f"   docker-compose up")
        else:
            print(f"   cd k8s && python demo.py")
    else:
        print(f"\nBUILD FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()