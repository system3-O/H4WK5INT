import requests
import socket
import socks
from urllib.parse import urlparse
import time
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class TorProxy:
    """Tor SOCKS proxy manager for anonymous requests"""
    
    def __init__(self, proxy_url: str = 'socks5://127.0.0.1:9050', timeout: int = 30):
        """
        Initialize Tor proxy
        
        Args:
            proxy_url: SOCKS proxy URL (default: socks5://127.0.0.1:9050)
            timeout: Request timeout in seconds
        """
        self.proxy_url = proxy_url
        self.timeout = timeout
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with Tor proxy"""
        try:
            parsed_proxy = urlparse(self.proxy_url)
            
            self.session = requests.Session()
            
            # Configure proxy
            proxies = {
                'http': self.proxy_url,
                'https': self.proxy_url
            }
            self.session.proxies.update(proxies)
            
            # Set headers to mimic a regular browser
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            logger.info(f"Tor proxy session configured with {self.proxy_url}")
            
        except Exception as e:
            logger.error(f"Failed to setup Tor proxy session: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Tor connection and get IP information
        
        Returns:
            Dict containing connection status and IP information
        """
        try:
            # Test basic connectivity
            response = self.session.get('https://httpbin.org/ip', timeout=self.timeout)
            
            if response.status_code == 200:
                ip_info = response.json()
                
                # Get Tor check information
                tor_check = self.check_tor_status()
                
                return {
                    'status': 'connected',
                    'ip_address': ip_info.get('origin'),
                    'tor_enabled': tor_check['tor_enabled'],
                    'response_time': response.elapsed.total_seconds(),
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                    'timestamp': time.time()
                }
                
        except requests.exceptions.ProxyError as e:
            logger.error(f"Tor proxy connection failed: {e}")
            return {
                'status': 'proxy_error',
                'error': str(e),
                'timestamp': time.time()
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"Tor connection timeout: {e}")
            return {
                'status': 'timeout',
                'error': str(e),
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Tor connection test failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def check_tor_status(self) -> Dict[str, Any]:
        """
        Check if connection is actually using Tor
        
        Returns:
            Dict containing Tor status information
        """
        try:
            # Check with Tor Project's check service
            response = self.session.get('https://check.torproject.org/api/ip', timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'tor_enabled': data.get('IsTor', False),
                    'ip_address': data.get('IP'),
                    'country': data.get('Country'),
                    'timestamp': time.time()
                }
            else:
                return {
                    'tor_enabled': False,
                    'error': f'HTTP {response.status_code}',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.warning(f"Could not verify Tor status: {e}")
            return {
                'tor_enabled': None,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make GET request through Tor
        
        Args:
            url: URL to request
            **kwargs: Additional requests parameters
            
        Returns:
            requests.Response object
        """
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Make POST request through Tor
        
        Args:
            url: URL to request
            **kwargs: Additional requests parameters
            
        Returns:
            requests.Response object
        """
        kwargs.setdefault('timeout', self.timeout)
        return self.session.post(url, **kwargs)
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request through Tor
        
        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional requests parameters
            
        Returns:
            requests.Response object
        """
        kwargs.setdefault('timeout', self.timeout)
        return self.session.request(method, url, **kwargs)
    
    def new_circuit(self) -> bool:
        """
        Request new Tor circuit (requires Tor control port access)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would require stem library and Tor control port access
            # For now, we'll just recreate the session
            self._setup_session()
            
            # Test the new circuit
            test_result = self.test_connection()
            return test_result.get('status') == 'connected'
            
        except Exception as e:
            logger.error(f"Failed to create new Tor circuit: {e}")
            return False
    
    def close(self):
        """Close the Tor proxy session"""
        if self.session:
            self.session.close()
            logger.info("Tor proxy session closed")

# Global Tor proxy instance
_tor_proxy: Optional[TorProxy] = None

def get_tor_proxy(proxy_url: str = 'socks5://127.0.0.1:9050', timeout: int = 30) -> TorProxy:
    """
    Get global Tor proxy instance
    
    Args:
        proxy_url: SOCKS proxy URL
        timeout: Request timeout
        
    Returns:
        TorProxy instance
    """
    global _tor_proxy
    
    if _tor_proxy is None:
        _tor_proxy = TorProxy(proxy_url, timeout)
    
    return _tor_proxy

def make_tor_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Make HTTP request through Tor proxy
    
    Args:
        method: HTTP method
        url: URL to request
        **kwargs: Additional requests parameters
        
    Returns:
        requests.Response object
    """
    proxy = get_tor_proxy()
    return proxy.request(method, url, **kwargs)

def test_tor_connection() -> Dict[str, Any]:
    """
    Test Tor connection and return status
    
    Returns:
        Dict containing connection status
    """
    try:
        proxy = get_tor_proxy()
        return proxy.test_connection()
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }

def check_tor_availability() -> bool:
    """
    Check if Tor proxy is available
    
    Returns:
        True if Tor is available, False otherwise
    """
    try:
        # Try to connect to Tor SOCKS port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        return result == 0
    except Exception:
        return False