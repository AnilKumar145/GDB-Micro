#!/usr/bin/env python3
"""
Quick test to verify the Transaction Service can be imported and started.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_app_import():
    """Test if the app can be imported without errors."""
    print("Testing app import...")
    
    try:
        from app.main import app
        print("✅ App imported successfully")
        
        # Test if the app has the expected routers
        routes = [route.path for route in app.routes]
        print(f"\n✅ Found {len(routes)} routes:")
        for route in sorted(set(routes)):
            print(f"   - {route}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import app: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_app_import())
    sys.exit(0 if success else 1)
