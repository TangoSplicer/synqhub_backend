"""
SynQ Standard Library - Strings Module

Provides string manipulation, formatting, and regular expression operations.
"""

import re
import base64
import binascii
from typing import List, Optional, Tuple, Union


# ============================================================================
# Basic String Operations
# ============================================================================

def length(s: str) -> int:
    """Get string length."""
    return len(s)


def concat(*strings: str) -> str:
    """Concatenate multiple strings."""
    return ''.join(strings)


def split(s: str, delimiter: str = None, maxsplit: int = -1) -> List[str]:
    """Split string by delimiter."""
    if delimiter is None:
        return s.split()
    return s.split(delimiter, maxsplit)


def join(parts: List[str], separator: str = '') -> str:
    """Join list of strings with separator."""
    return separator.join(parts)


def trim(s: str) -> str:
    """Remove leading and trailing whitespace."""
    return s.strip()


def ltrim(s: str) -> str:
    """Remove leading whitespace."""
    return s.lstrip()


def rtrim(s: str) -> str:
    """Remove trailing whitespace."""
    return s.rstrip()


def uppercase(s: str) -> str:
    """Convert to uppercase."""
    return s.upper()


def lowercase(s: str) -> str:
    """Convert to lowercase."""
    return s.lower()


def capitalize(s: str) -> str:
    """Capitalize first character."""
    return s.capitalize()


def reverse(s: str) -> str:
    """Reverse string."""
    return s[::-1]


def contains(s: str, substring: str) -> bool:
    """Check if string contains substring."""
    return substring in s


def starts_with(s: str, prefix: str) -> bool:
    """Check if string starts with prefix."""
    return s.startswith(prefix)


def ends_with(s: str, suffix: str) -> bool:
    """Check if string ends with suffix."""
    return s.endswith(suffix)


def index_of(s: str, substring: str, start: int = 0) -> int:
    """Find index of substring (-1 if not found)."""
    try:
        return s.index(substring, start)
    except ValueError:
        return -1


def last_index_of(s: str, substring: str) -> int:
    """Find last index of substring (-1 if not found)."""
    try:
        return s.rindex(substring)
    except ValueError:
        return -1


def replace(s: str, old: str, new: str, count: int = -1) -> str:
    """Replace occurrences of substring."""
    if count == -1:
        return s.replace(old, new)
    return s.replace(old, new, count)


def substring(s: str, start: int, end: Optional[int] = None) -> str:
    """Extract substring."""
    if end is None:
        return s[start:]
    return s[start:end]


def repeat(s: str, count: int) -> str:
    """Repeat string count times."""
    if count < 0:
        raise ValueError("repeat: count must be non-negative")
    return s * count


def char_at(s: str, index: int) -> str:
    """Get character at index."""
    if not 0 <= index < len(s):
        raise IndexError("char_at: index out of bounds")
    return s[index]


def count(s: str, substring: str) -> int:
    """Count occurrences of substring."""
    return s.count(substring)


# ============================================================================
# Formatting Functions
# ============================================================================

def format(template: str, *args, **kwargs) -> str:
    """Format string with positional and keyword arguments."""
    try:
        return template.format(*args, **kwargs)
    except (IndexError, KeyError) as e:
        raise ValueError(f"format: {e}")


def sprintf(fmt: str, *args) -> str:
    """Format string using printf-style formatting."""
    try:
        return fmt % args if args else fmt
    except (TypeError, ValueError) as e:
        raise ValueError(f"sprintf: {e}")


def pad_left(s: str, width: int, fill: str = ' ') -> str:
    """Pad string on left to width."""
    if len(fill) != 1:
        raise ValueError("pad_left: fill must be single character")
    return s.rjust(width, fill)


def pad_right(s: str, width: int, fill: str = ' ') -> str:
    """Pad string on right to width."""
    if len(fill) != 1:
        raise ValueError("pad_right: fill must be single character")
    return s.ljust(width, fill)


def center(s: str, width: int, fill: str = ' ') -> str:
    """Center string in field of width."""
    if len(fill) != 1:
        raise ValueError("center: fill must be single character")
    return s.center(width, fill)


# ============================================================================
# Parsing Functions
# ============================================================================

def parse_int(s: str, base: int = 10) -> int:
    """Parse string as integer."""
    try:
        return int(s.strip(), base)
    except ValueError:
        raise ValueError(f"parse_int: '{s}' is not a valid integer")


def parse_float(s: str) -> float:
    """Parse string as float."""
    try:
        return float(s.strip())
    except ValueError:
        raise ValueError(f"parse_float: '{s}' is not a valid float")


def parse_bool(s: str) -> bool:
    """Parse string as boolean."""
    s_lower = s.lower().strip()
    if s_lower in ('true', '1', 'yes', 'on'):
        return True
    elif s_lower in ('false', '0', 'no', 'off'):
        return False
    else:
        raise ValueError(f"parse_bool: '{s}' is not a valid boolean")


