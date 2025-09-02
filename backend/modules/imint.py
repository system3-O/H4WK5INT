from typing import List, Dict, Any
import os
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
import requests
from modules.base import BaseOSINTModule

class IMINTModule(BaseOSINTModule):
    """Image Intelligence Module"""
    
    async def run_investigation(self, image_url: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run IMINT investigation"""
        results = []
        analysis_types = options.get('analysis_types', ['reverse_search', 'metadata', 'faces'])
        
        self.log_result(f"Starting IMINT investigation for: {image_url}")
        
        # Download image for analysis
        image_path = await self._download_image(image_url)
        if not image_path:
            return results
        
        try:
            for analysis_type in analysis_types:
                if analysis_type == 'reverse_search':
                    results.extend(await self._reverse_image_search(image_url, image_path))
                elif analysis_type == 'metadata':
                    results.extend(await self._extract_metadata(image_path))
                elif analysis_type == 'faces':
                    results.extend(await self._detect_faces(image_path))
                elif analysis_type == 'objects':
                    results.extend(await self._detect_objects(image_path))
        
        finally:
            # Clean up downloaded image
            if os.path.exists(image_path):
                os.remove(image_path)
        
        return results
    
    async def _download_image(self, image_url: str) -> str:
        """Download image for analysis"""
        try:
            response = await self.make_request(image_url)
            if not response:
                return None
            
            # Create temp directory
            temp_dir = "/tmp/h4wk5int_images"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate filename based on URL hash
            url_hash = hashlib.md5(image_url.encode()).hexdigest()
            image_path = os.path.join(temp_dir, f"{url_hash}.jpg")
            
            # Download image using requests since we need binary content
            img_response = requests.get(image_url, stream=True)
            if img_response.status_code == 200:
                with open(image_path, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
                return image_path
            
            return None
            
        except Exception as e:
            self.log_result(f"Error downloading image: {e}")
            return None
    
    async def _reverse_image_search(self, image_url: str, image_path: str) -> List[Dict[str, Any]]:
        """Perform reverse image search"""
        results = []
        
        try:
            # Google reverse image search
            google_results = await self._google_reverse_search(image_url)
            if google_results:
                results.append(self.format_result(
                    "reverse_search",
                    google_results,
                    sub_module="google_images",
                    confidence=85,
                    source_url="https://images.google.com"
                ))
            
            # TinEye reverse search
            tineye_results = await self._tineye_search(image_url)
            if tineye_results:
                results.append(self.format_result(
                    "reverse_search",
                    tineye_results,
                    sub_module="tineye",
                    confidence=90,
                    source_url="https://tineye.com"
                ))
            
            # Yandex reverse search
            yandex_results = await self._yandex_reverse_search(image_url)
            if yandex_results:
                results.append(self.format_result(
                    "reverse_search",
                    yandex_results,
                    sub_module="yandex_images",
                    confidence=80,
                    source_url="https://yandex.com/images"
                ))
        
        except Exception as e:
            self.log_result(f"Error in reverse image search: {e}")
        
        return results
    
    async def _extract_metadata(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract EXIF metadata from image"""
        results = []
        
        try:
            with Image.open(image_path) as image:
                # Basic image info
                basic_info = {
                    "filename": os.path.basename(image_path),
                    "format": image.format,
                    "mode": image.mode,
                    "size": image.size,
                    "width": image.width,
                    "height": image.height
                }
                
                results.append(self.format_result(
                    "image_info",
                    basic_info,
                    sub_module="basic_metadata",
                    confidence=100,
                    metadata={"analysis_type": "basic_properties"}
                ))
                
                # EXIF data
                exif_data = {}
                if hasattr(image, '_getexif'):
                    exif = image._getexif()
                    if exif:
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                
                if exif_data:
                    # Extract GPS data if available
                    gps_info = self._extract_gps_data(exif_data)
                    if gps_info:
                        results.append(self.format_result(
                            "gps_location",
                            gps_info,
                            sub_module="exif_gps",
                            confidence=95,
                            metadata={"source": "exif_data"}
                        ))
                    
                    # Camera information
                    camera_info = self._extract_camera_info(exif_data)
                    if camera_info:
                        results.append(self.format_result(
                            "camera_info",
                            camera_info,
                            sub_module="exif_camera",
                            confidence=90,
                            metadata={"source": "exif_data"}
                        ))
                    
                    # Full EXIF data
                    results.append(self.format_result(
                        "exif_data",
                        exif_data,
                        sub_module="full_exif",
                        confidence=100,
                        metadata={"analysis_type": "complete_exif"}
                    ))
        
        except Exception as e:
            self.log_result(f"Error extracting metadata: {e}")
        
        return results
    
    async def _detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        results = []
        
        try:
            # Simulated face detection (would use OpenCV/face_recognition in real implementation)
            faces_detected = {
                "faces_count": 1,
                "faces": [
                    {
                        "face_id": 1,
                        "confidence": 0.95,
                        "coordinates": {"x": 100, "y": 150, "width": 200, "height": 250},
                        "estimated_age": "25-35",
                        "estimated_gender": "unknown",
                        "emotions": {"happy": 0.8, "neutral": 0.2}
                    }
                ],
                "analysis_method": "simulated"
            }
            
            results.append(self.format_result(
                "face_detection",
                faces_detected,
                sub_module="face_analysis",
                confidence=85,
                metadata={"analysis_type": "facial_recognition"}
            ))
        
        except Exception as e:
            self.log_result(f"Error detecting faces: {e}")
        
        return results
    
    async def _detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        results = []
        
        try:
            # Simulated object detection
            objects_detected = {
                "objects_count": 3,
                "objects": [
                    {"name": "person", "confidence": 0.92, "coordinates": {"x": 50, "y": 100, "width": 300, "height": 400}},
                    {"name": "car", "confidence": 0.87, "coordinates": {"x": 400, "y": 200, "width": 250, "height": 150}},
                    {"name": "building", "confidence": 0.76, "coordinates": {"x": 0, "y": 0, "width": 800, "height": 300}}
                ],
                "analysis_method": "simulated"
            }
            
            results.append(self.format_result(
                "object_detection",
                objects_detected,
                sub_module="object_analysis",
                confidence=80,
                metadata={"analysis_type": "object_recognition"}
            ))
        
        except Exception as e:
            self.log_result(f"Error detecting objects: {e}")
        
        return results
    
    async def _google_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """Perform Google reverse image search"""
        try:
            # Simulated Google reverse search results
            return {
                "search_url": f"https://images.google.com/searchbyimage?image_url={image_url}",
                "matches_found": 15,
                "similar_images": [
                    {"url": "https://example1.com/image1.jpg", "title": "Similar image 1"},
                    {"url": "https://example2.com/image2.jpg", "title": "Similar image 2"}
                ],
                "best_guess": "person in urban setting",
                "related_searches": ["city photography", "street portrait"]
            }
        except Exception as e:
            self.log_result(f"Error in Google reverse search: {e}")
            return None
    
    async def _tineye_search(self, image_url: str) -> Dict[str, Any]:
        """Perform TinEye reverse search"""
        try:
            # Simulated TinEye results
            return {
                "search_url": f"https://tineye.com/search?url={image_url}",
                "matches_found": 8,
                "results": [
                    {"url": "https://site1.com/page1", "domain": "site1.com", "crawl_date": "2023-01-15"},
                    {"url": "https://site2.com/page2", "domain": "site2.com", "crawl_date": "2023-02-20"}
                ],
                "oldest_match": "2022-06-10",
                "newest_match": "2023-02-20"
            }
        except Exception as e:
            self.log_result(f"Error in TinEye search: {e}")
            return None
    
    async def _yandex_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """Perform Yandex reverse image search"""
        try:
            # Simulated Yandex results
            return {
                "search_url": f"https://yandex.com/images/search?url={image_url}",
                "matches_found": 12,
                "similar_images": [
                    {"url": "https://example3.com/image3.jpg", "similarity": 0.95},
                    {"url": "https://example4.com/image4.jpg", "similarity": 0.87}
                ],
                "text_recognition": ["sample text", "street sign"],
                "location_suggestions": ["New York", "Urban area"]
            }
        except Exception as e:
            self.log_result(f"Error in Yandex search: {e}")
            return None
    
    def _extract_gps_data(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GPS coordinates from EXIF data"""
        gps_tags = ['GPSLatitude', 'GPSLongitude', 'GPSLatitudeRef', 'GPSLongitudeRef']
        
        if any(tag in exif_data for tag in gps_tags):
            return {
                "latitude": exif_data.get('GPSLatitude', 'Unknown'),
                "longitude": exif_data.get('GPSLongitude', 'Unknown'),
                "latitude_ref": exif_data.get('GPSLatitudeRef', 'Unknown'),
                "longitude_ref": exif_data.get('GPSLongitudeRef', 'Unknown'),
                "coordinates": "Coordinates available in EXIF"
            }
        return None
    
    def _extract_camera_info(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract camera information from EXIF data"""
        camera_tags = ['Make', 'Model', 'DateTime', 'Software', 'FNumber', 'ExposureTime', 'ISO']
        camera_info = {}
        
        for tag in camera_tags:
            if tag in exif_data:
                camera_info[tag.lower()] = exif_data[tag]
        
        return camera_info if camera_info else None