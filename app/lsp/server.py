"""
SynQ Language Server Protocol (LSP) Implementation

Provides IDE support with syntax highlighting, code completion, diagnostics,
and other language features.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# LSP Data Structures
# ============================================================================

class DiagnosticSeverity(Enum):
    """Diagnostic severity levels."""
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


@dataclass
class Position:
    """Position in a document."""
    line: int
    character: int


@dataclass
class Range:
    """Range in a document."""
    start: Position
    end: Position


@dataclass
class Location:
    """Location in a document."""
    uri: str
    range: Range


@dataclass
class Diagnostic:
    """Diagnostic message."""
    range: Range
    severity: int
    code: Optional[str]
    source: str
    message: str
    relatedInformation: Optional[List[Dict]] = None


@dataclass
class CompletionItem:
    """Completion item for code completion."""
    label: str
    kind: int
    detail: Optional[str] = None
    documentation: Optional[str] = None
    sortText: Optional[str] = None
    filterText: Optional[str] = None
    insertText: Optional[str] = None


@dataclass
class SymbolInformation:
    """Symbol information for navigation."""
    name: str
    kind: int
    location: Location
    containerName: Optional[str] = None


@dataclass
class Hover:
    """Hover information."""
    contents: str
    range: Optional[Range] = None


# ============================================================================
# LSP Server
# ============================================================================

class SynQLSPServer:
    """Language Server Protocol server for SynQ."""
    
    def __init__(self):
        """Initialize LSP server."""
        self.logger = logging.getLogger('synq-lsp')
        self.documents: Dict[str, str] = {}
        self.diagnostics: Dict[str, List[Diagnostic]] = {}
        self.symbols: Dict[str, List[SymbolInformation]] = {}
        self.references: Dict[str, List[Location]] = {}
    
    # ========================================================================
    # Document Management
    # ========================================================================
    
    def open_document(self, uri: str, text: str) -> None:
        """Open document."""
        self.documents[uri] = text
        self.analyze_document(uri)
    
    def close_document(self, uri: str) -> None:
        """Close document."""
        if uri in self.documents:
            del self.documents[uri]
        if uri in self.diagnostics:
            del self.diagnostics[uri]
        if uri in self.symbols:
            del self.symbols[uri]
    
    def update_document(self, uri: str, text: str) -> None:
        """Update document content."""
        self.documents[uri] = text
        self.analyze_document(uri)
    
    # ========================================================================
    # Analysis
    # ========================================================================
    
    def analyze_document(self, uri: str) -> None:
        """Analyze document for diagnostics and symbols."""
        if uri not in self.documents:
            return
        
        text = self.documents[uri]
        diagnostics = []
        symbols = []
        
        # Parse document
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            # Check for syntax errors
            diagnostics.extend(self._check_syntax(line, line_num))
            
            # Extract symbols
            symbols.extend(self._extract_symbols(line, line_num, uri))
        
        self.diagnostics[uri] = diagnostics
        self.symbols[uri] = symbols
    
    def _check_syntax(self, line: str, line_num: int) -> List[Diagnostic]:
        """Check line for syntax errors."""
        diagnostics = []
        
        # Check for unclosed strings
        if line.count('"') % 2 != 0:
            diagnostics.append(Diagnostic(
                range=Range(Position(line_num, 0), Position(line_num, len(line))),
                severity=DiagnosticSeverity.ERROR.value,
                code="unclosed_string",
                source="synq",
                message="Unclosed string literal"
            ))
        
        # Check for unclosed parentheses
        open_parens = line.count('(') - line.count(')')
        if open_parens > 0:
            diagnostics.append(Diagnostic(
                range=Range(Position(line_num, 0), Position(line_num, len(line))),
                severity=DiagnosticSeverity.WARNING.value,
                code="unclosed_paren",
                source="synq",
                message="Unclosed parenthesis"
            ))
        
        return diagnostics
    
    def _extract_symbols(self, line: str, line_num: int, uri: str) -> List[SymbolInformation]:
        """Extract symbols from line."""
        symbols = []
        
        # Extract function definitions
        if line.strip().startswith('fn '):
            parts = line.strip().split('(')
            if len(parts) > 0:
                name = parts[0].replace('fn ', '').strip()
                symbols.append(SymbolInformation(
                    name=name,
                    kind=12,  # Function
                    location=Location(uri, Range(Position(line_num, 0), Position(line_num, len(line))))
                ))
        
        # Extract type definitions
        if line.strip().startswith('type '):
            parts = line.strip().split('=')
            if len(parts) > 0:
                name = parts[0].replace('type ', '').strip()
                symbols.append(SymbolInformation(
                    name=name,
                    kind=5,  # Class
                    location=Location(uri, Range(Position(line_num, 0), Position(line_num, len(line))))
                ))
        
        return symbols
    
    # ========================================================================
    # Code Completion
    # ========================================================================
    
    def get_completions(self, uri: str, line: int, character: int) -> List[CompletionItem]:
        """Get code completion suggestions."""
        if uri not in self.documents:
            return []
        
        text = self.documents[uri]
        lines = text.split('\n')
        
        if line >= len(lines):
            return []
        
        current_line = lines[line]
        word_start = character
        
        # Find word boundary
        while word_start > 0 and current_line[word_start - 1].isalnum():
            word_start -= 1
        
        prefix = current_line[word_start:character]
        
        # Get completions based on context
        completions = []
        
        # Keywords
        keywords = ['fn', 'type', 'let', 'mut', 'if', 'else', 'for', 'while', 'match', 'return']
        for keyword in keywords:
            if keyword.startswith(prefix):
                completions.append(CompletionItem(
                    label=keyword,
                    kind=14,  # Keyword
                    detail="Keyword",
                    sortText=f"0_{keyword}"
                ))
        
        # Built-in functions
        builtins = ['print', 'println', 'len', 'push', 'pop', 'map', 'filter']
        for builtin in builtins:
            if builtin.startswith(prefix):
                completions.append(CompletionItem(
                    label=builtin,
                    kind=3,  # Function
                    detail="Built-in function",
                    sortText=f"1_{builtin}"
                ))
        
        # Symbols from current document
        if uri in self.symbols:
            for symbol in self.symbols[uri]:
                if symbol.name.startswith(prefix):
                    completions.append(CompletionItem(
                        label=symbol.name,
                        kind=symbol.kind,
                        detail="Symbol",
                        sortText=f"2_{symbol.name}"
                    ))
        
        return completions
    
    # ========================================================================
    # Navigation
    # ========================================================================
    
    def get_definition(self, uri: str, line: int, character: int) -> Optional[Location]:
        """Get definition location for symbol at position."""
        if uri not in self.documents:
            return None
        
        text = self.documents[uri]
        lines = text.split('\n')
        
        if line >= len(lines):
            return None
        
        current_line = lines[line]
        
        # Find word at position
        word_start = character
        word_end = character
        
        while word_start > 0 and current_line[word_start - 1].isalnum():
            word_start -= 1
        while word_end < len(current_line) and current_line[word_end].isalnum():
            word_end += 1
        
        word = current_line[word_start:word_end]
        
        # Find definition
        if uri in self.symbols:
            for symbol in self.symbols[uri]:
                if symbol.name == word:
                    return symbol.location
        
        return None
    
    def find_references(self, uri: str, line: int, character: int) -> List[Location]:
        """Find all references to symbol at position."""
        if uri not in self.documents:
            return []
        
        text = self.documents[uri]
        lines = text.split('\n')
        
        if line >= len(lines):
            return []
        
        current_line = lines[line]
        
        # Find word at position
        word_start = character
        word_end = character
        
        while word_start > 0 and current_line[word_start - 1].isalnum():
            word_start -= 1
        while word_end < len(current_line) and current_line[word_end].isalnum():
            word_end += 1
        
        word = current_line[word_start:word_end]
        
        # Find all references
        references = []
        for line_num, line_text in enumerate(lines):
            for match_start in range(len(line_text)):
                if line_text[match_start:match_start + len(word)] == word:
                    references.append(Location(
                        uri=uri,
                        range=Range(
                            Position(line_num, match_start),
                            Position(line_num, match_start + len(word))
                        )
                    ))
        
        return references
    
    # ========================================================================
    # Hover Information
    # ========================================================================
    
    def get_hover(self, uri: str, line: int, character: int) -> Optional[Hover]:
        """Get hover information for symbol at position."""
        if uri not in self.documents:
            return None
        
        text = self.documents[uri]
        lines = text.split('\n')
        
        if line >= len(lines):
            return None
        
        current_line = lines[line]
        
        # Find word at position
        word_start = character
        word_end = character
        
        while word_start > 0 and current_line[word_start - 1].isalnum():
            word_start -= 1
        while word_end < len(current_line) and current_line[word_end].isalnum():
            word_end += 1
        
        word = current_line[word_start:word_end]
        
        # Get hover information
        if uri in self.symbols:
            for symbol in self.symbols[uri]:
                if symbol.name == word:
                    return Hover(
                        contents=f"**{symbol.name}** ({self._get_symbol_kind_name(symbol.kind)})",
                        range=Range(Position(line, word_start), Position(line, word_end))
                    )
        
        return None
    
    def _get_symbol_kind_name(self, kind: int) -> str:
        """Get human-readable symbol kind name."""
        kinds = {
            1: "File",
            2: "Module",
            3: "Namespace",
            4: "Package",
            5: "Class",
            6: "Method",
            7: "Property",
            8: "Field",
            9: "Constructor",
            10: "Enum",
            11: "Interface",
            12: "Function",
            13: "Variable",
            14: "Constant",
            15: "String",
            16: "Number",
            17: "Boolean",
            18: "Array",
            19: "Object",
            20: "Key",
            21: "Null",
            22: "EnumMember",
            23: "Struct",
            24: "Event",
            25: "Operator",
            26: "TypeParameter"
        }
        return kinds.get(kind, "Unknown")
    
    # ========================================================================
    # Formatting
    # ========================================================================
    
    def format_document(self, uri: str) -> str:
        """Format entire document."""
        if uri not in self.documents:
            return ""
        
        text = self.documents[uri]
        lines = text.split('\n')
        formatted_lines = []
        
        indent_level = 0
        for line in lines:
            stripped = line.strip()
            
            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Format line
            if stripped:
                formatted_lines.append('  ' * indent_level + stripped)
            else:
                formatted_lines.append('')
            
            # Increase indent for opening braces
            if stripped.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def format_range(self, uri: str, start_line: int, end_line: int) -> str:
        """Format range of lines."""
        if uri not in self.documents:
            return ""
        
        text = self.documents[uri]
        lines = text.split('\n')
        
        # Format only the specified range
        formatted_lines = []
        for i, line in enumerate(lines):
            if start_line <= i <= end_line:
                formatted_lines.append(line.strip())
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    # ========================================================================
    # Workspace Symbols
    # ========================================================================
    
    def get_workspace_symbols(self, query: str = "") -> List[SymbolInformation]:
        """Get all symbols in workspace."""
        symbols = []
        
        for uri, uri_symbols in self.symbols.items():
            for symbol in uri_symbols:
                if not query or query.lower() in symbol.name.lower():
                    symbols.append(symbol)
        
        return symbols
    
    # ========================================================================
    # Diagnostics
    # ========================================================================
    
    def get_diagnostics(self, uri: str) -> List[Diagnostic]:
        """Get diagnostics for document."""
        return self.diagnostics.get(uri, [])


__all__ = [
    'DiagnosticSeverity', 'Position', 'Range', 'Location',
    'Diagnostic', 'CompletionItem', 'SymbolInformation', 'Hover',
    'SynQLSPServer'
]
