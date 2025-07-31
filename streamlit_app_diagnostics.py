#!/usr/bin/env python3
"""
Streamlit App Diagnostics
Check Streamlit app status and configuration
"""
import requests
import json
from unicode_handler import safe_print

def check_streamlit_app():
    """Comprehensive Streamlit app diagnostics"""
    safe_print("🔍 Streamlit App Diagnostics")
    safe_print("=" * 40)
    
    urls_to_check = [
        "https://trenchcoat-pro.streamlit.app/",
        "https://trenchcoatpro.streamlit.app/",
        "https://app-trenchcoat-pro.streamlit.app/",
        "https://projecttrench.streamlit.app/",
        "https://trench.streamlit.app/"
    ]
    
    for url in urls_to_check:
        safe_print(f"\n📡 Checking: {url}")
        try:
            response = requests.get(url, timeout=10, allow_redirects=False)
            
            safe_print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                safe_print("✅ App is accessible!")
                content_preview = response.text[:500]
                if "trench" in content_preview.lower():
                    safe_print("✅ Contains TrenchCoat content")
                else:
                    safe_print("⚠️ May not be our app")
                break
                    
            elif response.status_code == 303:
                redirect_url = response.headers.get('location', 'No location header')
                safe_print(f"📍 Redirects to: {redirect_url}")
                
                if "auth" in redirect_url:
                    safe_print("🔒 App requires authentication - likely set to private")
                    safe_print("💡 Solution: Set app to public in Streamlit Cloud settings")
                
            elif response.status_code == 404:
                safe_print("❌ App not found at this URL")
                
            else:
                safe_print(f"⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            safe_print("⏰ Request timed out")
        except requests.exceptions.ConnectionError:
            safe_print("🔌 Connection failed")
        except Exception as e:
            safe_print(f"💥 Error: {e}")
    
    safe_print("\n" + "=" * 40)
    safe_print("📋 Diagnosis Summary:")
    safe_print("- If all URLs show 303 redirects to auth: App is set to private")
    safe_print("- If all URLs show 404: App may not exist or URL changed")
    safe_print("- If timeout/connection errors: Streamlit Cloud may be down")
    safe_print("\n💡 Next Steps:")
    safe_print("1. Check Streamlit Cloud dashboard for correct URL")
    safe_print("2. Ensure app is set to 'Public' not 'Private'")
    safe_print("3. If app doesn't exist, recreate from GitHub repo")

if __name__ == "__main__":
    check_streamlit_app()