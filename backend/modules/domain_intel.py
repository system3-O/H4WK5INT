import time
import logging
import ssl
import socket
import subprocess
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import json
import re

from utils.tor_proxy import make_tor_request

logger = logging.getLogger(__name__)

class DomainIntelligence:
    """Domain Intelligence module for domain and network analysis"""
    
    def __init__(self, use_tor: bool = True):
        """
        Initialize Domain Intelligence module
        
        Args:
            use_tor: Whether to use Tor proxy for requests
        """
        self.use_tor = use_tor
    
    def whois_lookup(self, domain: str) -> Dict[str, Any]:
        """
        Perform WHOIS lookup for domain
        
        Args:
            domain: Domain to lookup
            
        Returns:
            Dict containing WHOIS information
        """
        results = {
            'domain': domain,
            'whois_data': {},
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'name_servers': [],
            'registrant': {},
            'admin_contact': {},
            'tech_contact': {},
            'status': [],
            'timestamp': time.time()
        }
        
        try:
            import whois
            
            # Perform WHOIS lookup
            w = whois.whois(domain)
            
            # Extract basic information
            results['registrar'] = getattr(w, 'registrar', None)
            results['creation_date'] = str(getattr(w, 'creation_date', None))
            results['expiration_date'] = str(getattr(w, 'expiration_date', None))
            results['name_servers'] = getattr(w, 'name_servers', [])
            results['status'] = getattr(w, 'status', [])
            
            # Extract contact information (if available)
            results['registrant'] = {
                'name': getattr(w, 'name', None),
                'organization': getattr(w, 'org', None),
                'email': getattr(w, 'email', None),
                'country': getattr(w, 'country', None)
            }
            
            # Store raw WHOIS data
            results['whois_data'] = w
            results['success'] = True
            
        except Exception as e:
            logger.error(f"WHOIS lookup failed for {domain}: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def dns_enumeration(self, domain: str) -> Dict[str, Any]:
        """
        Perform comprehensive DNS enumeration
        
        Args:
            domain: Domain to enumerate
            
        Returns:
            Dict containing DNS records
        """
        results = {
            'domain': domain,
            'records': {},
            'timestamp': time.time()
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR']
        
        try:
            import dns.resolver
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    results['records'][record_type] = [str(rdata) for rdata in answers]
                except dns.resolver.NXDOMAIN:
                    results['records'][record_type] = []
                except dns.resolver.NoAnswer:
                    results['records'][record_type] = []
                except Exception as e:
                    results['records'][record_type] = {'error': str(e)}
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"DNS enumeration failed for {domain}: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def subdomain_discovery(self, domain: str, wordlist: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Discover subdomains using various techniques
        
        Args:
            domain: Domain to scan for subdomains
            wordlist: Custom subdomain wordlist
            
        Returns:
            Dict containing discovered subdomains
        """
        if wordlist is None:
            wordlist = self._get_default_subdomain_wordlist()
        
        results = {
            'domain': domain,
            'subdomains_found': [],
            'subdomains_tested': 0,
            'methods_used': [],
            'timestamp': time.time()
        }
        
        # Method 1: Brute force with wordlist
        brute_force_results = self._brute_force_subdomains(domain, wordlist)
        results['subdomains_found'].extend(brute_force_results)
        results['subdomains_tested'] += len(wordlist)
        results['methods_used'].append('brute_force')
        
        # Method 2: Certificate transparency logs
        ct_results = self._check_certificate_transparency(domain)
        results['subdomains_found'].extend(ct_results)
        results['methods_used'].append('certificate_transparency')
        
        # Method 3: Search engine dorking
        search_results = self._search_engine_subdomains(domain)
        results['subdomains_found'].extend(search_results)
        results['methods_used'].append('search_engines')
        
        # Remove duplicates and sort
        results['subdomains_found'] = sorted(list(set(results['subdomains_found'])))
        results['total_found'] = len(results['subdomains_found'])
        
        return results
    
    def ssl_analysis(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        Analyze SSL/TLS certificate and configuration
        
        Args:
            domain: Domain to analyze
            port: Port to connect to (default: 443)
            
        Returns:
            Dict containing SSL analysis results
        """
        results = {
            'domain': domain,
            'port': port,
            'certificate': {},
            'chain': [],
            'cipher_suites': [],
            'protocols': [],
            'vulnerabilities': [],
            'grade': None,
            'timestamp': time.time()
        }
        
        try:
            # Get certificate information
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Extract certificate details
                    results['certificate'] = {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert['version'],
                        'serial_number': cert['serialNumber'],
                        'not_before': cert['notBefore'],
                        'not_after': cert['notAfter'],
                        'signature_algorithm': cert.get('signatureAlgorithm'),
                        'subject_alt_names': [x[1] for x in cert.get('subjectAltName', [])]
                    }
                    
                    # Cipher information
                    if cipher:
                        results['cipher_suites'] = [{
                            'name': cipher[0],
                            'protocol': cipher[1],
                            'bits': cipher[2]
                        }]
                    
                    # Check for common vulnerabilities
                    results['vulnerabilities'] = self._check_ssl_vulnerabilities(domain, port)
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"SSL analysis failed for {domain}:{port}: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def port_scan(self, domain: str, ports: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Perform port scan on domain
        
        Args:
            domain: Domain to scan
            ports: List of ports to scan (if None, scans common ports)
            
        Returns:
            Dict containing port scan results
        """
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
        
        results = {
            'domain': domain,
            'open_ports': [],
            'closed_ports': [],
            'filtered_ports': [],
            'total_scanned': len(ports),
            'timestamp': time.time()
        }
        
        try:
            # Resolve domain to IP
            import socket
            ip = socket.gethostbyname(domain)
            results['ip_address'] = ip
            
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((ip, port))
                    
                    if result == 0:
                        # Try to grab banner
                        banner = self._grab_banner(ip, port)
                        results['open_ports'].append({
                            'port': port,
                            'service': self._identify_service(port),
                            'banner': banner
                        })
                    else:
                        results['closed_ports'].append(port)
                    
                    sock.close()
                    
                except Exception as e:
                    results['filtered_ports'].append({
                        'port': port,
                        'error': str(e)
                    })
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"Port scan failed for {domain}: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def technology_detection(self, domain: str) -> Dict[str, Any]:
        """
        Detect technologies used by domain
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dict containing detected technologies
        """
        results = {
            'domain': domain,
            'technologies': {},
            'web_server': None,
            'frameworks': [],
            'cms': None,
            'programming_languages': [],
            'analytics': [],
            'cdn': None,
            'timestamp': time.time()
        }
        
        try:
            url = f"https://{domain}"
            
            if self.use_tor:
                response = make_tor_request('GET', url, timeout=15)
            else:
                import requests
                response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                # Analyze headers
                headers = response.headers
                content = response.text
                
                # Web server detection
                server_header = headers.get('Server', '').lower()
                if 'nginx' in server_header:
                    results['web_server'] = 'Nginx'
                elif 'apache' in server_header:
                    results['web_server'] = 'Apache'
                elif 'iis' in server_header:
                    results['web_server'] = 'IIS'
                elif 'cloudflare' in server_header:
                    results['cdn'] = 'Cloudflare'
                
                # Framework detection from headers
                if 'X-Powered-By' in headers:
                    powered_by = headers['X-Powered-By']
                    results['frameworks'].append(powered_by)
                
                # Content analysis
                content_lower = content.lower()
                
                # CMS detection
                cms_signatures = {
                    'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
                    'drupal': ['drupal.js', 'drupal.css', '/sites/default/'],
                    'joomla': ['joomla', '/components/', '/modules/'],
                    'magento': ['magento', 'mage/cookies.js'],
                    'shopify': ['shopify', 'cdn.shopify.com']
                }
                
                for cms, signatures in cms_signatures.items():
                    if any(sig in content_lower for sig in signatures):
                        results['cms'] = cms.title()
                        break
                
                # Programming language detection
                lang_signatures = {
                    'php': ['.php', '<?php'],
                    'asp.net': ['__viewstate', 'asp.net'],
                    'java': ['.jsp', '.do'],
                    'python': ['django', 'flask'],
                    'ruby': ['ruby on rails', '.rb'],
                    'nodejs': ['node.js', 'express']
                }
                
                for lang, signatures in lang_signatures.items():
                    if any(sig in content_lower for sig in signatures):
                        results['programming_languages'].append(lang.upper())
                
                # Analytics detection
                analytics_signatures = {
                    'google_analytics': ['google-analytics.com', 'gtag'],
                    'google_tag_manager': ['googletagmanager.com'],
                    'facebook_pixel': ['facebook.net/en_us/fbevents.js'],
                    'hotjar': ['hotjar.com'],
                    'mixpanel': ['mixpanel.com']
                }
                
                for analytics, signatures in analytics_signatures.items():
                    if any(sig in content_lower for sig in signatures):
                        results['analytics'].append(analytics.replace('_', ' ').title())
                
                results['success'] = True
            
            else:
                results['error'] = f"HTTP {response.status_code}"
                results['success'] = False
        
        except Exception as e:
            logger.error(f"Technology detection failed for {domain}: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def _brute_force_subdomains(self, domain: str, wordlist: List[str]) -> List[str]:
        """Brute force subdomain discovery"""
        found_subdomains = []
        
        for subdomain in wordlist:
            try:
                test_domain = f"{subdomain}.{domain}"
                
                # Try to resolve
                import socket
                socket.gethostbyname(test_domain)
                found_subdomains.append(test_domain)
                
                # Small delay to avoid overwhelming DNS servers
                time.sleep(0.1)
                
            except socket.gaierror:
                # Subdomain doesn't exist
                pass
            except Exception as e:
                logger.debug(f"Error testing {subdomain}.{domain}: {e}")
        
        return found_subdomains
    
    def _check_certificate_transparency(self, domain: str) -> List[str]:
        """Check certificate transparency logs for subdomains"""
        subdomains = []
        
        try:
            # This would integrate with CT log APIs like crt.sh
            ct_url = f"https://crt.sh/?q=%.{domain}&output=json"
            
            if self.use_tor:
                response = make_tor_request('GET', ct_url, timeout=10)
            else:
                import requests
                response = requests.get(ct_url, timeout=10)
            
            if response.status_code == 200:
                certificates = response.json()
                
                for cert in certificates:
                    name_value = cert.get('name_value', '')
                    if name_value:
                        # Extract subdomains from certificate
                        names = name_value.split('\n')
                        for name in names:
                            name = name.strip()
                            if name.endswith(f'.{domain}') and name not in subdomains:
                                subdomains.append(name)
        
        except Exception as e:
            logger.warning(f"Certificate transparency check failed: {e}")
        
        return subdomains
    
    def _search_engine_subdomains(self, domain: str) -> List[str]:
        """Use search engines to find subdomains"""
        subdomains = []
        
        try:
            # Google dorking for subdomains
            search_query = f"site:*.{domain}"
            
            # This would require proper search engine API integration
            # For now, return empty list
            pass
        
        except Exception as e:
            logger.warning(f"Search engine subdomain discovery failed: {e}")
        
        return subdomains
    
    def _check_ssl_vulnerabilities(self, domain: str, port: int) -> List[str]:
        """Check for common SSL vulnerabilities"""
        vulnerabilities = []
        
        try:
            # This would integrate with tools like testssl.sh or custom checks
            # For now, return basic checks
            
            # Check for weak protocols (would need more sophisticated implementation)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Additional vulnerability checks would go here
            
        except Exception as e:
            logger.warning(f"SSL vulnerability check failed: {e}")
        
        return vulnerabilities
    
    def _grab_banner(self, ip: str, port: int) -> Optional[str]:
        """Grab service banner from open port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip, port))
            
            # Send HTTP request for web services
            if port in [80, 8080]:
                sock.send(b'GET / HTTP/1.1\r\nHost: ' + ip.encode() + b'\r\n\r\n')
            elif port in [443, 8443]:
                # For HTTPS, we'd need SSL context
                return None
            else:
                # For other services, just try to receive
                pass
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            return banner if banner else None
            
        except Exception:
            return None
    
    def _identify_service(self, port: int) -> str:
        """Identify common services by port number"""
        port_services = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            993: 'IMAPS',
            995: 'POP3S',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt'
        }
        
        return port_services.get(port, 'Unknown')
    
    def _get_default_subdomain_wordlist(self) -> List[str]:
        """Get default subdomain wordlist"""
        return [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'secure', 'vpn', 'mx',
            'email', 'cloud', 'api', 'test', 'dev', 'staging', 'admin', 'cdn', 'blog',
            'shop', 'store', 'support', 'help', 'portal', 'app', 'mobile', 'static',
            'assets', 'media', 'images', 'img', 'css', 'js', 'fonts', 'files', 'docs'
        ]