def to_string(value) -> str:
    """Convert value to string."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    elif value is None:
        return 'null'
    return str(value)


# ============================================================================
# Regular Expressions
# ============================================================================

class Regex:
    """Regular expression wrapper."""
    
    def __init__(self, pattern: str, flags: int = 0):
        """Compile regular expression."""
        try:
            self.pattern = pattern
            self.regex = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Regex: invalid pattern - {e}")
    
    def match(self, text: str) -> bool:
        """Check if regex matches text."""
        return self.regex.search(text) is not None
    
    def find(self, text: str) -> Optional[str]:
        """Find first match."""
        m = self.regex.search(text)
        return m.group(0) if m else None
    
    def find_all(self, text: str) -> List[str]:
        """Find all matches."""
        return self.regex.findall(text)
    
    def replace(self, text: str, replacement: str) -> str:
        """Replace all matches."""
        return self.regex.sub(replacement, text)
    
    def split(self, text: str) -> List[str]:
        """Split by regex."""
        return self.regex.split(text)


def regex_compile(pattern: str) -> Regex:
    """Compile regular expression."""
    return Regex(pattern)


def regex_match(regex: Regex, text: str) -> bool:
    """Check if regex matches text."""
    return regex.match(text)


def regex_find(regex: Regex, text: str) -> Optional[str]:
    """Find first match."""
    return regex.find(text)


def regex_find_all(regex: Regex, text: str) -> List[str]:
    """Find all matches."""
    return regex.find_all(text)


def regex_replace(regex: Regex, text: str, replacement: str) -> str:
    """Replace all matches."""
    return regex.replace(text, replacement)


# ============================================================================
# Encoding/Decoding Functions
# ============================================================================

def encode_utf8(s: str) -> bytes:
    """Encode string as UTF-8 bytes."""
    return s.encode('utf-8')


def decode_utf8(data: bytes) -> str:
    """Decode UTF-8 bytes as string."""
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError as e:
        raise ValueError(f"decode_utf8: invalid UTF-8 - {e}")


def encode_base64(s: str) -> str:
    """Encode string as base64."""
    return base64.b64encode(s.encode('utf-8')).decode('ascii')


def decode_base64(s: str) -> str:
    """Decode base64 string."""
    try:
        return base64.b64decode(s).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError) as e:
        raise ValueError(f"decode_base64: invalid base64 - {e}")


def encode_hex(s: str) -> str:
    """Encode string as hexadecimal."""
    return s.encode('utf-8').hex()


def decode_hex(s: str) -> str:
    """Decode hexadecimal string."""
    try:
        return bytes.fromhex(s).decode('utf-8')
    except (ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"decode_hex: invalid hex - {e}")


def encode_url(s: str) -> str:
    """URL-encode string."""
    import urllib.parse
    return urllib.parse.quote(s)


def decode_url(s: str) -> str:
    """URL-decode string."""
    import urllib.parse
    return urllib.parse.unquote(s)


# ============================================================================
# Character Classification
# ============================================================================

def is_alpha(s: str) -> bool:
    """Check if all characters are alphabetic."""
    return s.isalpha()


def is_digit(s: str) -> bool:
    """Check if all characters are digits."""
    return s.isdigit()


def is_alnum(s: str) -> bool:
    """Check if all characters are alphanumeric."""
    return s.isalnum()


def is_space(s: str) -> bool:
    """Check if all characters are whitespace."""
    return s.isspace()


def is_upper(s: str) -> bool:
    """Check if all cased characters are uppercase."""
    return s.isupper()


def is_lower(s: str) -> bool:
    """Check if all cased characters are lowercase."""
    return s.islower()


# ============================================================================
# String Comparison
# ============================================================================

def equals(a: str, b: str) -> bool:
    """Check if strings are equal."""
    return a == b


def equals_ignore_case(a: str, b: str) -> bool:
    """Check if strings are equal (case-insensitive)."""
    return a.lower() == b.lower()


def compare(a: str, b: str) -> int:
    """Compare strings (-1, 0, 1)."""
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0


def levenshtein_distance(a: str, b: str) -> int:
    """Calculate Levenshtein distance between strings."""
    if len(a) < len(b):
        a, b = b, a
    
    if len(b) == 0:
        return len(a)
    
    previous_row = range(len(b) + 1)
    for i, ca in enumerate(a):
        current_row = [i + 1]
        for j, cb in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


__all__ = [
    'length', 'concat', 'split', 'join', 'trim', 'ltrim', 'rtrim',
    'uppercase', 'lowercase', 'capitalize', 'reverse',
    'contains', 'starts_with', 'ends_with', 'index_of', 'last_index_of',
    'replace', 'substring', 'repeat', 'char_at', 'count',
    'format', 'sprintf', 'pad_left', 'pad_right', 'center',
    'parse_int', 'parse_float', 'parse_bool', 'to_string',
    'Regex', 'regex_compile', 'regex_match', 'regex_find',
    'regex_find_all', 'regex_replace',
    'encode_utf8', 'decode_utf8', 'encode_base64', 'decode_base64',
    'encode_hex', 'decode_hex', 'encode_url', 'decode_url',
    'is_alpha', 'is_digit', 'is_alnum', 'is_space', 'is_upper', 'is_lower',
    'equals', 'equals_ignore_case', 'compare', 'levenshtein_distance'
]
