import subprocess
import sys

# Install numpy
print("Installing numpy...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "-q"])
print("✅ numpy installed")

# Verify imports work
try:
    import numpy
    print("✅ numpy import successful")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")