def run_domain_intel(operation: str, domain: str, **kwargs) -> Dict[str, Any]:
    """
    Run domain intelligence operation
    
    Args:
        operation: Type of operation to run
        domain: Target domain
        **kwargs: Additional parameters
        
    Returns:
        Dict containing operation results
    """
    domain_intel = DomainIntelligence(use_tor=kwargs.get('use_tor', True))
    
    try:
        if operation == 'whois_lookup':
            return domain_intel.whois_lookup(domain)
        
        elif operation == 'dns_enumeration':
            return domain_intel.dns_enumeration(domain)
        
        elif operation == 'subdomain_discovery':
            wordlist = kwargs.get('wordlist')
            return domain_intel.subdomain_discovery(domain, wordlist)
        
        elif operation == 'ssl_analysis':
            port = kwargs.get('port', 443)
            return domain_intel.ssl_analysis(domain, port)
        
        elif operation == 'port_scan':
            ports = kwargs.get('ports')
            return domain_intel.port_scan(domain, ports)
        
        elif operation == 'technology_detection':
            return domain_intel.technology_detection(domain)
        
        else:
            return {
                'error': f'Unknown operation: {operation}',
                'available_operations': [
                    'whois_lookup', 'dns_enumeration', 'subdomain_discovery',
                    'ssl_analysis', 'port_scan', 'technology_detection'
                ]
            }
    
    except Exception as e:
        logger.error(f"Domain intelligence operation failed: {e}")
        return {
            'error': str(e),
            'operation': operation,
            'domain': domain,
            'timestamp': time.time()
        }