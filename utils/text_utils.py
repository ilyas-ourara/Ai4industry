"""Text processing utilities."""

import re
from typing import List, Optional
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing unicode.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    
    # Remove control characters except newlines
    text = "".join(c for c in text if c == "\n" or not unicodedata.category(c).startswith("C"))
    
    # Normalize whitespace
    text = normalize_whitespace(text)
    
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    - Multiple spaces -> single space
    - Multiple newlines -> max 2 newlines
    - Tabs -> spaces
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    
    # Multiple spaces to single space
    text = re.sub(r" +", " ", text)
    
    # Multiple newlines to max 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Remove trailing whitespace on lines
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    return text


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from text.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted numbers
    """
    if not text:
        return []
    
    # Pattern for integers and decimals
    pattern = r"-?\d+(?:[.,]\d+)?"
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            # Handle French decimal separator
            match = match.replace(",", ".")
            numbers.append(float(match))
        except ValueError:
            continue
    
    return numbers


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Simple sentence splitting for French
    pattern = r"(?<=[.!?])\s+"
    sentences = re.split(pattern, text)
    
    return [s.strip() for s in sentences if s.strip()]


def remove_accents(text: str) -> str:
    """
    Remove accents from text.
    
    Args:
        text: Input text
        
    Returns:
        Text without accents
    """
    if not text:
        return ""
    
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def is_mostly_uppercase(text: str, threshold: float = 0.7) -> bool:
    """
    Check if text is mostly uppercase (likely a title/heading).
    
    Args:
        text: Input text
        threshold: Percentage of uppercase letters
        
    Returns:
        True if mostly uppercase
    """
    if not text:
        return False
    
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    
    uppercase_count = sum(1 for c in letters if c.isupper())
    return uppercase_count / len(letters) >= threshold
