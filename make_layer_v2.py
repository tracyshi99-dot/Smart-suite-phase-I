"""在 WSL 中运行: python3 /mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1/make_layer_v2.py"""
import subprocess
import shutil
import os

LAYER_DIR = "/tmp/layer2"
ZIP_OUT = "/tmp/fastapi_layer2.zip"
DEST = "/mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1/fastapi_layer.zip"

# Clean
if os.path.exists(LAYER_DIR):
    shutil.rmtree(LAYER_DIR)
os.makedirs(f"{LAYER_DIR}/python", exist_ok=True)

# Install with platform targeting Lambda (Amazon Linux 2)
subprocess.run([
    "pip3", "install",
    "fastapi", "mangum", "pydantic", "requests", "python-multipart",
    "-t", f"{LAYER_DIR}/python",
    "--platform", "manylinux2014_x86_64",
    "--implementation", "cp",
    "--python-version", "3.11",
    "--only-binary=:all:",
    "--quiet"
], check=True)

print("Dependencies installed (manylinux2014_x86_64)")

# Zip
if os.path.exists(ZIP_OUT):
    os.remove(ZIP_OUT)
shutil.make_archive(ZIP_OUT.replace(".zip", ""), "zip", LAYER_DIR, "python")

size = os.path.getsize(ZIP_OUT) / 1024 / 1024
print(f"Layer zip: {size:.1f} MB")

# Copy to Windows
shutil.copy(ZIP_OUT, DEST)
print(f"Copied to: {DEST}")
