from typing import List, Dict, Any
import re
import json
from modules.base import BaseOSINTModule

class SOCMINTModule(BaseOSINTModule):
    """Social Media Intelligence Module"""
    
    async def run_investigation(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run SOCMINT investigation"""
        results = []
        platforms = options.get('platforms', ['twitter', 'facebook', 'instagram', 'linkedin'])
        
        self.log_result(f"Starting SOCMINT investigation for: {query}")
        
        for platform in platforms:
            platform_results = await self._search_platform(query, platform)
            results.extend(platform_results)
        
        return results
    
    async def _search_platform(self, query: str, platform: str) -> List[Dict[str, Any]]:
        """Search specific social media platform"""
        results = []
        
        if platform == 'twitter':
            results.extend(await self._search_twitter(query))
        elif platform == 'facebook':
            results.extend(await self._search_facebook(query))
        elif platform == 'instagram':
            results.extend(await self._search_instagram(query))
        elif platform == 'linkedin':
            results.extend(await self._search_linkedin(query))
        
        return results
    
    async def _search_twitter(self, query: str) -> List[Dict[str, Any]]:
        """Search Twitter for profiles and content"""
        results = []
        
        # Twitter profile search
        if '@' in query or self._is_username(query):
            username = query.replace('@', '')
            profile_data = await self._get_twitter_profile(username)
            if profile_data:
                results.append(self.format_result(
                    "profile",
                    profile_data,
                    sub_module="twitter_profile",
                    confidence=80,
                    source_url=f"https://twitter.com/{username}"
                ))
        
        # Twitter search for mentions
        search_results = await self._twitter_search(query)
        results.extend(search_results)
        
        return results
    
    async def _get_twitter_profile(self, username: str) -> Dict[str, Any]:
        """Get Twitter profile information"""
        try:
            # This would use Twitter API in a real implementation
            # For now, we'll simulate the data structure
            return {
                "username": username,
                "display_name": f"User {username}",
                "bio": "Sample bio",
                "followers_count": 100,
                "following_count": 50,
                "tweets_count": 200,
                "verified": False,
                "location": "Unknown",
                "created_at": "2020-01-01",
                "profile_image": f"https://twitter.com/{username}/profile_image"
            }
        except Exception as e:
            self.log_result(f"Error getting Twitter profile: {e}")
            return None
    
    async def _twitter_search(self, query: str) -> List[Dict[str, Any]]:
        """Search Twitter for content"""
        results = []
        
        try:
            # Simulate Twitter search results
            tweets = [
                {
                    "id": "123456789",
                    "text": f"Sample tweet mentioning {query}",
                    "author": "sample_user",
                    "created_at": "2023-01-01T12:00:00Z",
                    "retweets": 5,
                    "likes": 10,
                    "replies": 2
                }
            ]
            
            for tweet in tweets:
                results.append(self.format_result(
                    "tweet",
                    tweet,
                    sub_module="twitter_search",
                    confidence=70,
                    source_url=f"https://twitter.com/{tweet['author']}/status/{tweet['id']}"
                ))
        
        except Exception as e:
            self.log_result(f"Error searching Twitter: {e}")
        
        return results
    
    async def _search_facebook(self, query: str) -> List[Dict[str, Any]]:
        """Search Facebook for profiles and content"""
        results = []
        
        try:
            # Simulate Facebook search
            profile = {
                "name": f"Facebook User for {query}",
                "id": "123456789",
                "profile_url": f"https://facebook.com/profile/{query}",
                "location": "Unknown",
                "work": "Unknown",
                "education": "Unknown"
            }
            
            results.append(self.format_result(
                "profile",
                profile,
                sub_module="facebook_profile",
                confidence=60,
                source_url=profile["profile_url"]
            ))
        
        except Exception as e:
            self.log_result(f"Error searching Facebook: {e}")
        
        return results
    
    async def _search_instagram(self, query: str) -> List[Dict[str, Any]]:
        """Search Instagram for profiles and content"""
        results = []
        
        try:
            # Simulate Instagram search
            if self._is_username(query):
                profile = {
                    "username": query,
                    "full_name": f"Instagram User {query}",
                    "bio": "Sample Instagram bio",
                    "followers": 1000,
                    "following": 500,
                    "posts": 100,
                    "verified": False,
                    "profile_pic": f"https://instagram.com/{query}/profile.jpg"
                }
                
                results.append(self.format_result(
                    "profile",
                    profile,
                    sub_module="instagram_profile",
                    confidence=75,
                    source_url=f"https://instagram.com/{query}"
                ))
        
        except Exception as e:
            self.log_result(f"Error searching Instagram: {e}")
        
        return results
    
    async def _search_linkedin(self, query: str) -> List[Dict[str, Any]]:
        """Search LinkedIn for professional profiles"""
        results = []
        
        try:
            # Simulate LinkedIn search
            profile = {
                "name": f"LinkedIn User {query}",
                "headline": "Professional Title",
                "location": "City, Country", 
                "current_company": "Company Name",
                "education": "University Name",
                "connections": "500+",
                "profile_url": f"https://linkedin.com/in/{query}"
            }
            
            results.append(self.format_result(
                "profile",
                profile,
                sub_module="linkedin_profile",
                confidence=85,
                source_url=profile["profile_url"]
            ))
        
        except Exception as e:
            self.log_result(f"Error searching LinkedIn: {e}")
        
        return results
    
    def _is_username(self, query: str) -> bool:
        """Check if query looks like a username"""
        return bool(re.match(r'^[a-zA-Z0-9_]{3,30}$', query.replace('@', '')))