import re
import time
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, quote
import json
from email_validator import validate_email, EmailNotValidError

from utils.tor_proxy import make_tor_request

logger = logging.getLogger(__name__)

class PeopleIntelligence:
    """People Intelligence (PEOPINT) module for user information gathering"""
    
    def __init__(self, use_tor: bool = True):
        """
        Initialize People Intelligence module
        
        Args:
            use_tor: Whether to use Tor proxy for requests
        """
        self.use_tor = use_tor
        self.results = {}
    
    def username_enumeration(self, username: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enumerate username across multiple social media platforms
        
        Args:
            username: Username to search for
            platforms: List of platforms to check (if None, checks all)
            
        Returns:
            Dict containing enumeration results
        """
        if platforms is None:
            platforms = [
                'github', 'twitter', 'instagram', 'facebook', 'linkedin',
                'reddit', 'youtube', 'pinterest', 'tiktok', 'snapchat'
            ]
        
        results = {
            'username': username,
            'platforms_found': [],
            'platforms_not_found': [],
            'platforms_uncertain': [],
            'total_checked': 0,
            'timestamp': time.time()
        }
        
        platform_urls = {
            'github': f'https://github.com/{username}',
            'twitter': f'https://twitter.com/{username}',
            'instagram': f'https://instagram.com/{username}',
            'facebook': f'https://facebook.com/{username}',
            'linkedin': f'https://linkedin.com/in/{username}',
            'reddit': f'https://reddit.com/user/{username}',
            'youtube': f'https://youtube.com/@{username}',
            'pinterest': f'https://pinterest.com/{username}',
            'tiktok': f'https://tiktok.com/@{username}',
            'snapchat': f'https://snapchat.com/add/{username}'
        }
        
        for platform in platforms:
            if platform not in platform_urls:
                continue
                
            try:
                url = platform_urls[platform]
                
                if self.use_tor:
                    response = make_tor_request('GET', url, timeout=10)
                else:
                    import requests
                    response = requests.get(url, timeout=10)
                
                results['total_checked'] += 1
                
                # Analyze response to determine if profile exists
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Platform-specific detection logic
                    if platform == 'github':
                        if 'not found' in content or '404' in content:
                            results['platforms_not_found'].append(platform)
                        else:
                            results['platforms_found'].append({
                                'platform': platform,
                                'url': url,
                                'status': 'found'
                            })
                    
                    elif platform == 'twitter':
                        if 'this account doesn\'t exist' in content or 'account suspended' in content:
                            results['platforms_not_found'].append(platform)
                        else:
                            results['platforms_found'].append({
                                'platform': platform,
                                'url': url,
                                'status': 'found'
                            })
                    
                    elif platform == 'instagram':
                        if 'sorry, this page isn\'t available' in content:
                            results['platforms_not_found'].append(platform)
                        else:
                            results['platforms_found'].append({
                                'platform': platform,
                                'url': url,
                                'status': 'found'
                            })
                    
                    else:
                        # Generic detection for other platforms
                        not_found_indicators = [
                            'not found', '404', 'page not found', 'user not found',
                            'profile not found', 'doesn\'t exist'
                        ]
                        
                        if any(indicator in content for indicator in not_found_indicators):
                            results['platforms_not_found'].append(platform)
                        else:
                            results['platforms_found'].append({
                                'platform': platform,
                                'url': url,
                                'status': 'found'
                            })
                
                elif response.status_code == 404:
                    results['platforms_not_found'].append(platform)
                else:
                    results['platforms_uncertain'].append({
                        'platform': platform,
                        'status_code': response.status_code,
                        'reason': 'unexpected_response'
                    })
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error checking {platform}: {e}")
                results['platforms_uncertain'].append({
                    'platform': platform,
                    'error': str(e),
                    'reason': 'request_failed'
                })
        
        return results
    
    def email_validation(self, email: str) -> Dict[str, Any]:
        """
        Validate email address and check for breaches
        
        Args:
            email: Email address to validate
            
        Returns:
            Dict containing validation results
        """
        results = {
            'email': email,
            'valid': False,
            'format_valid': False,
            'domain_exists': False,
            'mx_records': [],
            'disposable': False,
            'breach_check': None,
            'timestamp': time.time()
        }
        
        try:
            # Basic format validation
            validate_email(email)
            results['format_valid'] = True
            
            # Extract domain
            domain = email.split('@')[1]
            
            # DNS MX record check
            try:
                import dns.resolver
                mx_records = dns.resolver.resolve(domain, 'MX')
                results['mx_records'] = [str(mx) for mx in mx_records]
                results['domain_exists'] = len(results['mx_records']) > 0
            except Exception as e:
                logger.warning(f"MX record lookup failed for {domain}: {e}")
            
            # Check if it's a disposable email
            disposable_domains = self._get_disposable_domains()
            results['disposable'] = domain.lower() in disposable_domains
            
            # Overall validity
            results['valid'] = results['format_valid'] and results['domain_exists'] and not results['disposable']
            
            # Breach check (simplified - in production, use HaveIBeenPwned API)
            results['breach_check'] = self._check_email_breaches(email)
            
        except EmailNotValidError as e:
            results['format_valid'] = False
            results['error'] = str(e)
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            results['error'] = str(e)
        
        return results
    
    def phone_lookup(self, phone: str, country_code: str = None) -> Dict[str, Any]:
        """
        Lookup phone number information
        
        Args:
            phone: Phone number to lookup
            country_code: Optional country code (e.g., 'US', 'GB')
            
        Returns:
            Dict containing phone lookup results
        """
        results = {
            'phone': phone,
            'formatted': None,
            'valid': False,
            'country': None,
            'carrier': None,
            'line_type': None,
            'location': None,
            'timestamp': time.time()
        }
        
        try:
            # Basic phone number parsing and validation
            import phonenumbers
            from phonenumbers import geocoder, carrier
            
            # Parse phone number
            if country_code:
                parsed = phonenumbers.parse(phone, country_code)
            else:
                parsed = phonenumbers.parse(phone, None)
            
            # Validate
            results['valid'] = phonenumbers.is_valid_number(parsed)
            
            if results['valid']:
                # Format number
                results['formatted'] = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
                
                # Get country
                results['country'] = geocoder.country_name_for_number(parsed, 'en')
                
                # Get carrier (may not work for all numbers)
                try:
                    results['carrier'] = carrier.name_for_number(parsed, 'en')
                except:
                    pass
                
                # Get location
                try:
                    results['location'] = geocoder.description_for_number(parsed, 'en')
                except:
                    pass
                
                # Determine line type
                number_type = phonenumbers.number_type(parsed)
                type_map = {
                    phonenumbers.PhoneNumberType.MOBILE: 'mobile',
                    phonenumbers.PhoneNumberType.FIXED_LINE: 'landline',
                    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'landline_or_mobile',
                    phonenumbers.PhoneNumberType.TOLL_FREE: 'toll_free',
                    phonenumbers.PhoneNumberType.PREMIUM_RATE: 'premium_rate',
                    phonenumbers.PhoneNumberType.VOIP: 'voip'
                }
                results['line_type'] = type_map.get(number_type, 'unknown')
        
        except Exception as e:
            logger.warning(f"Phone lookup error: {e}")
            results['error'] = str(e)
        
        return results
    
    def social_media_search(self, query: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for profiles and content across social media platforms
        
        Args:
            query: Search query (name, email, username, etc.)
            platforms: List of platforms to search
            
        Returns:
            Dict containing search results
        """
        if platforms is None:
            platforms = ['twitter', 'instagram', 'facebook', 'linkedin']
        
        results = {
            'query': query,
            'platforms_searched': [],
            'profiles_found': [],
            'total_results': 0,
            'timestamp': time.time()
        }
        
        for platform in platforms:
            try:
                platform_results = self._search_platform(platform, query)
                results['platforms_searched'].append(platform)
                
                if platform_results:
                    results['profiles_found'].extend(platform_results)
                    results['total_results'] += len(platform_results)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"Error searching {platform}: {e}")
        
        return results
    
    def _search_platform(self, platform: str, query: str) -> List[Dict[str, Any]]:
        """
        Search specific platform for profiles
        
        Args:
            platform: Platform name
            query: Search query
            
        Returns:
            List of found profiles
        """
        profiles = []
        
        try:
            if platform == 'twitter':
                # Twitter search would require API access
                # This is a simplified example
                search_url = f"https://twitter.com/search?q={quote(query)}"
                
                if self.use_tor:
                    response = make_tor_request('GET', search_url, timeout=10)
                else:
                    import requests
                    response = requests.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    # Parse response to extract profile information
                    # This would require proper HTML parsing in production
                    profiles.append({
                        'platform': platform,
                        'url': search_url,
                        'query': query,
                        'status': 'search_completed'
                    })
            
            # Similar logic for other platforms...
            
        except Exception as e:
            logger.warning(f"Platform search error for {platform}: {e}")
        
        return profiles
    
    def _get_disposable_domains(self) -> set:
        """Get list of disposable email domains"""
        # This would typically be loaded from a database or external service
        return {
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'throwaway.email', 'yopmail.com'
        }
    
    def _check_email_breaches(self, email: str) -> Dict[str, Any]:
        """
        Check if email appears in known data breaches
        
        Args:
            email: Email to check
            
        Returns:
            Dict containing breach information
        """
        # This would integrate with HaveIBeenPwned API or similar service
        # For now, return a placeholder
        return {
            'checked': True,
            'breaches_found': 0,
            'paste_count': 0,
            'note': 'Breach checking not implemented - integrate with HaveIBeenPwned API'
        }

def run_people_intel(operation: str, query: str, **kwargs) -> Dict[str, Any]:
    """
    Run people intelligence operation
    
    Args:
        operation: Type of operation to run
        query: Target query
        **kwargs: Additional parameters
        
    Returns:
        Dict containing operation results
    """
    peopint = PeopleIntelligence(use_tor=kwargs.get('use_tor', True))
    
    try:
        if operation == 'username_enumeration':
            platforms = kwargs.get('platforms')
            return peopint.username_enumeration(query, platforms)
        
        elif operation == 'email_validation':
            return peopint.email_validation(query)
        
        elif operation == 'phone_lookup':
            country_code = kwargs.get('country_code')
            return peopint.phone_lookup(query, country_code)
        
        elif operation == 'social_media_search':
            platforms = kwargs.get('platforms')
            return peopint.social_media_search(query, platforms)
        
        else:
            return {
                'error': f'Unknown operation: {operation}',
                'available_operations': [
                    'username_enumeration', 'email_validation', 
                    'phone_lookup', 'social_media_search'
                ]
            }
    
    except Exception as e:
        logger.error(f"People intelligence operation failed: {e}")
        return {
            'error': str(e),
            'operation': operation,
            'query': query,
            'timestamp': time.time()
        }