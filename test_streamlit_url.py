#!/usr/bin/env python3
"""
Test specific Streamlit app URLs and analyze response
"""
import requests
import time
from unicode_handler import safe_print

def test_streamlit_url(url):
    """Test a specific Streamlit URL with detailed analysis"""
    safe_print(f"🔍 Testing: {url}")
    
    try:
        # Test with different methods
        response = requests.get(url, timeout=15, allow_redirects=True)
        
        safe_print(f"Status: {response.status_code}")
        safe_print(f"Final URL: {response.url}")
        safe_print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content = response.text
            safe_print(f"Content length: {len(content)} chars")
            
            # Look for specific indicators
            indicators = ['streamlit', 'trenchcoat', 'dashboard', 'error', 'coin data']
            for indicator in indicators:
                if indicator.lower() in content.lower():
                    safe_print(f"✅ Found: {indicator}")
                else:
                    safe_print(f"❌ Missing: {indicator}")
            
            # Show first 500 chars
            safe_print(f"\nContent preview:")
            safe_print(content[:500])
            
        return response
        
    except Exception as e:
        safe_print(f"Error: {e}")
        return None

def main():
    """Test the Streamlit app URL"""
    url = "https://trenchcoat-pro.streamlit.app"
    
    safe_print("🚀 Streamlit App URL Test")
    safe_print("=" * 40)
    
    # Test main URL
    test_streamlit_url(url)
    
    safe_print("\n" + "=" * 40)
    safe_print("Waiting 30 seconds then testing again...")
    time.sleep(30)
    
    test_streamlit_url(url)

if __name__ == "__main__":
    main()