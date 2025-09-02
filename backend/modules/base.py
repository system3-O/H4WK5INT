import asyncio
import aiohttp
import requests
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import time

from config.settings import settings
from utils.tor_proxy import TorSession

class BaseOSINTModule(ABC):
    """Base class for all OSINT modules"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('module', '')
        self.session = TorSession() if settings.use_tor else requests.Session()
    
    @abstractmethod
    async def run_investigation(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the OSINT investigation"""
        pass
    
    def log_result(self, message: str):
        """Log investigation result"""
        print(f"[{self.name.upper()}] {message}")
    
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[Dict]:
        """Make HTTP request through Tor if enabled"""
        try:
            if settings.use_tor:
                response = await self.session.get(url, **kwargs)
            else:
                if method.upper() == "GET":
                    response = requests.get(url, **kwargs)
                else:
                    response = requests.post(url, **kwargs)
            
            if response.status_code == 200:
                return response.json() if 'application/json' in response.headers.get('content-type', '') else {"content": response.text}
            else:
                self.log_result(f"Request failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result(f"Request error: {str(e)}")
            return None
    
    def format_result(self, result_type: str, data: Dict[str, Any], sub_module: str = None, 
                     confidence: int = 50, source_url: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Format result for database storage"""
        return {
            "type": result_type,
            "sub_module": sub_module,
            "data": data,
            "metadata": metadata or {},
            "confidence": confidence,
            "source_url": source_url,
            "timestamp": time.time()
        }