"""
Check where Marker/Surya models are cached and if they exist
"""
import os
from pathlib import Path

print("=== Model Cache Location Check ===\n")

# Check HuggingFace cache locations
cache_locations = []

# Default HuggingFace cache (Windows)
home = Path.home()
default_cache = home / ".cache" / "huggingface" / "hub"
cache_locations.append(("Default HF cache", default_cache))

# HF_HOME environment variable
if os.getenv("HF_HOME"):
    hf_home = Path(os.getenv("HF_HOME")) / "hub"
    cache_locations.append(("HF_HOME env var", hf_home))

# TRANSFORMERS_CACHE (older, deprecated)
if os.getenv("TRANSFORMERS_CACHE"):
    transformers_cache = Path(os.getenv("TRANSFORMERS_CACHE"))
    cache_locations.append(("TRANSFORMERS_CACHE (deprecated)", transformers_cache))

print("Cache locations to check:")
for name, path in cache_locations:
    exists = path.exists()
    print(f"\n{name}:")
    print(f"  Path: {path}")
    print(f"  Exists: {exists}")
    
    if exists:
        try:
            # List model directories
            model_dirs = [d for d in path.iterdir() if d.is_dir()]
            print(f"  Model directories found: {len(model_dirs)}")
            
            # Look for Surya models (typically start with "models--vikp--" or similar)
            surya_models = [d for d in model_dirs if "surya" in d.name.lower() or "vikp" in d.name.lower()]
            if surya_models:
                print(f"  Surya-related models: {len(surya_models)}")
                for model in surya_models[:5]:  # Show first 5
                    size = sum(f.stat().st_size for f in model.rglob('*') if f.is_file())
                    size_mb = size / (1024 * 1024)
                    print(f"    - {model.name} ({size_mb:.1f} MB)")
        except PermissionError:
            print("  ⚠ Permission denied")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

print("\n=== Why models might download multiple times ===")
print("""
1. **Different Python environments** - Each virtual environment has its own cache
   Solution: Use the same environment, or set HF_HOME to a shared location

2. **Cache cleared** - Someone/something deleted the cache directory
   Solution: Don't delete ~/.cache/huggingface/ (or your HF_HOME)

3. **Different users** - Each user account has its own cache
   Solution: Set HF_HOME to a shared location if needed

4. **Model version changes** - If Surya updates model checkpoints, new versions download
   Solution: This is normal - old versions stay cached, new ones download

5. **Cache directory issues** - Permissions or disk space problems
   Solution: Check disk space and permissions on cache directory
""")

print("\n=== Recommendations ===")
print("""
To ensure models only download once:
1. Set HF_HOME to a persistent location:
   $env:HF_HOME = "C:\\Users\\paris\\.huggingface"
   
2. Check if models are already cached before running conversion
3. Use the same Python environment for all Marker runs
""")
