"""
Utility functions for the Moments Bot
"""
import re
from datetime import datetime, date
from typing import List, Optional

def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove or replace problematic characters
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text.strip()

def format_date(dt: datetime) -> str:
    """Format datetime for user display"""
    return dt.strftime("%B %d, %Y at %I:%M %p")

def format_date_short(dt: datetime) -> str:
    """Format datetime in short format"""
    return dt.strftime("%b %d, %Y")

def is_valid_spanish_text(text: str) -> bool:
    """Basic validation for Spanish text (very permissive)"""
    if not text or len(text.strip()) < 3:
        return False
    
    # Allow letters, numbers, spaces, and common Spanish punctuation
    spanish_pattern = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s\.,!?¿¡;:()\-\'\"]+$'
    return bool(re.match(spanish_pattern, text.strip()))

def extract_keywords(text: str) -> List[str]:
    """Extract potential keywords from text for tagging"""
    if not text:
        return []
    
    # Simple keyword extraction - split on whitespace and punctuation
    words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b', text.lower())
    
    # Filter out common words (basic stop words)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    # Return words longer than 3 characters that aren't stop words
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    # Return unique keywords, keeping original order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords[:10]  # Limit to 10 keywords

def estimate_text_difficulty(text: str) -> int:
    """Estimate the difficulty of Spanish text on a scale of 1-10"""
    if not text:
        return 1
    
    # Basic difficulty estimation based on various factors
    difficulty_score = 1
    
    # Length factor
    word_count = len(text.split())
    if word_count > 20:
        difficulty_score += 2
    elif word_count > 10:
        difficulty_score += 1
    
    # Sentence complexity (multiple sentences = higher difficulty)
    sentence_count = len([s for s in text.split('.') if s.strip()])
    if sentence_count > 3:
        difficulty_score += 2
    elif sentence_count > 1:
        difficulty_score += 1
    
    # Presence of complex punctuation
    complex_punctuation = [';', ':', '(', ')', '"', "'"]
    if any(punct in text for punct in complex_punctuation):
        difficulty_score += 1
    
    # Subjunctive mood indicators (common Spanish subjunctive triggers)
    subjunctive_triggers = ['que', 'ojalá', 'aunque', 'para que', 'sin que']
    if any(trigger in text.lower() for trigger in subjunctive_triggers):
        difficulty_score += 2
    
    # Complex verb forms (approximation)
    complex_verbs = ['habría', 'hubiese', 'hubiera', 'habiendo', 'hubiendo']
    if any(verb in text.lower() for verb in complex_verbs):
        difficulty_score += 2
    
    # Cap at 10
    return min(difficulty_score, 10)

def get_encouragement_message(difficulty: int) -> str:
    """Get an encouraging message based on difficulty level"""
    if difficulty <= 3:
        return "¡Excelente! Great job with this moment! 🌟"
    elif difficulty <= 6:
        return "¡Muy bien! You're making great progress! 💪"
    elif difficulty <= 8:
        return "¡Impresionante! That was challenging - well done! 🎉"
    else:
        return "¡Increíble! You tackled a complex moment - amazing work! 🏆"

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text for display purposes"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def is_today(dt: datetime) -> bool:
    """Check if a datetime is today"""
    return dt.date() == date.today()

def days_ago(dt: datetime) -> int:
    """Calculate how many days ago a datetime was"""
    return (date.today() - dt.date()).days

def format_relative_date(dt: datetime) -> str:
    """Format date relative to today (Today, Yesterday, 3 days ago, etc.)"""
    days = days_ago(dt)
    
    if days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        return format_date_short(dt)