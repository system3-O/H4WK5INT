import time
import logging
from typing import Dict, List, Any, Optional
import json
import requests
from PIL import Image
from PIL.ExifTags import TAGS
import io
import os

from utils.tor_proxy import make_tor_request

logger = logging.getLogger(__name__)

class ImageIntelligence:
    """Image Intelligence (IMINT) module for image analysis and reverse search"""
    
    def __init__(self, use_tor: bool = True):
        """
        Initialize Image Intelligence module
        
        Args:
            use_tor: Whether to use Tor proxy for requests
        """
        self.use_tor = use_tor
    
    def reverse_image_search(self, image_url: str) -> Dict[str, Any]:
        """
        Perform reverse image search using multiple engines
        
        Args:
            image_url: URL of image to search
            
        Returns:
            Dict containing reverse search results
        """
        results = {
            'image_url': image_url,
            'search_engines': {},
            'similar_images': [],
            'possible_sources': [],
            'timestamp': time.time()
        }
        
        try:
            # Google Images reverse search
            google_results = self._google_reverse_search(image_url)
            results['search_engines']['google'] = google_results
            
            # TinEye reverse search
            tineye_results = self._tineye_reverse_search(image_url)
            results['search_engines']['tineye'] = tineye_results
            
            # Yandex reverse search
            yandex_results = self._yandex_reverse_search(image_url)
            results['search_engines']['yandex'] = yandex_results
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"Reverse image search failed: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def extract_exif_data(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dict containing EXIF data
        """
        results = {
            'exif_data': {},
            'gps_coordinates': None,
            'camera_info': {},
            'timestamp_info': {},
            'software_info': {},
            'timestamp': time.time()
        }
        
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Extract EXIF data
            exif_data = image.getexif()
            
            if exif_data:
                exif_dict = {}
                gps_info = {}
                
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_dict[tag] = value
                    
                    # Extract specific information
                    if tag == 'GPSInfo':
                        gps_info = value
                    elif tag in ['Make', 'Model']:
                        results['camera_info'][tag.lower()] = value
                    elif tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        results['timestamp_info'][tag.lower()] = value
                    elif tag in ['Software', 'ProcessingSoftware']:
                        results['software_info'][tag.lower()] = value
                
                results['exif_data'] = exif_dict
                
                # Process GPS coordinates
                if gps_info:
                    coordinates = self._parse_gps_coordinates(gps_info)
                    results['gps_coordinates'] = coordinates
            
            # Additional image properties
            results['image_properties'] = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'has_transparency': 'transparency' in image.info
            }
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"EXIF extraction failed: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def analyze_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive image metadata analysis
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing comprehensive metadata analysis
        """
        results = {
            'file_info': {},
            'exif_analysis': {},
            'security_analysis': {},
            'forensic_indicators': [],
            'timestamp': time.time()
        }
        
        try:
            # File system information
            stat_info = os.stat(image_path)
            results['file_info'] = {
                'size_bytes': stat_info.st_size,
                'created': time.ctime(stat_info.st_ctime),
                'modified': time.ctime(stat_info.st_mtime),
                'accessed': time.ctime(stat_info.st_atime)
            }
            
            # Read image data
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # EXIF analysis
            results['exif_analysis'] = self.extract_exif_data(image_data)
            
            # Security analysis
            results['security_analysis'] = self._analyze_image_security(image_data)
            
            # Forensic indicators
            results['forensic_indicators'] = self._detect_forensic_indicators(image_data)
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"Image metadata analysis failed: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def facial_recognition_search(self, image_data: bytes) -> Dict[str, Any]:
        """
        Placeholder for facial recognition search
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dict containing facial recognition results
        """
        return {
            'error': 'Facial recognition not implemented - requires specialized APIs',
            'note': 'This feature would integrate with services like PimEyes, FindClone, or custom face recognition models',
            'timestamp': time.time(),
            'success': False
        }
    
    def _google_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """Google Images reverse search"""
        try:
            search_url = f"https://www.google.com/searchbyimage?image_url={image_url}"
            
            if self.use_tor:
                response = make_tor_request('GET', search_url, timeout=15)
            else:
                response = requests.get(search_url, timeout=15)
            
            return {
                'status': 'completed',
                'search_url': search_url,
                'response_code': response.status_code,
                'note': 'Google reverse search requires HTML parsing for full results'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _tineye_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """TinEye reverse search"""
        try:
            search_url = f"https://tineye.com/search?url={image_url}"
            
            if self.use_tor:
                response = make_tor_request('GET', search_url, timeout=15)
            else:
                response = requests.get(search_url, timeout=15)
            
            return {
                'status': 'completed',
                'search_url': search_url,
                'response_code': response.status_code,
                'note': 'TinEye API integration recommended for better results'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _yandex_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """Yandex reverse search"""
        try:
            search_url = f"https://yandex.com/images/search?rpt=imageview&url={image_url}"
            
            if self.use_tor:
                response = make_tor_request('GET', search_url, timeout=15)
            else:
                response = requests.get(search_url, timeout=15)
            
            return {
                'status': 'completed',
                'search_url': search_url,
                'response_code': response.status_code,
                'note': 'Yandex often provides good results for reverse image search'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _parse_gps_coordinates(self, gps_info: dict) -> Optional[Dict[str, float]]:
        """Parse GPS coordinates from EXIF GPS info"""
        try:
            def convert_to_degrees(value):
                d, m, s = value
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = convert_to_degrees(gps_info.get(2, [0, 0, 0]))
            lat_ref = gps_info.get(1, 'N')
            
            lon = convert_to_degrees(gps_info.get(4, [0, 0, 0]))
            lon_ref = gps_info.get(3, 'E')
            
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon
            
            return {
                'latitude': lat,
                'longitude': lon,
                'latitude_ref': lat_ref,
                'longitude_ref': lon_ref
            }
            
        except Exception as e:
            logger.warning(f"GPS coordinate parsing failed: {e}")
            return None
    
    def _analyze_image_security(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image for security indicators"""
        analysis = {
            'file_size': len(image_data),
            'entropy_analysis': {},
            'header_analysis': {},
            'suspicious_indicators': []
        }
        
        try:
            # Basic header analysis
            header = image_data[:20]
            
            # JPEG header check
            if header.startswith(b'\xff\xd8\xff'):
                analysis['file_type'] = 'JPEG'
                analysis['header_analysis']['valid_jpeg'] = True
            # PNG header check
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                analysis['file_type'] = 'PNG'
                analysis['header_analysis']['valid_png'] = True
            else:
                analysis['suspicious_indicators'].append('Unknown or modified file header')
            
            # Size analysis
            if len(image_data) > 10 * 1024 * 1024:  # 10MB
                analysis['suspicious_indicators'].append('Unusually large file size')
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _detect_forensic_indicators(self, image_data: bytes) -> List[str]:
        """Detect forensic indicators in image"""
        indicators = []
        
        try:
            # Check for embedded data (steganography indicators)
            if b'PK' in image_data[100:]:  # ZIP signature
                indicators.append('Possible ZIP archive embedded')
            
            if b'%PDF' in image_data[100:]:  # PDF signature
                indicators.append('Possible PDF embedded')
            
            # Check for unusual metadata
            if len(image_data) < 1000:
                indicators.append('Unusually small image file')
            
        except Exception as e:
            indicators.append(f'Forensic analysis error: {str(e)}')
        
        return indicators

def run_image_intel(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Run image intelligence operation
    
    Args:
        operation: Type of operation to run
        **kwargs: Operation parameters
        
    Returns:
        Dict containing operation results
    """
    imint = ImageIntelligence(use_tor=kwargs.get('use_tor', True))
    
    try:
        if operation == 'reverse_image_search':
            image_url = kwargs.get('image_url')
            if not image_url:
                return {'error': 'image_url parameter required'}
            return imint.reverse_image_search(image_url)
        
        elif operation == 'exif_extraction':
            image_data = kwargs.get('image_data')
            if not image_data:
                return {'error': 'image_data parameter required'}
            return imint.extract_exif_data(image_data)
        
        elif operation == 'metadata_analysis':
            image_path = kwargs.get('image_path')
            if not image_path:
                return {'error': 'image_path parameter required'}
            return imint.analyze_image_metadata(image_path)
        
        elif operation == 'facial_recognition':
            image_data = kwargs.get('image_data')
            if not image_data:
                return {'error': 'image_data parameter required'}
            return imint.facial_recognition_search(image_data)
        
        else:
            return {
                'error': f'Unknown operation: {operation}',
                'available_operations': [
                    'reverse_image_search', 'exif_extraction',
                    'metadata_analysis', 'facial_recognition'
                ]
            }
    
    except Exception as e:
        logger.error(f"Image intelligence operation failed: {e}")
        return {
            'error': str(e),
            'operation': operation,
            'timestamp': time.time()
        }