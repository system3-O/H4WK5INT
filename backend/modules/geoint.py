from typing import List, Dict, Any
import re
import socket
import ipaddress
from modules.base import BaseOSINTModule

class GEOINTModule(BaseOSINTModule):
    """Geographic Intelligence Module"""
    
    async def run_investigation(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run GEOINT investigation"""
        results = []
        location_types = options.get('location_types', ['ip_geo', 'address', 'coordinates'])
        
        self.log_result(f"Starting GEOINT investigation for: {query}")
        
        # Determine query type
        query_type = self._detect_location_type(query)
        
        for location_type in location_types:
            try:
                if location_type == 'ip_geo' and (query_type == 'ip' or self._is_ip(query)):
                    results.extend(await self._geolocate_ip(query))
                elif location_type == 'address' and query_type == 'address':
                    results.extend(await self._geocode_address(query))
                elif location_type == 'coordinates' and query_type == 'coordinates':
                    results.extend(await self._reverse_geocode(query))
                elif location_type == 'domain_geo':
                    results.extend(await self._geolocate_domain(query))
            except Exception as e:
                self.log_result(f"Error in {location_type} analysis: {e}")
        
        return results
    
    def _detect_location_type(self, query: str) -> str:
        """Detect the type of location query"""
        if self._is_ip(query):
            return 'ip'
        elif self._is_coordinates(query):
            return 'coordinates'
        elif self._is_domain(query):
            return 'domain'
        else:
            return 'address'
    
    def _is_ip(self, query: str) -> bool:
        """Check if query is an IP address"""
        try:
            ipaddress.ip_address(query.strip())
            return True
        except ValueError:
            return False
    
    def _is_coordinates(self, query: str) -> bool:
        """Check if query contains coordinates"""
        coord_patterns = [
            r'^-?\d+\.?\d*,-?\d+\.?\d*$',  # lat,lng
            r'^-?\d+\.?\d*\s+-?\d+\.?\d*$',  # lat lng
        ]
        return any(re.match(pattern, query.strip()) for pattern in coord_patterns)
    
    def _is_domain(self, query: str) -> bool:
        """Check if query is a domain"""
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, query.strip()))
    
    async def _geolocate_ip(self, ip: str) -> List[Dict[str, Any]]:
        """Geolocate IP address"""
        results = []
        
        try:
            # IP validation
            ip_obj = ipaddress.ip_address(ip)
            
            # Check if IP is private
            if ip_obj.is_private:
                results.append(self.format_result(
                    "ip_analysis",
                    {
                        "ip": ip,
                        "type": "private",
                        "location": "Local network",
                        "country": "Unknown",
                        "city": "Unknown",
                        "isp": "Unknown"
                    },
                    sub_module="ip_geolocation",
                    confidence=100,
                    metadata={"ip_type": "private"}
                ))
                return results
            
            # Simulate geolocation lookup (would use real API in production)
            geo_data = await self._lookup_ip_geolocation(ip)
            if geo_data:
                results.append(self.format_result(
                    "ip_geolocation",
                    geo_data,
                    sub_module="ip_geolocation",
                    confidence=85,
                    metadata={"source": "geolocation_api"}
                ))
            
            # ASN lookup
            asn_data = await self._lookup_asn(ip)
            if asn_data:
                results.append(self.format_result(
                    "asn_info",
                    asn_data,
                    sub_module="asn_lookup",
                    confidence=90,
                    metadata={"source": "asn_database"}
                ))
            
            # Reverse DNS lookup
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                results.append(self.format_result(
                    "reverse_dns",
                    {
                        "ip": ip,
                        "hostname": hostname,
                        "query_type": "PTR"
                    },
                    sub_module="reverse_dns",
                    confidence=95,
                    metadata={"lookup_type": "reverse_dns"}
                ))
            except socket.herror:
                pass
        
        except Exception as e:
            self.log_result(f"IP geolocation error: {e}")
        
        return results
    
    async def _geocode_address(self, address: str) -> List[Dict[str, Any]]:
        """Geocode physical address"""
        results = []
        
        try:
            # Simulate address geocoding
            geocoded_data = {
                "address": address,
                "formatted_address": f"Formatted {address}",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "country": "United States",
                "state": "New York",
                "city": "New York",
                "postal_code": "10001",
                "accuracy": "ROOFTOP"
            }
            
            results.append(self.format_result(
                "geocoded_address",
                geocoded_data,
                sub_module="address_geocoding",
                confidence=80,
                metadata={"geocoding_service": "simulated"}
            ))
            
            # Nearby points of interest
            poi_data = await self._find_nearby_poi(geocoded_data["latitude"], geocoded_data["longitude"])
            if poi_data:
                results.append(self.format_result(
                    "nearby_poi",
                    poi_data,
                    sub_module="poi_search",
                    confidence=75,
                    metadata={"radius": "1km"}
                ))
        
        except Exception as e:
            self.log_result(f"Address geocoding error: {e}")
        
        return results
    
    async def _reverse_geocode(self, coordinates: str) -> List[Dict[str, Any]]:
        """Reverse geocode coordinates to address"""
        results = []
        
        try:
            # Parse coordinates
            if ',' in coordinates:
                lat, lng = coordinates.split(',')
            else:
                lat, lng = coordinates.split()
            
            lat, lng = float(lat.strip()), float(lng.strip())
            
            # Simulate reverse geocoding
            reverse_data = {
                "latitude": lat,
                "longitude": lng,
                "formatted_address": "123 Sample St, Sample City, Sample State 12345",
                "country": "United States",
                "state": "Sample State",
                "city": "Sample City",
                "postal_code": "12345",
                "neighborhood": "Sample Neighborhood"
            }
            
            results.append(self.format_result(
                "reverse_geocoded",
                reverse_data,
                sub_module="reverse_geocoding",
                confidence=85,
                metadata={"service": "simulated_reverse_geocoding"}
            ))
            
            # Time zone information
            timezone_data = await self._get_timezone(lat, lng)
            if timezone_data:
                results.append(self.format_result(
                    "timezone_info",
                    timezone_data,
                    sub_module="timezone_lookup",
                    confidence=95,
                    metadata={"coordinates": f"{lat},{lng}"}
                ))
        
        except Exception as e:
            self.log_result(f"Reverse geocoding error: {e}")
        
        return results
    
    async def _geolocate_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Geolocate domain by resolving IP"""
        results = []
        
        try:
            # Resolve domain to IP
            ip = socket.gethostbyname(domain)
            
            # Get geolocation for the IP
            ip_results = await self._geolocate_ip(ip)
            
            # Add domain context to results
            for result in ip_results:
                result['data']['domain'] = domain
                result['data']['resolved_ip'] = ip
                result['sub_module'] = f"domain_{result['sub_module']}"
                results.append(result)
        
        except Exception as e:
            self.log_result(f"Domain geolocation error: {e}")
        
        return results
    
    async def _lookup_ip_geolocation(self, ip: str) -> Dict[str, Any]:
        """Lookup IP geolocation data"""
        # Simulated geolocation data
        return {
            "ip": ip,
            "country": "United States",
            "country_code": "US",
            "region": "New York",
            "region_code": "NY",
            "city": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
            "isp": "Sample ISP",
            "organization": "Sample Organization",
            "connection_type": "broadband",
            "accuracy_radius": 1000
        }
    
    async def _lookup_asn(self, ip: str) -> Dict[str, Any]:
        """Lookup ASN information"""
        return {
            "ip": ip,
            "asn": "AS12345",
            "asn_name": "SAMPLE-ASN",
            "asn_description": "Sample ASN Description",
            "asn_country": "US",
            "network": "192.168.0.0/16",
            "allocated_date": "2020-01-01"
        }
    
    async def _find_nearby_poi(self, lat: float, lng: float) -> Dict[str, Any]:
        """Find nearby points of interest"""
        return {
            "center_coordinates": {"latitude": lat, "longitude": lng},
            "search_radius": "1km",
            "poi_count": 5,
            "points_of_interest": [
                {
                    "name": "Sample Restaurant",
                    "type": "restaurant",
                    "distance": "200m",
                    "rating": 4.5
                },
                {
                    "name": "Sample Hotel",
                    "type": "lodging",
                    "distance": "500m",
                    "rating": 4.2
                },
                {
                    "name": "Sample Park",
                    "type": "park",
                    "distance": "800m",
                    "rating": 4.7
                }
            ]
        }
    
    async def _get_timezone(self, lat: float, lng: float) -> Dict[str, Any]:
        """Get timezone information for coordinates"""
        return {
            "latitude": lat,
            "longitude": lng,
            "timezone": "America/New_York",
            "utc_offset": "-05:00",
            "dst_offset": "-04:00",
            "timezone_name": "Eastern Standard Time",
            "current_time": "2023-01-01T12:00:00-05:00"
        }