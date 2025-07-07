"""
Tests for fuzzy search functionality
"""

import pytest
from veridoc.core.fuzzy_search import (
    levenshtein_distance,
    fuzzy_match_score,
    fuzzy_search_tokens,
    split_camel_case,
    enhanced_fuzzy_match,
    FuzzyMatcher
)


class TestLevenshteinDistance:
    """Test cases for Levenshtein distance calculation."""
    
    def test_identical_strings(self):
        """Test distance between identical strings is 0."""
        assert levenshtein_distance("hello", "hello") == 0
        assert levenshtein_distance("", "") == 0
    
    def test_empty_strings(self):
        """Test distance with empty strings."""
        assert levenshtein_distance("hello", "") == 5
        assert levenshtein_distance("", "world") == 5
    
    def test_single_substitution(self):
        """Test single character substitution."""
        assert levenshtein_distance("cat", "bat") == 1
        assert levenshtein_distance("hello", "hallo") == 1
    
    def test_single_insertion(self):
        """Test single character insertion."""
        assert levenshtein_distance("cat", "cats") == 1
        assert levenshtein_distance("hello", "hellow") == 1
    
    def test_single_deletion(self):
        """Test single character deletion."""
        assert levenshtein_distance("cats", "cat") == 1
        assert levenshtein_distance("hello", "helo") == 1
    
    def test_complex_cases(self):
        """Test complex transformations."""
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("saturday", "sunday") == 3


class TestFuzzyMatchScore:
    """Test cases for fuzzy match scoring."""
    
    def test_exact_match(self):
        """Test exact matches get perfect score."""
        assert fuzzy_match_score("hello", "hello") == 1.0
        assert fuzzy_match_score("Hello", "hello", case_sensitive=False) == 1.0
    
    def test_substring_match(self):
        """Test substring matches get high scores."""
        score = fuzzy_match_score("doc", "document")
        assert 0.8 <= score < 1.0
        
        score = fuzzy_match_score("test", "unittest.py")
        assert 0.8 <= score < 1.0
    
    def test_no_match(self):
        """Test completely different strings get low scores."""
        assert fuzzy_match_score("xyz", "abc") == 0.0
        assert fuzzy_match_score("hello", "world") == 0.0
    
    def test_case_sensitivity(self):
        """Test case sensitive matching."""
        assert fuzzy_match_score("Hello", "hello", case_sensitive=True) < 1.0
        assert fuzzy_match_score("Hello", "hello", case_sensitive=False) == 1.0
    
    def test_similarity_threshold(self):
        """Test similarity threshold filtering."""
        # Similar strings should get non-zero scores
        assert fuzzy_match_score("test", "tests") > 0.7
        assert fuzzy_match_score("file", "files") > 0.7
        
        # Very different strings should get 0
        assert fuzzy_match_score("abc", "xyz") == 0.0


class TestFuzzySearchTokens:
    """Test cases for searching tokens with fuzzy matching."""
    
    def test_exact_token_match(self):
        """Test exact token matching."""
        tokens = ["hello", "world", "test"]
        results = fuzzy_search_tokens("hello", tokens)
        assert len(results) == 1
        assert results[0] == ("hello", 1.0)
    
    def test_fuzzy_token_match(self):
        """Test fuzzy token matching."""
        tokens = ["hello", "helo", "help", "world"]
        results = fuzzy_search_tokens("hello", tokens, threshold=0.7)
        
        # Should match "hello" exactly and "helo" fuzzily
        assert len(results) >= 2
        assert results[0][0] == "hello"
        assert results[0][1] == 1.0
    
    def test_threshold_filtering(self):
        """Test threshold filtering."""
        tokens = ["test", "testing", "tests", "best", "rest"]
        results = fuzzy_search_tokens("test", tokens, threshold=0.8)
        
        # Should match exact and very similar tokens
        matched_tokens = [r[0] for r in results]
        assert "test" in matched_tokens
        assert "tests" in matched_tokens
        assert "best" not in matched_tokens  # Too different


class TestSplitCamelCase:
    """Test cases for camelCase splitting."""
    
    def test_camel_case(self):
        """Test splitting camelCase."""
        assert split_camel_case("camelCase") == ["camel", "case"]
        assert split_camel_case("getUserName") == ["get", "user", "name"]
    
    def test_pascal_case(self):
        """Test splitting PascalCase."""
        assert split_camel_case("PascalCase") == ["pascal", "case"]
        assert split_camel_case("FileHandler") == ["file", "handler"]
    
    def test_snake_case(self):
        """Test splitting snake_case."""
        assert split_camel_case("snake_case") == ["snake", "case"]
        assert split_camel_case("get_user_name") == ["get", "user", "name"]
    
    def test_mixed_cases(self):
        """Test mixed naming conventions."""
        assert split_camel_case("HTTPSConnection") == ["https", "connection"]
        assert split_camel_case("file-name.txt") == ["file", "name", "txt"]


class TestEnhancedFuzzyMatch:
    """Test cases for enhanced fuzzy matching."""
    
    def test_exact_match(self):
        """Test exact matching."""
        assert enhanced_fuzzy_match("test", "test") == 1.0
    
    def test_substring_match(self):
        """Test substring matching with position bonus."""
        # Match at beginning should score higher
        score1 = enhanced_fuzzy_match("test", "test_file.py")
        score2 = enhanced_fuzzy_match("test", "my_test.py")
        assert score1 > score2
    
    def test_word_boundary_match(self):
        """Test word boundary matching."""
        score = enhanced_fuzzy_match("get user", "getUserName")
        assert score >= 0.85
    
    def test_acronym_match(self):
        """Test acronym matching."""
        score = enhanced_fuzzy_match("gfn", "getFileName")
        assert score >= 0.8
        
        score = enhanced_fuzzy_match("fh", "FileHandler")
        assert score >= 0.8
    
    def test_multi_word_query(self):
        """Test multi-word query matching."""
        score = enhanced_fuzzy_match("file handler", "FileHandler")
        assert score >= 0.85
        
        score = enhanced_fuzzy_match("user name", "get_user_name")
        assert score >= 0.8


class TestFuzzyMatcher:
    """Test cases for FuzzyMatcher class."""
    
    def test_initialization(self):
        """Test matcher initialization."""
        matcher = FuzzyMatcher(threshold=0.8, case_sensitive=True)
        assert matcher.threshold == 0.8
        assert matcher.case_sensitive == True
    
    def test_match_single(self):
        """Test matching single target."""
        matcher = FuzzyMatcher(threshold=0.7)
        
        # Exact match
        assert matcher.match("hello", "hello") == 1.0
        
        # Fuzzy match above threshold
        score = matcher.match("hello", "helo")
        assert score is not None
        assert score > 0.7
        
        # No match below threshold
        assert matcher.match("hello", "world") is None
    
    def test_match_list(self):
        """Test matching against list of targets."""
        matcher = FuzzyMatcher(threshold=0.7)
        targets = ["hello", "world", "help", "helm", "test"]
        
        results = matcher.match_list("hello", targets)
        
        # Should match "hello" exactly and maybe "help"/"helm" fuzzily
        assert len(results) >= 1
        assert results[0][0] == "hello"
        assert results[0][1] == 1.0
    
    def test_best_match(self):
        """Test finding best match."""
        matcher = FuzzyMatcher(threshold=0.6)
        targets = ["hello", "helo", "help", "world"]
        
        best = matcher.best_match("hello", targets)
        assert best is not None
        assert best[0] == "hello"
        assert best[1] == 1.0
        
        # No match above threshold
        best = matcher.best_match("xyz", targets)
        assert best is None