#!/usr/bin/env python3
"""
Test script for Phase 1 implementation
Validates that all core functionality works correctly
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from config.settings import settings
        from models.moment import Moment, UserStats
        from services.storage import storage
        from handlers.commands import BasicCommandHandlers
        from handlers.conversation import MomentConversationHandler
        from utils.helpers import clean_text, estimate_text_difficulty
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_moment_creation():
    """Test moment creation and data model"""
    print("\n🧪 Testing moment creation...")
    
    try:
        from models.moment import Moment
        
        # Create a moment
        moment = Moment.create_new(
            user_id=99999,
            english_text="Today I discovered a new café and tried their amazing pastries."
        )
        
        assert moment.id is not None
        assert moment.user_id == 99999
        assert moment.english_text == "Today I discovered a new café and tried their amazing pastries."
        assert moment.spanish_attempt == ""
        assert moment.is_completed == False
        
        # Add Spanish attempt
        moment.add_spanish_attempt("Hoy descubrí una nueva cafetería y probé sus pasteles increíbles.")
        assert moment.spanish_attempt != ""
        
        # Test serialization
        moment_dict = moment.to_dict()
        assert isinstance(moment_dict['timestamp'], str)
        
        # Test deserialization
        restored_moment = Moment.from_dict(moment_dict)
        assert restored_moment.id == moment.id
        assert restored_moment.english_text == moment.english_text
        
        print("✅ Moment creation and serialization working")
        return True
    except Exception as e:
        print(f"❌ Moment creation error: {e}")
        return False

def test_storage():
    """Test storage functionality"""
    print("\n🧪 Testing storage functionality...")
    
    try:
        from models.moment import Moment
        from services.storage import storage
        
        # Create test moments
        test_user_id = 99999
        
        moment1 = Moment.create_new(test_user_id, "I had breakfast with my family.")
        moment1.add_spanish_attempt("Desayuné con mi familia.")
        
        moment2 = Moment.create_new(test_user_id, "I read an interesting book today.")
        moment2.add_spanish_attempt("Leí un libro interesante hoy.")
        
        # Test saving
        assert storage.save_moment(moment1) == True
        assert storage.save_moment(moment2) == True
        
        # Test loading
        moments = storage.get_moments(test_user_id)
        assert len(moments) == 2
        
        # Test searching
        search_results = storage.search_moments(test_user_id, "book")
        assert len(search_results) == 1
        assert "book" in search_results[0].english_text.lower()
        
        # Test stats
        stats = storage.get_user_stats(test_user_id)
        assert stats.total_moments == 2
        
        # Test export
        export_text = storage.export_moments(test_user_id, format='text')
        assert "breakfast" in export_text.lower()
        assert "book" in export_text.lower()
        
        # Clean up
        import os
        test_file = storage._get_user_file_path(test_user_id)
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("✅ Storage functionality working")
        return True
    except Exception as e:
        print(f"❌ Storage error: {e}")
        return False

def test_utilities():
    """Test utility functions"""
    print("\n🧪 Testing utility functions...")
    
    try:
        from utils.helpers import clean_text, estimate_text_difficulty, extract_keywords
        
        # Test text cleaning
        dirty_text = "  Hello   world!  \n\r  "
        clean = clean_text(dirty_text)
        assert clean == "Hello world!"
        
        # Test difficulty estimation
        simple_text = "Hola mundo"
        complex_text = "Aunque sea difícil, creo que deberíamos intentarlo para que podamos conseguir nuestros objetivos."
        
        simple_difficulty = estimate_text_difficulty(simple_text)
        complex_difficulty = estimate_text_difficulty(complex_text)
        assert complex_difficulty > simple_difficulty
        
        # Test keyword extraction
        keywords = extract_keywords("I went to the beautiful park and saw amazing flowers")
        assert "beautiful" in keywords
        assert "flowers" in keywords
        assert "the" not in keywords  # Stop word should be filtered
        
        print("✅ Utility functions working")
        return True
    except Exception as e:
        print(f"❌ Utility error: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config.settings import settings
        
        # Test default values
        assert settings.MAX_MOMENTS_PER_DAY > 0
        assert settings.CONVERSATION_TIMEOUT > 0
        assert settings.DATA_DIR == 'data'
        
        # Test path generation
        test_path = settings.get_moments_file_path(12345)
        assert "moments_12345.json" in test_path
        
        print("✅ Configuration working")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Phase 1 implementation tests...\n")
    
    tests = [
        test_imports,
        test_configuration,
        test_moment_creation,
        test_storage,
        test_utilities,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 1 implementation is ready.")
        print("\n🤖 Your Spanish Moments Bot is ready to use!")
        print("   1. Add your BOT_TOKEN to .env")
        print("   2. Run: python bot.py")
        print("   3. Start chatting with your bot!")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)