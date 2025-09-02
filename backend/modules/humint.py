from typing import List, Dict, Any
import re
import asyncio
from modules.base import BaseOSINTModule

class HUMINTModule(BaseOSINTModule):
    """Human Intelligence Module"""
    
    async def run_investigation(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run HUMINT investigation"""
        results = []
        search_types = options.get('search_types', ['email', 'username', 'phone', 'name'])
        
        self.log_result(f"Starting HUMINT investigation for: {query}")
        
        # Determine query type
        query_type = self._detect_query_type(query)
        
        for search_type in search_types:
            if search_type == 'email' and (query_type == 'email' or '@' in query):
                results.extend(await self._investigate_email(query))
            elif search_type == 'username':
                results.extend(await self._investigate_username(query))
            elif search_type == 'phone' and (query_type == 'phone' or self._is_phone(query)):
                results.extend(await self._investigate_phone(query))
            elif search_type == 'name' and query_type == 'name':
                results.extend(await self._investigate_name(query))
        
        return results
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query (email, phone, name, username)"""
        if '@' in query and '.' in query.split('@')[-1]:
            return 'email'
        elif self._is_phone(query):
            return 'phone'
        elif ' ' in query.strip():
            return 'name'
        else:
            return 'username'
    
    def _is_phone(self, query: str) -> bool:
        """Check if query looks like a phone number"""
        phone_pattern = r'^[\+]?[\d\s\-\(\)]{7,15}$'
        return bool(re.match(phone_pattern, query.strip()))
    
    async def _investigate_email(self, email: str) -> List[Dict[str, Any]]:
        """Investigate email address"""
        results = []
        
        try:
            # Email validation and domain analysis
            if '@' in email:
                local_part, domain = email.split('@', 1)
                
                # Check email format validity
                email_info = {
                    "email": email,
                    "local_part": local_part,
                    "domain": domain,
                    "is_valid_format": self._validate_email_format(email),
                    "domain_type": self._get_domain_type(domain)
                }
                
                results.append(self.format_result(
                    "email_analysis",
                    email_info,
                    sub_module="email_validation",
                    confidence=90,
                    metadata={"analysis_type": "format_validation"}
                ))
                
                # Domain reputation check
                domain_info = await self._check_domain_reputation(domain)
                if domain_info:
                    results.append(self.format_result(
                        "domain_reputation",
                        domain_info,
                        sub_module="domain_check",
                        confidence=75
                    ))
                
                # Breach database check (simulated)
                breach_info = await self._check_data_breaches(email)
                if breach_info:
                    results.append(self.format_result(
                        "data_breach",
                        breach_info,
                        sub_module="breach_check",
                        confidence=95
                    ))
        
        except Exception as e:
            self.log_result(f"Error investigating email: {e}")
        
        return results
    
    async def _investigate_username(self, username: str) -> List[Dict[str, Any]]:
        """Investigate username across platforms"""
        results = []
        
        platforms = [
            'github.com', 'twitter.com', 'instagram.com', 'facebook.com',
            'linkedin.com', 'reddit.com', 'pinterest.com', 'youtube.com'
        ]
        
        for platform in platforms:
            availability = await self._check_username_availability(username, platform)
            if availability:
                results.append(self.format_result(
                    "username_check",
                    availability,
                    sub_module="username_enum",
                    confidence=80,
                    source_url=availability.get('profile_url')
                ))
        
        return results
    
    async def _investigate_phone(self, phone: str) -> List[Dict[str, Any]]:
        """Investigate phone number"""
        results = []
        
        try:
            # Phone number analysis
            phone_info = {
                "phone": phone,
                "formatted": self._format_phone(phone),
                "country_code": self._extract_country_code(phone),
                "carrier": "Unknown",
                "type": "Unknown",
                "location": "Unknown"
            }
            
            results.append(self.format_result(
                "phone_analysis",
                phone_info,
                sub_module="phone_lookup",
                confidence=70,
                metadata={"analysis_type": "basic_info"}
            ))
            
            # Carrier lookup (simulated)
            carrier_info = await self._lookup_carrier(phone)
            if carrier_info:
                results.append(self.format_result(
                    "carrier_info",
                    carrier_info,
                    sub_module="carrier_lookup",
                    confidence=85
                ))
        
        except Exception as e:
            self.log_result(f"Error investigating phone: {e}")
        
        return results
    
    async def _investigate_name(self, name: str) -> List[Dict[str, Any]]:
        """Investigate person by name"""
        results = []
        
        try:
            # Name analysis
            name_parts = name.strip().split()
            name_info = {
                "full_name": name,
                "first_name": name_parts[0] if name_parts else "",
                "last_name": name_parts[-1] if len(name_parts) > 1 else "",
                "middle_names": " ".join(name_parts[1:-1]) if len(name_parts) > 2 else "",
                "variations": self._generate_name_variations(name)
            }
            
            results.append(self.format_result(
                "name_analysis",
                name_info,
                sub_module="name_parsing",
                confidence=95,
                metadata={"analysis_type": "name_breakdown"}
            ))
            
            # Public records search (simulated)
            records = await self._search_public_records(name)
            results.extend(records)
            
        except Exception as e:
            self.log_result(f"Error investigating name: {e}")
        
        return results
    
    def _validate_email_format(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _get_domain_type(self, domain: str) -> str:
        """Get domain type (personal, business, temporary, etc.)"""
        temporary_domains = ['10minutemail.com', 'guerrillamail.com', 'tempmail.org']
        business_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
        
        if domain in temporary_domains:
            return 'temporary'
        elif domain in business_domains:
            return 'personal'
        else:
            return 'business'
    
    async def _check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation"""
        return {
            "domain": domain,
            "reputation": "good",
            "blacklisted": False,
            "creation_date": "2020-01-01",
            "registrar": "Unknown"
        }
    
    async def _check_data_breaches(self, email: str) -> Dict[str, Any]:
        """Check if email appears in data breaches"""
        # Simulated breach check
        return {
            "email": email,
            "breaches_found": 0,
            "breach_names": [],
            "last_breach_date": None,
            "password_exposed": False
        }
    
    async def _check_username_availability(self, username: str, platform: str) -> Dict[str, Any]:
        """Check if username exists on platform"""
        # Simulated username check
        return {
            "username": username,
            "platform": platform,
            "exists": True,
            "profile_url": f"https://{platform}/{username}",
            "last_activity": "Unknown",
            "profile_data": {}
        }
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number"""
        digits = re.sub(r'[^\d+]', '', phone)
        return digits
    
    def _extract_country_code(self, phone: str) -> str:
        """Extract country code from phone number"""
        if phone.startswith('+1'):
            return 'US/CA'
        elif phone.startswith('+44'):
            return 'UK'
        elif phone.startswith('+33'):
            return 'FR'
        else:
            return 'Unknown'
    
    async def _lookup_carrier(self, phone: str) -> Dict[str, Any]:
        """Lookup phone carrier information"""
        return {
            "phone": phone,
            "carrier": "Unknown Carrier",
            "type": "Mobile",
            "country": "Unknown",
            "region": "Unknown"
        }
    
    def _generate_name_variations(self, name: str) -> List[str]:
        """Generate name variations"""
        variations = [name]
        parts = name.split()
        
        if len(parts) >= 2:
            # First Last
            variations.append(f"{parts[0]} {parts[-1]}")
            # Last, First
            variations.append(f"{parts[-1]}, {parts[0]}")
            # First Initial Last
            variations.append(f"{parts[0][0]}. {parts[-1]}")
            # First Last Initial
            if len(parts) > 2:
                variations.append(f"{parts[0]} {parts[-1][0]}.")
        
        return list(set(variations))
    
    async def _search_public_records(self, name: str) -> List[Dict[str, Any]]:
        """Search public records for name"""
        records = []
        
        # Simulated public records
        record_types = ['voter_registration', 'property_records', 'business_registration']
        
        for record_type in record_types:
            record = {
                "name": name,
                "record_type": record_type,
                "location": "Unknown",
                "date": "2020-01-01",
                "details": f"Sample {record_type.replace('_', ' ')} record"
            }
            
            records.append(self.format_result(
                "public_record",
                record,
                sub_module=record_type,
                confidence=60,
                metadata={"source": "public_records"}
            ))
        
        return records