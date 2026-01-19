"""
Quick test to see if Marker loads and what errors occur
"""
import sys
import traceback

try:
    print("Testing Marker imports...")
    from marker.config.parser import ConfigParser
    print("✓ ConfigParser imported")
    
    from marker.models import create_model_dict
    print("✓ Models module imported")
    print("Loading models (this may take a while on first run)...")
    models = create_model_dict()
    print("✓ Models loaded successfully")
    
    print("\nMarker is working correctly!")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
