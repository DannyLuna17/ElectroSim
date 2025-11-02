#!/usr/bin/env python3
"""
Deployment script for ElectroSim Web Version
This script sets up everything needed to run ElectroSim in the browser.
"""

import shutil
import sys
from pathlib import Path

def main():
    """Deploy ElectroSim to web."""
    
    project_root = Path(__file__).parent
    web_dir = project_root / "web"
    electrosim_src = project_root / "electrosim"
    
    # Create web directory if it doesn't exist
    web_dir.mkdir(exist_ok=True)
    
    # Check if electrosim package exists
    if not electrosim_src.exists():
        return False
    
    # Copy electrosim package to web directory
    electrosim_web = web_dir / "electrosim"
    if electrosim_web.exists():
        shutil.rmtree(electrosim_web)
    
    shutil.copytree(electrosim_src, electrosim_web)
    
    # Check if web files exist
    required_files = [
        "index.html",
        "main_web.py", 
        "config_web.py",
        "server.py",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not (web_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        return False
    
    # Test if Python can import pygame (for server)
    try:
        import pygame
        print(f"Pygame available for server")
    except ImportError:
        print(f"Pygame not available, but server will still work")
    
    print("\nWeb deployment complete!")
    print("\nNext steps:")
    print("1. cd web")
    print("2. python server.py")
    print("3. Open http://localhost:8000 in your browser")
    print("4. Wait for Pyodide to load (30-60 seconds first time)")
    print("5. Click 'Start Simulation'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

