import time
import logging
import socket
from typing import Dict, List, Any, Optional
import json
import re

from utils.tor_proxy import make_tor_request

logger = logging.getLogger(__name__)

class GeographicIntelligence:
    """Geographic Intelligence (GEOINT) module for location-based analysis"""
    
    def __init__(self, use_tor: bool = True):
        """
        Initialize Geographic Intelligence module
        
        Args:
            use_tor: Whether to use Tor proxy for requests
        """
        self.use_tor = use_tor
    
    def ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """
        Perform IP geolocation lookup
        
        Args:
            ip_address: IP address to geolocate
            
        Returns:
            Dict containing geolocation information
        """
        results = {
            'ip_address': ip_address,
            'location': {},
            'network_info': {},
            'security_info': {},
            'sources': [],
            'timestamp': time.time()
        }
        
        try:
            # Validate IP address
            if not self._validate_ip(ip_address):
                return {
                    'error': 'Invalid IP address format',
                    'ip_address': ip_address,
                    'timestamp': time.time()
                }
            
            # Multiple geolocation sources
            sources = [
                self._ipapi_lookup,
                self._ipinfo_lookup,
                self._maxmind_lookup,
                self._ipgeolocation_lookup
            ]
            
            for source_func in sources:
                try:
                    source_result = source_func(ip_address)
                    if source_result.get('success'):
                        results['sources'].append(source_result)
                        
                        # Merge location data
                        if 'location' in source_result:
                            for key, value in source_result['location'].items():
                                if key not in results['location'] and value:
                                    results['location'][key] = value
                        
                        # Merge network info
                        if 'network_info' in source_result:
                            for key, value in source_result['network_info'].items():
                                if key not in results['network_info'] and value:
                                    results['network_info'][key] = value
                
                except Exception as e:
                    logger.warning(f"Geolocation source failed: {e}")
                    continue
            
            # Additional network analysis
            results['network_analysis'] = self._analyze_network(ip_address)
            
            # Security analysis
            results['security_analysis'] = self._analyze_ip_security(ip_address)
            
            results['success'] = len(results['sources']) > 0
            
        except Exception as e:
            logger.error(f"IP geolocation failed: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def location_search(self, query: str, search_type: str = 'general') -> Dict[str, Any]:
        """
        Search for location information
        
        Args:
            query: Location query (address, coordinates, place name)
            search_type: Type of search ('general', 'coordinates', 'address')
            
        Returns:
            Dict containing location search results
        """
        results = {
            'query': query,
            'search_type': search_type,
            'locations': [],
            'coordinates': None,
            'map_urls': [],
            'timestamp': time.time()
        }
        
        try:
            if search_type == 'coordinates':
                # Parse coordinates
                coords = self._parse_coordinates(query)
                if coords:
                    results['coordinates'] = coords
                    results['locations'] = [self._reverse_geocode(coords)]
                    results['map_urls'] = self._generate_map_urls(coords)
            
            elif search_type == 'address':
                # Geocode address
                geocode_result = self._geocode_address(query)
                if geocode_result:
                    results['locations'] = [geocode_result]
                    if geocode_result.get('coordinates'):
                        results['coordinates'] = geocode_result['coordinates']
                        results['map_urls'] = self._generate_map_urls(geocode_result['coordinates'])
            
            else:
                # General location search
                search_results = self._general_location_search(query)
                results['locations'] = search_results
                
                if search_results and search_results[0].get('coordinates'):
                    results['coordinates'] = search_results[0]['coordinates']
                    results['map_urls'] = self._generate_map_urls(search_results[0]['coordinates'])
            
            results['success'] = len(results['locations']) > 0
            
        except Exception as e:
            logger.error(f"Location search failed: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def osint_mapping(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create OSINT map from multiple entities with location data
        
        Args:
            entities: List of entities with location information
            
        Returns:
            Dict containing mapping analysis
        """
        results = {
            'entities': entities,
            'mapped_locations': [],
            'geographic_clusters': [],
            'distance_analysis': {},
            'map_data': {},
            'timestamp': time.time()
        }
        
        try:
            # Extract and validate coordinates
            valid_locations = []
            
            for entity in entities:
                if 'coordinates' in entity and entity['coordinates']:
                    coords = entity['coordinates']
                    if isinstance(coords, dict) and 'latitude' in coords and 'longitude' in coords:
                        valid_locations.append({
                            'entity': entity,
                            'coordinates': coords,
                            'lat': float(coords['latitude']),
                            'lon': float(coords['longitude'])
                        })
            
            results['mapped_locations'] = valid_locations
            
            # Cluster analysis
            if len(valid_locations) >= 2:
                results['geographic_clusters'] = self._analyze_clusters(valid_locations)
                results['distance_analysis'] = self._calculate_distances(valid_locations)
            
            # Generate map data
            results['map_data'] = self._generate_map_data(valid_locations)
            
            results['success'] = len(valid_locations) > 0
            
        except Exception as e:
            logger.error(f"OSINT mapping failed: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def _validate_ip(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            socket.inet_aton(ip_address)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip_address)
                return True
            except socket.error:
                return False
    
    def _ipapi_lookup(self, ip_address: str) -> Dict[str, Any]:
        """IP-API.com geolocation lookup"""
        try:
            url = f"http://ip-api.com/json/{ip_address}"
            
            if self.use_tor:
                response = make_tor_request('GET', url, timeout=10)
            else:
                import requests
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'source': 'ip-api.com',
                    'success': data.get('status') == 'success',
                    'location': {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'zip_code': data.get('zip')
                    },
                    'network_info': {
                        'isp': data.get('isp'),
                        'organization': data.get('org'),
                        'as_number': data.get('as')
                    }
                }
            
        except Exception as e:
            logger.warning(f"IP-API lookup failed: {e}")
        
        return {'source': 'ip-api.com', 'success': False}
    
    def _ipinfo_lookup(self, ip_address: str) -> Dict[str, Any]:
        """IPInfo.io geolocation lookup"""
        try:
            url = f"https://ipinfo.io/{ip_address}/json"
            
            if self.use_tor:
                response = make_tor_request('GET', url, timeout=10)
            else:
                import requests
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse location
                loc = data.get('loc', '').split(',')
                lat, lon = (float(loc[0]), float(loc[1])) if len(loc) == 2 else (None, None)
                
                return {
                    'source': 'ipinfo.io',
                    'success': True,
                    'location': {
                        'country': data.get('country'),
                        'region': data.get('region'),
                        'city': data.get('city'),
                        'latitude': lat,
                        'longitude': lon,
                        'timezone': data.get('timezone'),
                        'zip_code': data.get('postal')
                    },
                    'network_info': {
                        'organization': data.get('org'),
                        'hostname': data.get('hostname')
                    }
                }
                
        except Exception as e:
            logger.warning(f"IPInfo lookup failed: {e}")
        
        return {'source': 'ipinfo.io', 'success': False}
    
    def _maxmind_lookup(self, ip_address: str) -> Dict[str, Any]:
        """MaxMind GeoLite2 lookup (placeholder)"""
        # This would require MaxMind GeoLite2 database
        return {
            'source': 'maxmind',
            'success': False,
            'note': 'MaxMind GeoLite2 database not configured'
        }
    
    def _ipgeolocation_lookup(self, ip_address: str) -> Dict[str, Any]:
        """IPGeolocation.io lookup"""
        try:
            url = f"https://api.ipgeolocation.io/ipgeo?ip={ip_address}"
            
            if self.use_tor:
                response = make_tor_request('GET', url, timeout=10)
            else:
                import requests
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'source': 'ipgeolocation.io',
                    'success': True,
                    'location': {
                        'country': data.get('country_name'),
                        'country_code': data.get('country_code2'),
                        'region': data.get('state_prov'),
                        'city': data.get('city'),
                        'latitude': float(data.get('latitude', 0)),
                        'longitude': float(data.get('longitude', 0)),
                        'timezone': data.get('time_zone', {}).get('name'),
                        'zip_code': data.get('zipcode')
                    },
                    'network_info': {
                        'isp': data.get('isp'),
                        'organization': data.get('organization')
                    }
                }
                
        except Exception as e:
            logger.warning(f"IPGeolocation lookup failed: {e}")
        
        return {'source': 'ipgeolocation.io', 'success': False}
    
    def _analyze_network(self, ip_address: str) -> Dict[str, Any]:
        """Analyze network characteristics"""
        analysis = {
            'ip_type': 'unknown',
            'private_ip': False,
            'reserved_ip': False,
            'whois_info': {}
        }
        
        try:
            # IP type analysis
            import ipaddress
            ip_obj = ipaddress.ip_address(ip_address)
            
            analysis['ip_type'] = 'ipv6' if ip_obj.version == 6 else 'ipv4'
            analysis['private_ip'] = ip_obj.is_private
            analysis['reserved_ip'] = ip_obj.is_reserved
            analysis['multicast'] = ip_obj.is_multicast
            analysis['loopback'] = ip_obj.is_loopback
            
            # WHOIS lookup (simplified)
            analysis['whois_info'] = self._simple_whois_lookup(ip_address)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_ip_security(self, ip_address: str) -> Dict[str, Any]:
        """Analyze IP for security indicators"""
        analysis = {
            'reputation_checks': [],
            'blacklist_status': 'unknown',
            'threat_indicators': [],
            'proxy_detection': 'unknown'
        }
        
        try:
            # This would integrate with threat intelligence APIs
            # For now, return placeholder data
            analysis['note'] = 'Security analysis requires threat intelligence API integration'
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _parse_coordinates(self, coord_string: str) -> Optional[Dict[str, float]]:
        """Parse coordinate string into lat/lon"""
        try:
            # Match various coordinate formats
            patterns = [
                r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)',  # lat,lon
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',   # lat lon
                r'(\d+\.?\d*)[°]?\s*([NS])\s*(\d+\.?\d*)[°]?\s*([EW])'  # DMS format
            ]
            
            for pattern in patterns:
                match = re.search(pattern, coord_string)
                if match:
                    if len(match.groups()) == 2:
                        lat, lon = float(match.group(1)), float(match.group(2))
                        return {'latitude': lat, 'longitude': lon}
                    elif len(match.groups()) == 4:
                        # DMS format
                        lat = float(match.group(1))
                        if match.group(2) == 'S':
                            lat = -lat
                        lon = float(match.group(3))
                        if match.group(4) == 'W':
                            lon = -lon
                        return {'latitude': lat, 'longitude': lon}
            
        except Exception as e:
            logger.warning(f"Coordinate parsing failed: {e}")
        
        return None
    
    def _reverse_geocode(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Reverse geocode coordinates to location"""
        # Placeholder - would use geocoding API
        return {
            'coordinates': coordinates,
            'address': 'Reverse geocoding not implemented',
            'note': 'Requires geocoding API integration'
        }
    
    def _geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode address to coordinates"""
        # Placeholder - would use geocoding API
        return {
            'address': address,
            'coordinates': None,
            'note': 'Geocoding not implemented - requires API integration'
        }
    
    def _general_location_search(self, query: str) -> List[Dict[str, Any]]:
        """General location search"""
        # Placeholder - would integrate with mapping APIs
        return [{
            'query': query,
            'note': 'General location search not implemented'
        }]
    
    def _generate_map_urls(self, coordinates: Dict[str, float]) -> List[str]:
        """Generate map URLs for coordinates"""
        lat, lon = coordinates['latitude'], coordinates['longitude']
        
        return [
            f"https://www.google.com/maps/@{lat},{lon},15z",
            f"https://www.openstreetmap.org/#map=15/{lat}/{lon}",
            f"https://www.bing.com/maps?cp={lat}~{lon}&lvl=15"
        ]
    
    def _analyze_clusters(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze geographic clusters"""
        # Simplified clustering - would use proper clustering algorithms
        clusters = []
        
        if len(locations) >= 2:
            clusters.append({
                'cluster_id': 1,
                'locations': locations,
                'center': self._calculate_center(locations),
                'radius_km': self._calculate_max_distance(locations)
            })
        
        return clusters
    
    def _calculate_distances(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate distances between locations"""
        distances = {}
        
        for i, loc1 in enumerate(locations):
            for j, loc2 in enumerate(locations[i+1:], i+1):
                distance = self._haversine_distance(
                    loc1['lat'], loc1['lon'],
                    loc2['lat'], loc2['lon']
                )
                distances[f"location_{i}_to_{j}"] = {
                    'distance_km': distance,
                    'from': loc1['entity'].get('name', f'Location {i}'),
                    'to': loc2['entity'].get('name', f'Location {j}')
                }
        
        return distances
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _calculate_center(self, locations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate geographic center of locations"""
        if not locations:
            return {'latitude': 0, 'longitude': 0}
        
        lat_sum = sum(loc['lat'] for loc in locations)
        lon_sum = sum(loc['lon'] for loc in locations)
        
        return {
            'latitude': lat_sum / len(locations),
            'longitude': lon_sum / len(locations)
        }
    
    def _calculate_max_distance(self, locations: List[Dict[str, Any]]) -> float:
        """Calculate maximum distance between any two locations"""
        max_distance = 0
        
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                distance = self._haversine_distance(
                    loc1['lat'], loc1['lon'],
                    loc2['lat'], loc2['lon']
                )
                max_distance = max(max_distance, distance)
        
        return max_distance
    
    def _generate_map_data(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate map visualization data"""
        if not locations:
            return {}
        
        return {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [loc['lon'], loc['lat']]
                    },
                    'properties': {
                        'name': loc['entity'].get('name', 'Unknown'),
                        'description': loc['entity'].get('description', ''),
                        'entity_type': loc['entity'].get('type', 'unknown')
                    }
                }
                for loc in locations
            ]
        }
    
    def _simple_whois_lookup(self, ip_address: str) -> Dict[str, Any]:
        """Simple WHOIS lookup for IP"""
        # Placeholder - would use proper WHOIS library
        return {
            'note': 'WHOIS lookup not implemented',
            'ip': ip_address
        }

def run_geoint(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Run geographic intelligence operation
    
    Args:
        operation: Type of operation to run
        **kwargs: Operation parameters
        
    Returns:
        Dict containing operation results
    """
    geoint = GeographicIntelligence(use_tor=kwargs.get('use_tor', True))
    
    try:
        if operation == 'ip_geolocation':
            ip_address = kwargs.get('ip_address')
            if not ip_address:
                return {'error': 'ip_address parameter required'}
            return geoint.ip_geolocation(ip_address)
        
        elif operation == 'location_search':
            query = kwargs.get('query')
            search_type = kwargs.get('search_type', 'general')
            if not query:
                return {'error': 'query parameter required'}
            return geoint.location_search(query, search_type)
        
        elif operation == 'osint_mapping':
            entities = kwargs.get('entities', [])
            return geoint.osint_mapping(entities)
        
        else:
            return {
                'error': f'Unknown operation: {operation}',
                'available_operations': [
                    'ip_geolocation', 'location_search', 'osint_mapping'
                ]
            }
    
    except Exception as e:
        logger.error(f"Geographic intelligence operation failed: {e}")
        return {
            'error': str(e),
            'operation': operation,
            'timestamp': time.time()
        }