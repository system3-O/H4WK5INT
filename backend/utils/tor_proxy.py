import requests
import asyncio
import aiohttp
from config.settings import settings

class TorSession:
    """Session class for making requests through Tor"""
    
    def __init__(self):
        self.proxies = {
            'http': settings.tor_proxy,
            'https': settings.tor_proxy
        } if settings.use_tor else {}
        
        self.session = requests.Session()
        if settings.use_tor:
            self.session.proxies.update(self.proxies)
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def get(self, url: str, **kwargs):
        """Make GET request through Tor"""
        return self.session.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs):
        """Make POST request through Tor"""
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close session"""
        self.session.close()

def test_tor_connection() -> bool:
    """Test if Tor connection is working"""
    try:
        session = TorSession()
        response = session.session.get('https://check.torproject.org/api/ip', timeout=10)
        data = response.json()
        return data.get('IsTor', False)
    except Exception as e:
        print(f"Tor connection test failed: {e}")
        return False