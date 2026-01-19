"""
Quick diagnostic - tests imports without loading models
"""
import sys
import os

# Suppress warnings that might be causing issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

print("=== Marker Quick Diagnostic ===")
print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")

errors = []

# Test basic imports
try:
    print("\n1. Testing basic Marker imports...")
    from marker.config.parser import ConfigParser
    print("   ✓ ConfigParser OK")
except Exception as e:
    print(f"   ✗ ConfigParser failed: {e}")
    errors.append(f"ConfigParser: {e}")

try:
    from marker.models import create_model_dict
    print("   ✓ Models module OK")
except Exception as e:
    print(f"   ✗ Models module failed: {e}")
    errors.append(f"Models: {e}")

# Test environment
print("\n2. Checking environment...")
if os.getenv("GOOGLE_API_KEY"):
    print("   ✓ GOOGLE_API_KEY is set")
else:
    print("   ⚠ GOOGLE_API_KEY not set (needed for --use_llm)")

if os.getenv("TORCH_DEVICE"):
    print(f"   ✓ TORCH_DEVICE = {os.getenv('TORCH_DEVICE')}")
else:
    print("   ℹ TORCH_DEVICE not set (will auto-detect)")

# Test file existence
print("\n3. Checking PDF file...")
pdf_path = "Books/LotNR.pdf"
if os.path.exists(pdf_path):
    size = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"   ✓ PDF found: {pdf_path} ({size:.2f} MB)")
else:
    print(f"   ✗ PDF not found: {pdf_path}")
    errors.append(f"PDF not found: {pdf_path}")

print("\n=== Summary ===")
if errors:
    print("Errors found:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("✓ Basic checks passed")
    print("\nNote: Model loading will happen on first conversion")
    print("      This can take 5-15 minutes and download ~2-5GB")
    print("\nTo convert, run:")
    print("  marker_single Books\\LotNR.pdf --use_llm --output_dir Books")
