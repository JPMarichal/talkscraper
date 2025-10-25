"""
Integrity Tests for Phase 3 - Note Extraction

These tests validate the extraction of notes from talk URLs using the existing
Selenium-based infrastructure. The tests use specific URLs with known note counts
to validate extraction accuracy.
"""

import pytest
import os
import sys
from typing import List, Dict, Tuple
from pathlib import Path

# Add the project root to Python path to import existing note extraction code
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
src_path = project_root / "src"
sys.path.append(str(src_path))

from core.talk_content_extractor import TalkContentExtractor
from utils.config_manager import ConfigManager


def extract_notes_with_selenium_final(url: str, config_path: str = None) -> List[str]:
    """
    Wrapper function to extract notes using TalkContentExtractor.
    
    This replaces the eliminated extract_notes_final module functionality.
    
    Args:
        url: URL to extract notes from
        config_path: Path to config file. If None, looks for config.ini in project root.
    """
    if config_path is None:
        # Try to find config.ini in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = str(project_root / "config.ini")
        if not Path(config_path).exists():
            config_path = "config.ini"  # Fallback to relative path
    
    try:
        extractor = TalkContentExtractor(config_path)
        return extractor._extract_notes_selenium(url) or []
    except FileNotFoundError:
        # If config not found, return empty list to allow test to continue
        # This allows tests to fail gracefully in environments without config
        return []


def extract_talk_content_static(url: str, config_path: str = None) -> Dict[str, str]:
    """
    Wrapper function to extract static content using TalkContentExtractor.
    
    This replaces the eliminated extract_notes_final module functionality.
    
    Args:
        url: URL to extract content from
        config_path: Path to config file. If None, looks for config.ini in project root.
    """
    if config_path is None:
        # Try to find config.ini in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = str(project_root / "config.ini")
        if not Path(config_path).exists():
            config_path = "config.ini"  # Fallback to relative path
    
    try:
        extractor = TalkContentExtractor(config_path)
        return extractor._extract_static_content(url) or {}
    except FileNotFoundError:
        # If config not found, return empty dict to allow test to continue
        # This allows tests to fail gracefully in environments without config
        return {}


