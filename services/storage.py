"""
Storage service for persisting moments to JSON files
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging

from models.moment import Moment, UserStats
from config.settings import settings

logger = logging.getLogger(__name__)

class StorageService:
    """Handles persistence of moments to JSON files"""
    
    def __init__(self):
        """Initialize storage service and ensure data directory exists"""
        self.data_dir = settings.DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_user_file_path(self, user_id: int) -> str:
        """Get the file path for a user's moments"""
        return settings.get_moments_file_path(user_id)
    
    def _load_user_data(self, user_id: int) -> Dict[str, Any]:
        """Load user data from JSON file"""
        file_path = self._get_user_file_path(user_id)
        
        if not os.path.exists(file_path):
            return {"moments": [], "user_id": user_id, "created_at": datetime.now().isoformat()}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading user data for {user_id}: {e}")
            return {"moments": [], "user_id": user_id, "created_at": datetime.now().isoformat()}
    
    def _save_user_data(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Save user data to JSON file"""
        file_path = self._get_user_file_path(user_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving user data for {user_id}: {e}")
            return False
    
    def save_moment(self, moment: Moment) -> bool:
        """Save a single moment"""
        try:
            user_data = self._load_user_data(moment.user_id)
            
            # Check if moment already exists (update) or is new (add)
            moment_dict = moment.to_dict()
            existing_index = None
            
            for i, existing_moment in enumerate(user_data["moments"]):
                if existing_moment.get("id") == moment.id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                user_data["moments"][existing_index] = moment_dict
                logger.info(f"Updated moment {moment.id} for user {moment.user_id}")
            else:
                user_data["moments"].append(moment_dict)
                logger.info(f"Added new moment {moment.id} for user {moment.user_id}")
            
            # Update metadata
            user_data["last_updated"] = datetime.now().isoformat()
            
            return self._save_user_data(moment.user_id, user_data)
            
        except Exception as e:
            logger.error(f"Error saving moment {moment.id}: {e}")
            return False
    
    def get_moments(self, user_id: int, limit: Optional[int] = None) -> List[Moment]:
        """Get all moments for a user, optionally limited"""
        try:
            user_data = self._load_user_data(user_id)
            moments = []
            
            for moment_dict in user_data["moments"]:
                try:
                    moment = Moment.from_dict(moment_dict)
                    moments.append(moment)
                except Exception as e:
                    logger.warning(f"Skipping invalid moment data: {e}")
                    continue
            
            # Sort by timestamp (most recent first)
            moments.sort(key=lambda m: m.timestamp, reverse=True)
            
            if limit:
                moments = moments[:limit]
            
            return moments
            
        except Exception as e:
            logger.error(f"Error loading moments for user {user_id}: {e}")
            return []
    
    def get_moment_by_id(self, user_id: int, moment_id: str) -> Optional[Moment]:
        """Get a specific moment by ID"""
        moments = self.get_moments(user_id)
        for moment in moments:
            if moment.id == moment_id:
                return moment
        return None
    
    def delete_moment(self, user_id: int, moment_id: str) -> bool:
        """Delete a specific moment"""
        try:
            user_data = self._load_user_data(user_id)
            
            # Find and remove the moment
            original_count = len(user_data["moments"])
            user_data["moments"] = [
                m for m in user_data["moments"] 
                if m.get("id") != moment_id
            ]
            
            if len(user_data["moments"]) < original_count:
                user_data["last_updated"] = datetime.now().isoformat()
                success = self._save_user_data(user_id, user_data)
                if success:
                    logger.info(f"Deleted moment {moment_id} for user {user_id}")
                return success
            else:
                logger.warning(f"Moment {moment_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting moment {moment_id}: {e}")
            return False
    
    def get_moments_by_date(self, user_id: int, target_date: date) -> List[Moment]:
        """Get all moments for a specific date"""
        all_moments = self.get_moments(user_id)
        return [
            moment for moment in all_moments
            if moment.timestamp.date() == target_date
        ]
    
    def get_recent_moments(self, user_id: int, days: int = 7) -> List[Moment]:
        """Get moments from the last N days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        all_moments = self.get_moments(user_id)
        
        return [
            moment for moment in all_moments
            if moment.timestamp >= cutoff_date
        ]
    
    def search_moments(self, user_id: int, query: str) -> List[Moment]:
        """Search moments by text content"""
        all_moments = self.get_moments(user_id)
        query_lower = query.lower()
        
        matching_moments = []
        for moment in all_moments:
            # Search in English text, Spanish attempt, and AI correction
            searchable_text = " ".join([
                moment.english_text,
                moment.spanish_attempt,
                moment.ai_correction
            ]).lower()
            
            if query_lower in searchable_text:
                matching_moments.append(moment)
        
        return matching_moments
    
    def get_user_stats(self, user_id: int) -> UserStats:
        """Get statistics for a user"""
        moments = self.get_moments(user_id)
        stats = UserStats(user_id=user_id)
        stats.update_from_moments(moments)
        return stats
    
    def get_incomplete_moments(self, user_id: int) -> List[Moment]:
        """Get moments that haven't been completed yet"""
        all_moments = self.get_moments(user_id)
        return [moment for moment in all_moments if not moment.is_completed]
    
    def export_moments(self, user_id: int, format: str = 'json') -> str:
        """Export all moments for a user in specified format"""
        moments = self.get_moments(user_id)
        
        if format.lower() == 'json':
            return json.dumps([moment.to_dict() for moment in moments], indent=2, ensure_ascii=False)
        
        elif format.lower() == 'text':
            lines = [f"Moments Export for User {user_id}", "=" * 50, ""]
            
            for moment in moments:
                lines.append(moment.get_detailed_view())
                lines.append("\n" + "-" * 50 + "\n")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def backup_user_data(self, user_id: int) -> Optional[str]:
        """Create a backup copy of user data and return the backup file path"""
        try:
            from datetime import datetime
            
            original_file = self._get_user_file_path(user_id)
            if not os.path.exists(original_file):
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"moments_{user_id}_backup_{timestamp}.json"
            backup_path = os.path.join(self.data_dir, backup_filename)
            
            import shutil
            shutil.copy2(original_file, backup_path)
            
            logger.info(f"Created backup for user {user_id} at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup for user {user_id}: {e}")
            return None

# Global storage service instance
storage = StorageService()