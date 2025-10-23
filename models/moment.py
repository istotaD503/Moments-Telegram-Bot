"""
Data models for the Moments Bot
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

@dataclass
class Moment:
    """Data model for a user's moment entry"""
    
    id: str
    user_id: int
    timestamp: datetime
    english_text: str
    spanish_attempt: str = ""
    ai_correction: str = ""
    ai_explanation: str = ""
    difficulty_score: int = 0  # 1-10, 0 means not yet assessed
    vocabulary_learned: List[str] = None
    tags: List[str] = None
    is_completed: bool = False
    
    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.vocabulary_learned is None:
            self.vocabulary_learned = []
        if self.tags is None:
            self.tags = []
    
    @classmethod
    def create_new(cls, user_id: int, english_text: str) -> 'Moment':
        """Create a new moment with generated ID and current timestamp"""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            english_text=english_text,
            vocabulary_learned=[],
            tags=[]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert moment to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime to ISO string
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Moment':
        """Create moment from dictionary (for JSON deserialization)"""
        # Convert ISO string back to datetime
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
    
    def add_spanish_attempt(self, spanish_text: str) -> None:
        """Add the user's Spanish translation attempt"""
        self.spanish_attempt = spanish_text
    
    def add_ai_feedback(self, correction: str, explanation: str, difficulty: int = 0, vocabulary: List[str] = None) -> None:
        """Add AI feedback to the moment"""
        self.ai_correction = correction
        self.ai_explanation = explanation
        self.difficulty_score = difficulty
        if vocabulary:
            self.vocabulary_learned.extend(vocabulary)
        self.is_completed = True
    
    def get_summary(self) -> str:
        """Get a brief summary of the moment for display"""
        preview = self.english_text[:50] + "..." if len(self.english_text) > 50 else self.english_text
        status = "✅ Completed" if self.is_completed else "⏳ In Progress"
        return f"{status} | {self.timestamp.strftime('%b %d, %Y')} | {preview}"
    
    def get_detailed_view(self) -> str:
        """Get a detailed view of the moment for review"""
        lines = [
            f"📅 **{self.timestamp.strftime('%B %d, %Y at %I:%M %p')}**",
            "",
            "🇺🇸 **English:**",
            self.english_text,
            "",
            "🇪🇸 **Your Spanish:**",
            self.spanish_attempt or "_Not yet attempted_",
        ]
        
        if self.ai_correction:
            lines.extend([
                "",
                "✨ **AI Correction:**",
                self.ai_correction,
            ])
        
        if self.ai_explanation:
            lines.extend([
                "",
                "📚 **Explanation:**",
                self.ai_explanation,
            ])
        
        if self.difficulty_score > 0:
            lines.extend([
                "",
                f"📊 **Difficulty:** {self.difficulty_score}/10",
            ])
        
        if self.vocabulary_learned:
            vocab_text = ", ".join(self.vocabulary_learned)
            lines.extend([
                "",
                f"📝 **New Vocabulary:** {vocab_text}",
            ])
        
        return "\n".join(lines)

@dataclass
class UserStats:
    """Statistics for a user's learning progress"""
    
    user_id: int
    total_moments: int = 0
    completed_moments: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    vocabulary_count: int = 0
    average_difficulty: float = 0.0
    
    def update_from_moments(self, moments: List[Moment]) -> None:
        """Update stats based on current moments"""
        self.total_moments = len(moments)
        self.completed_moments = sum(1 for m in moments if m.is_completed)
        
        # Calculate vocabulary count
        all_vocab = set()
        difficulty_scores = []
        
        for moment in moments:
            if moment.is_completed:
                all_vocab.update(moment.vocabulary_learned)
                if moment.difficulty_score > 0:
                    difficulty_scores.append(moment.difficulty_score)
        
        self.vocabulary_count = len(all_vocab)
        self.average_difficulty = sum(difficulty_scores) / len(difficulty_scores) if difficulty_scores else 0.0
        
        # Calculate streak (simplified - counts consecutive days with moments)
        # This is a basic implementation; you might want to make it more sophisticated
        self.current_streak = self._calculate_current_streak(moments)
        self.longest_streak = max(self.current_streak, self.longest_streak)
    
    def _calculate_current_streak(self, moments: List[Moment]) -> int:
        """Calculate current consecutive days with moments"""
        if not moments:
            return 0
        
        # Group moments by date
        from collections import defaultdict
        dates_with_moments = defaultdict(int)
        
        for moment in moments:
            date_key = moment.timestamp.date()
            dates_with_moments[date_key] += 1
        
        # Calculate consecutive days from today backwards
        from datetime import date, timedelta
        current_date = date.today()
        streak = 0
        
        while current_date in dates_with_moments:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    def get_summary(self) -> str:
        """Get a formatted summary of user stats"""
        completion_rate = (self.completed_moments / self.total_moments * 100) if self.total_moments > 0 else 0
        
        return f"""📊 **Your Learning Stats**

📝 Total Moments: {self.total_moments}
✅ Completed: {self.completed_moments} ({completion_rate:.1f}%)
🔥 Current Streak: {self.current_streak} days
🏆 Longest Streak: {self.longest_streak} days
📚 Vocabulary Learned: {self.vocabulary_count} words
📈 Average Difficulty: {self.average_difficulty:.1f}/10"""