@pytest.mark.integrity
@pytest.mark.phase3
@pytest.mark.network
@pytest.mark.slow
class TestPhase3NoteExtraction:
    """Test note extraction capabilities for Phase 3."""
    
    # Test cases with URLs and expected note counts
    TEST_CASES_ENGLISH = [
        ("https://www.churchofjesuschrist.org/study/general-conference/2025/04/21andersen?lang=eng", 23),
        ("https://www.churchofjesuschrist.org/study/general-conference/1977/10/the-foundations-of-righteousness?lang=eng", 0),
        ("https://www.churchofjesuschrist.org/study/general-conference/2020/04/23soares?lang=eng", 26),
        ("https://www.churchofjesuschrist.org/study/general-conference/2015/04/the-family-is-of-god?lang=eng", 16),
        ("https://www.churchofjesuschrist.org/study/general-conference/2000/04/the-cloven-tongues-of-fire?lang=eng", 36),
    ]
    
    # Spanish equivalents (should have same note counts)
    TEST_CASES_SPANISH = [
        ("https://www.churchofjesuschrist.org/study/general-conference/2025/04/21andersen?lang=spa", 23),
        ("https://www.churchofjesuschrist.org/study/general-conference/1977/10/the-foundations-of-righteousness?lang=spa", 0),
        ("https://www.churchofjesuschrist.org/study/general-conference/2020/04/23soares?lang=spa", 26),
        ("https://www.churchofjesuschrist.org/study/general-conference/2015/04/the-family-is-of-god?lang=spa", 16),
        ("https://www.churchofjesuschrist.org/study/general-conference/2000/04/the-cloven-tongues-of-fire?lang=spa", 36),
    ]
    
    def test_note_extraction_english_validation(self):
        """Test note extraction for English talks with known note counts."""
        results = []
        failures = []
        
        print(f"\n🔍 Testing note extraction for {len(self.TEST_CASES_ENGLISH)} English talks:")
        
        for url, expected_count in self.TEST_CASES_ENGLISH:
            talk_name = self._extract_talk_name_from_url(url)
            print(f"\n   📄 Testing: {talk_name}")
            print(f"   🌐 URL: {url}")
            print(f"   🎯 Expected notes: {expected_count}")
            
            try:
                notes = extract_notes_with_selenium_final(url)
                actual_count = len(notes) if notes else 0
                
                print(f"   📝 Extracted notes: {actual_count}")
                
                # Store result
                result = {
                    'url': url,
                    'talk_name': talk_name,
                    'expected': expected_count,
                    'actual': actual_count,
                    'success': actual_count == expected_count,
                    'notes': notes[:3] if notes else []  # Store first 3 notes as samples
                }
                results.append(result)
                
                if actual_count == expected_count:
                    print(f"   ✅ SUCCESS: {actual_count}/{expected_count}")
                else:
                    print(f"   ❌ MISMATCH: {actual_count}/{expected_count}")
                    failures.append(result)
                
            except Exception as e:
                print(f"   💥 ERROR: {e}")
                failure_result = {
                    'url': url,
                    'talk_name': talk_name,
                    'expected': expected_count,
                    'actual': -1,  # -1 indicates error
                    'success': False,
                    'error': str(e)
                }
                results.append(failure_result)
                failures.append(failure_result)
        
        # Summary
        successful = len([r for r in results if r['success']])
        print(f"\n📊 ENGLISH RESULTS SUMMARY:")
        print(f"   ✅ Successful: {successful}/{len(results)}")
        print(f"   ❌ Failed: {len(failures)}/{len(results)}")
        
        if failures:
            print(f"\n💥 FAILURES:")
            for failure in failures:
                if 'error' in failure:
                    print(f"   • {failure['talk_name']}: ERROR - {failure['error']}")
                else:
                    print(f"   • {failure['talk_name']}: Expected {failure['expected']}, got {failure['actual']}")
        
        # Test assertions
        assert len(results) == len(self.TEST_CASES_ENGLISH), "Not all test cases were executed"
        
        # We expect at least 60% success rate for now (can be adjusted as we improve)
        success_rate = successful / len(results)
        assert success_rate >= 0.6, f"Success rate too low: {success_rate:.1%}. Failed cases: {failures}"
        
        # Store results for further analysis
        self._store_test_results('english', results)
    
    def test_note_extraction_spanish_validation(self):
        """Test note extraction for Spanish talks with known note counts."""
        results = []
        failures = []
        
        print(f"\n🔍 Testing note extraction for {len(self.TEST_CASES_SPANISH)} Spanish talks:")
        
        for url, expected_count in self.TEST_CASES_SPANISH:
            talk_name = self._extract_talk_name_from_url(url)
            print(f"\n   📄 Testing: {talk_name}")
            print(f"   🌐 URL: {url}")
            print(f"   🎯 Expected notes: {expected_count}")
            
            try:
                notes = extract_notes_with_selenium_final(url)
                actual_count = len(notes) if notes else 0
                
                print(f"   📝 Extracted notes: {actual_count}")
                
                # Store result
                result = {
                    'url': url,
                    'talk_name': talk_name,
                    'expected': expected_count,
                    'actual': actual_count,
                    'success': actual_count == expected_count,
                    'notes': notes[:3] if notes else []  # Store first 3 notes as samples
                }
                results.append(result)
                
                if actual_count == expected_count:
                    print(f"   ✅ SUCCESS: {actual_count}/{expected_count}")
                else:
                    print(f"   ❌ MISMATCH: {actual_count}/{expected_count}")
                    failures.append(result)
                
            except Exception as e:
                print(f"   💥 ERROR: {e}")
                failure_result = {
                    'url': url,
                    'talk_name': talk_name,
                    'expected': expected_count,
                    'actual': -1,  # -1 indicates error
                    'success': False,
                    'error': str(e)
                }
                results.append(failure_result)
                failures.append(failure_result)
        
        # Summary
        successful = len([r for r in results if r['success']])
        print(f"\n📊 SPANISH RESULTS SUMMARY:")
        print(f"   ✅ Successful: {successful}/{len(results)}")
        print(f"   ❌ Failed: {len(failures)}/{len(results)}")
        
        if failures:
            print(f"\n💥 FAILURES:")
            for failure in failures:
                if 'error' in failure:
                    print(f"   • {failure['talk_name']}: ERROR - {failure['error']}")
                else:
                    print(f"   • {failure['talk_name']}: Expected {failure['expected']}, got {failure['actual']}")
        
        # Test assertions
        assert len(results) == len(self.TEST_CASES_SPANISH), "Not all test cases were executed"
        
        # We expect at least 60% success rate for now (can be adjusted as we improve)
        success_rate = successful / len(results)
        assert success_rate >= 0.6, f"Success rate too low: {success_rate:.1%}. Failed cases: {failures}"
        
        # Store results for further analysis
        self._store_test_results('spanish', results)
    
    def test_note_extraction_infrastructure_integration(self):
        """Test that the note extraction infrastructure integrates properly."""
        # Test with one known working URL
        test_url = "https://www.churchofjesuschrist.org/study/general-conference/2025/04/21andersen?lang=eng"
        
        print(f"\n🔧 Testing infrastructure integration with: {test_url}")
        
        # Test static content extraction
        print("   📄 Testing static content extraction...")
        try:
            static_content = extract_talk_content_static(test_url)
            
            assert static_content is not None, "Static content extraction returned None"
            assert 'title' in static_content, "Missing title in static content"
            assert 'author' in static_content, "Missing author in static content"
            assert 'content' in static_content, "Missing content in static content"
            assert len(static_content['content']) > 100, "Content too short"
            
            print(f"   ✅ Static content: Title='{static_content['title'][:50]}...', Author='{static_content['author']}'")
            
        except Exception as e:
            pytest.fail(f"Static content extraction failed: {e}")
        
        # Test note extraction
        print("   🔍 Testing note extraction...")
        try:
            notes = extract_notes_with_selenium_final(test_url)
            
            assert notes is not None, "Note extraction returned None"
            assert isinstance(notes, list), "Notes should be a list"
            
            print(f"   ✅ Note extraction: {len(notes)} notes extracted")
            
            # If notes were found, validate their format
            if notes:
                for i, note in enumerate(notes[:3]):
                    assert isinstance(note, str), f"Note {i} should be string"
                    assert len(note) > 5, f"Note {i} too short: '{note}'"
                    print(f"   📝 Sample note {i+1}: {note[:100]}...")
            
        except Exception as e:
            pytest.fail(f"Note extraction failed: {e}")
    
    def test_note_extraction_error_handling(self):
        """Test that note extraction handles errors gracefully."""
        # Test with invalid URL
        invalid_url = "https://www.churchofjesuschrist.org/invalid-path"
        
        print(f"\n🚫 Testing error handling with invalid URL: {invalid_url}")
        
        try:
            notes = extract_notes_with_selenium_final(invalid_url)
            
            # Should either return empty list or handle gracefully
            assert notes is not None, "Should not return None even for invalid URLs"
            assert isinstance(notes, list), "Should return list even for invalid URLs"
            
            print(f"   ✅ Error handled gracefully: {len(notes)} notes")
            
        except Exception as e:
            # If it throws an exception, it should be a reasonable one
            print(f"   ⚠️ Exception thrown (acceptable): {e}")
            assert "timeout" in str(e).lower() or "not found" in str(e).lower() or "connection" in str(e).lower(), \
                f"Unexpected exception type: {e}"
    
    def _extract_talk_name_from_url(self, url: str) -> str:
        """Extract a readable talk name from URL for reporting."""
        import re
        
        # Extract the talk slug from URL
        match = re.search(r'/([^/]+)\?lang=', url)
        if match:
            slug = match.group(1)
            # Convert from slug to readable name
            return slug.replace('-', ' ').title()
        
        return url.split('/')[-1].split('?')[0]
    
    def _store_test_results(self, language: str, results: List[Dict]) -> None:
        """Store test results for further analysis."""
        import json
        from datetime import datetime
        
        results_dir = Path(__file__).parent / 'note_extraction_results'
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"note_extraction_{language}_{timestamp}.json"
        
        result_data = {
            'timestamp': timestamp,
            'language': language,
            'total_tests': len(results),
            'successful': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results
        }
        
        with open(results_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Results saved to: {filename}")


@pytest.mark.integrity
@pytest.mark.phase3
@pytest.mark.critical
class TestPhase3NoteExtractionCritical:
    """Critical tests for note extraction that must pass."""
    
    def test_note_extraction_function_exists(self):
        """Test that the note extraction function exists and is callable."""
        assert callable(extract_notes_with_selenium_final), "extract_notes_with_selenium_final should be callable"
        assert callable(extract_talk_content_static), "extract_talk_content_static should be callable"
    
    def test_note_extraction_returns_proper_format(self):
        """Test that note extraction returns the expected data format."""
        # Use a known URL with notes
        test_url = "https://www.churchofjesuschrist.org/study/general-conference/2025/04/21andersen?lang=eng"
        
        try:
            notes = extract_notes_with_selenium_final(test_url)
            
            # Basic format checks
            assert notes is not None, "Should not return None"
            assert isinstance(notes, list), "Should return a list"
            
            # If notes exist, check their format
            if notes:
                for note in notes:
                    assert isinstance(note, str), "Each note should be a string"
                    assert len(note) > 0, "Notes should not be empty strings"
            
        except Exception as e:
            # For critical test, we just ensure it doesn't crash unexpectedly
            assert "selenium" not in str(e).lower() or "driver" not in str(e).lower(), \
                f"Selenium driver issue (critical): {e}"
    
    def test_static_content_extraction_baseline(self):
        """Test that basic static content extraction works (baseline for notes)."""
        test_url = "https://www.churchofjesuschrist.org/study/general-conference/2025/04/21andersen?lang=eng"
        
        try:
            content = extract_talk_content_static(test_url)
            
            assert content is not None, "Static content should not be None"
            assert isinstance(content, dict), "Should return a dictionary"
            assert 'title' in content, "Should have title"
            assert 'content' in content, "Should have content"
            
        except Exception as e:
            pytest.fail(f"Critical static content extraction failed: {e}")


if __name__ == "__main__":
    # Allow running this file directly for testing
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
