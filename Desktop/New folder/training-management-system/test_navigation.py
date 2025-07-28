"""
Navigation Testing Script
Test all navigation URLs to ensure they work correctly
"""

import requests
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

# Test URLs
test_urls = [
    # Public URLs (should work without login)
    ('/', 'Homepage'),
    ('/formations/', 'Formations List'),
    ('/courses/', 'Courses List'),
    ('/users/login/', 'Login Page'),
    ('/users/register/', 'Register Page'),
    ('/admin/', 'Admin Panel'),
    
    # Redirect URLs
    ('/login/', 'Login Redirect'),
    ('/register/', 'Register Redirect'),
    ('/dashboard/', 'Dashboard Redirect'),
    
    # Protected URLs (should redirect to login)
    ('/messaging/inbox/', 'Messaging Inbox'),
    ('/users/dashboard/', 'User Dashboard'),
    ('/users/profile/', 'User Profile'),
]

def test_navigation():
    print("🔍 Testing Navigation URLs...")
    print("=" * 50)
    
    for url_path, description in test_urls:
        full_url = urljoin(BASE_URL, url_path)
        try:
            response = requests.get(full_url, allow_redirects=False)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {description:<20} | {url_path:<25} | Status: {status}")
            elif status in [301, 302]:
                redirect_to = response.headers.get('Location', 'Unknown')
                print(f"🔄 {description:<20} | {url_path:<25} | Redirect to: {redirect_to}")
            elif status == 404:
                print(f"❌ {description:<20} | {url_path:<25} | Not Found (404)")
            else:
                print(f"⚠️  {description:<20} | {url_path:<25} | Status: {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"🔴 {description:<20} | {url_path:<25} | Server Not Running")
        except Exception as e:
            print(f"🔴 {description:<20} | {url_path:<25} | Error: {e}")
    
    print("=" * 50)
    print("✅ = Working  🔄 = Redirect  ❌ = Not Found  ⚠️ = Other Error")

if __name__ == "__main__":
    test_navigation()
