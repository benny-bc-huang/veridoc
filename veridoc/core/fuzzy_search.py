"""
Fuzzy search implementation for VeriDoc
Uses Levenshtein distance for approximate string matching
"""

from typing import List, Tuple, Optional


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    This is the minimum number of single-character edits (insertions, deletions, substitutions)
    required to change one string into the other.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    # Create distance matrix
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer than s2
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_match_score(query: str, target: str, case_sensitive: bool = False) -> float:
    """
    Calculate a fuzzy match score between 0 and 1.
    1.0 means perfect match, 0.0 means no match.
    """
    if not query or not target:
        return 0.0
    
    # Prepare strings
    if not case_sensitive:
        query = query.lower()
        target = target.lower()
    
    # Exact match
    if query == target:
        return 1.0
    
    # Substring match gets high score
    if query in target:
        return 0.9 - (0.1 * (len(target) - len(query)) / len(target))
    
    if target in query:
        return 0.8 - (0.1 * (len(query) - len(target)) / len(query))
    
    # Calculate Levenshtein distance
    distance = levenshtein_distance(query, target)
    max_len = max(len(query), len(target))
    
    # Convert distance to similarity score
    similarity = 1.0 - (distance / max_len)
    
    # Apply threshold - if similarity is too low, return 0
    if similarity < 0.5:
        return 0.0
    
    return similarity


def fuzzy_search_tokens(query: str, tokens: List[str], threshold: float = 0.7) -> List[Tuple[str, float]]:
    """
    Search for fuzzy matches in a list of tokens.
    Returns list of (token, score) tuples where score >= threshold.
    """
    results = []
    
    for token in tokens:
        score = fuzzy_match_score(query, token)
        if score >= threshold:
            results.append((token, score))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def split_camel_case(text: str) -> List[str]:
    """
    Split camelCase or PascalCase text into words.
    Example: "getUserName" -> ["get", "user", "name"]
    """
    import re
    
    # Handle sequences of uppercase letters (e.g., HTTPSConnection -> HTTPS Connection)
    # Insert space before uppercase letter that's followed by lowercase
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    
    # Insert space before uppercase letters that follow lowercase
    text = re.sub(r'([a-z\d])([A-Z])', r'\1 \2', text)
    
    # Split by various delimiters
    words = re.split(r'[\s_\-\.]+', text)
    
    return [w.lower() for w in words if w]


def enhanced_fuzzy_match(query: str, target: str, case_sensitive: bool = False) -> float:
    """
    Enhanced fuzzy matching that considers:
    - Exact matches
    - Substring matches
    - Word boundary matches
    - CamelCase splitting
    - Acronym matching
    """
    if not query or not target:
        return 0.0
    
    # Prepare strings
    if not case_sensitive:
        query_lower = query.lower()
        target_lower = target.lower()
    else:
        query_lower = query
        target_lower = target
    
    # Exact match
    if query_lower == target_lower:
        return 1.0
    
    # Substring match
    if query_lower in target_lower:
        position_bonus = 1.0 - (target_lower.index(query_lower) / len(target_lower))
        return 0.9 + (0.05 * position_bonus)
    
    # Check word boundaries
    target_words = split_camel_case(target)
    query_words = split_camel_case(query)
    
    # All query words match target words
    if all(any(qw in tw for tw in target_words) for qw in query_words):
        return 0.85
    
    # Acronym matching (e.g., "gfn" matches "getFileName")
    if len(query_lower) >= 2:
        target_initials = ''.join(w[0] for w in target_words if w)
        if query_lower == target_initials:
            return 0.8
    
    # Fuzzy match on the whole string
    base_score = fuzzy_match_score(query, target, case_sensitive)
    
    # Fuzzy match on individual words
    if len(query_words) > 1 or len(target_words) > 1:
        word_scores = []
        for qw in query_words:
            best_score = 0.0
            for tw in target_words:
                score = fuzzy_match_score(qw, tw)
                best_score = max(best_score, score)
            word_scores.append(best_score)
        
        if word_scores:
            word_score = sum(word_scores) / len(word_scores)
            base_score = max(base_score, word_score * 0.9)  # Slightly penalize word matching
    
    return base_score


class FuzzyMatcher:
    """
    A reusable fuzzy matcher that can be configured with different parameters.
    """
    
    def __init__(self, threshold: float = 0.7, case_sensitive: bool = False):
        self.threshold = threshold
        self.case_sensitive = case_sensitive
    
    def match(self, query: str, target: str) -> Optional[float]:
        """
        Match query against target. Returns score if >= threshold, None otherwise.
        """
        score = enhanced_fuzzy_match(query, target, self.case_sensitive)
        return score if score >= self.threshold else None
    
    def match_list(self, query: str, targets: List[str]) -> List[Tuple[str, float]]:
        """
        Match query against a list of targets.
        Returns list of (target, score) tuples for matches above threshold.
        """
        results = []
        
        for target in targets:
            score = self.match(query, target)
            if score is not None:
                results.append((target, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def best_match(self, query: str, targets: List[str]) -> Optional[Tuple[str, float]]:
        """
        Find the best match from a list of targets.
        Returns (target, score) tuple or None if no match above threshold.
        """
        matches = self.match_list(query, targets)
        return matches[0] if matches else None