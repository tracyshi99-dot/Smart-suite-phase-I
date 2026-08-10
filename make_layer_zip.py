import shutil
import os

os.chdir("/tmp/layer")
shutil.make_archive("/tmp/fastapi_layer", "zip", ".", "python")
print(f"Created: /tmp/fastapi_layer.zip")
size = os.path.getsize("/tmp/fastapi_layer.zip") / 1024 / 1024
print(f"Size: {size:.1f} MB")

# Copy to Windows
shutil.copy("/tmp/fastapi_layer.zip", "/mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1/fastapi_layer.zip")
print("Copied to project root")
