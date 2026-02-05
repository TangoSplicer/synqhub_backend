"""
SynQ Standard Library - I/O Module

Provides file operations, stream processing, console I/O, and network operations.
"""

import os
import sys
import io
from typing import Optional, List, Union, BinaryIO, TextIO
from pathlib import Path
import socket
import json


# ============================================================================
# File Operations
# ============================================================================

class File:
    """File handle wrapper."""
    
    def __init__(self, path: str, mode: str = 'r', encoding: str = 'utf-8'):
        """Open file."""
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self._file: Optional[Union[TextIO, BinaryIO]] = None
        self._open()
    
    def _open(self):
        """Open the file."""
        try:
            if 'b' in self.mode:
                self._file = open(self.path, self.mode)
            else:
                self._file = open(self.path, self.mode, encoding=self.encoding)
        except IOError as e:
            raise IOError(f"Failed to open file '{self.path}': {e}")
    
    def read(self, size: int = -1) -> str:
        """Read up to size characters."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.read(size)
        except IOError as e:
            raise IOError(f"Failed to read from file: {e}")
    
    def read_all(self) -> str:
        """Read entire file."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.read()
        except IOError as e:
            raise IOError(f"Failed to read from file: {e}")
    
    def read_line(self) -> str:
        """Read one line."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.readline()
        except IOError as e:
            raise IOError(f"Failed to read from file: {e}")
    
    def read_lines(self) -> List[str]:
        """Read all lines."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.readlines()
        except IOError as e:
            raise IOError(f"Failed to read from file: {e}")
    
    def write(self, data: str) -> int:
        """Write data to file."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.write(data)
        except IOError as e:
            raise IOError(f"Failed to write to file: {e}")
    
    def write_line(self, data: str) -> int:
        """Write line to file."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.write(data + '\n')
        except IOError as e:
            raise IOError(f"Failed to write to file: {e}")
    
    def seek(self, offset: int, whence: int = 0) -> int:
        """Seek to position."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.seek(offset, whence)
        except IOError as e:
            raise IOError(f"Failed to seek in file: {e}")
    
    def tell(self) -> int:
        """Get current position."""
        if not self._file:
            raise IOError("File is closed")
        try:
            return self._file.tell()
        except IOError as e:
            raise IOError(f"Failed to get position: {e}")
    
    def flush(self) -> None:
        """Flush buffer."""
        if self._file:
            try:
                self._file.flush()
            except IOError as e:
                raise IOError(f"Failed to flush file: {e}")
    
    def close(self) -> None:
        """Close file."""
        if self._file:
            try:
                self._file.close()
                self._file = None
            except IOError as e:
                raise IOError(f"Failed to close file: {e}")
    
    def is_closed(self) -> bool:
        """Check if file is closed."""
        return self._file is None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        return f"File('{self.path}')"


def file_open(path: str, mode: str = 'r') -> File:
    """Open file."""
    return File(path, mode)


def file_read(path: str) -> str:
    """Read entire file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Failed to read file '{path}': {e}")


def file_write(path: str, data: str) -> int:
    """Write data to file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            return f.write(data)
    except IOError as e:
        raise IOError(f"Failed to write to file '{path}': {e}")


def file_append(path: str, data: str) -> int:
    """Append data to file."""
    try:
        with open(path, 'a', encoding='utf-8') as f:
            return f.write(data)
    except IOError as e:
        raise IOError(f"Failed to append to file '{path}': {e}")


def file_exists(path: str) -> bool:
    """Check if file exists."""
    return os.path.isfile(path)


def file_delete(path: str) -> bool:
    """Delete file."""
    try:
        os.remove(path)
        return True
    except OSError:
        return False


def file_copy(src: str, dst: str) -> bool:
    """Copy file."""
    try:
        import shutil
        shutil.copy2(src, dst)
        return True
    except (IOError, OSError):
        return False


def file_rename(old: str, new: str) -> bool:
    """Rename file."""
    try:
        os.rename(old, new)
        return True
    except OSError:
        return False


def file_size(path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def file_modified_time(path: str) -> float:
    """Get file modification time."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return -1


# ============================================================================
# Directory Operations
# ============================================================================

def dir_exists(path: str) -> bool:
    """Check if directory exists."""
    return os.path.isdir(path)


def dir_create(path: str) -> bool:
    """Create directory."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def dir_delete(path: str) -> bool:
    """Delete directory."""
    try:
        import shutil
        shutil.rmtree(path)
        return True
    except OSError:
        return False


def dir_list(path: str) -> List[str]:
    """List directory contents."""
    try:
        return os.listdir(path)
    except OSError:
        return []


def dir_walk(path: str) -> List[tuple]:
    """Walk directory tree."""
    try:
        result = []
        for root, dirs, files in os.walk(path):
            result.append((root, dirs, files))
        return result
    except OSError:
        return []


def dir_current() -> str:
    """Get current working directory."""
    return os.getcwd()


def dir_change(path: str) -> bool:
    """Change working directory."""
    try:
        os.chdir(path)
        return True
    except OSError:
        return False


# ============================================================================
# Path Operations
# ============================================================================

def path_join(*parts: str) -> str:
    """Join path components."""
    return os.path.join(*parts)


def path_basename(path: str) -> str:
    """Get filename from path."""
    return os.path.basename(path)


def path_dirname(path: str) -> str:
    """Get directory from path."""
    return os.path.dirname(path)


def path_extension(path: str) -> str:
    """Get file extension."""
    return os.path.splitext(path)[1]


def path_without_extension(path: str) -> str:
    """Get path without extension."""
    return os.path.splitext(path)[0]


def path_absolute(path: str) -> str:
    """Get absolute path."""
    return os.path.abspath(path)


def path_normalize(path: str) -> str:
    """Normalize path."""
    return os.path.normpath(path)


def path_exists(path: str) -> bool:
    """Check if path exists."""
    return os.path.exists(path)


def path_is_file(path: str) -> bool:
    """Check if path is file."""
    return os.path.isfile(path)


def path_is_dir(path: str) -> bool:
    """Check if path is directory."""
    return os.path.isdir(path)


# ============================================================================
# Console I/O
# ============================================================================

def print(*args, sep: str = ' ', end: str = '\n') -> None:
    """Print to console."""
    print(*args, sep=sep, end=end)


def println(*args, sep: str = ' ') -> None:
    """Print line to console."""
    print(*args, sep=sep)


def read_line() -> str:
    """Read line from console."""
    try:
        return input()
    except EOFError:
        return ""


def read_char() -> str:
    """Read single character from console."""
    try:
        import sys
        if sys.stdin.isatty():
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        else:
            return sys.stdin.read(1)
    except Exception:
        return ""


def flush_stdout() -> None:
    """Flush stdout."""
    sys.stdout.flush()


def flush_stderr() -> None:
    """Flush stderr."""
    sys.stderr.flush()


# ============================================================================
# Stream Processing
# ============================================================================

class Stream:
    """Stream wrapper for processing sequences."""
    
    def __init__(self, data: List):
        """Create stream from list."""
        self.data = data
    
    def map(self, func):
        """Map function over stream."""
        return Stream([func(x) for x in self.data])
    
    def filter(self, predicate):
        """Filter stream by predicate."""
        return Stream([x for x in self.data if predicate(x)])
    
    def reduce(self, func, initial=None):
        """Reduce stream to single value."""
        if initial is None and self.data:
            result = self.data[0]
            for x in self.data[1:]:
                result = func(result, x)
        else:
            result = initial
            for x in self.data:
                result = func(result, x)
        return result
    
    def collect(self) -> List:
        """Collect stream to list."""
        return self.data.copy()
    
    def count(self) -> int:
        """Count elements in stream."""
        return len(self.data)
    
    def __iter__(self):
        """Iterate over stream."""
        return iter(self.data)
    
    def __repr__(self) -> str:
        return f"Stream({self.data})"


def stream(data: List) -> Stream:
    """Create stream from list."""
    return Stream(data)


# ============================================================================
# JSON Operations
# ============================================================================

def json_parse(text: str):
    """Parse JSON string."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"json_parse: invalid JSON - {e}")


def json_stringify(obj, indent: Optional[int] = None) -> str:
    """Convert object to JSON string."""
    try:
        return json.dumps(obj, indent=indent)
    except (TypeError, ValueError) as e:
        raise ValueError(f"json_stringify: cannot serialize - {e}")


def json_read_file(path: str):
    """Read JSON from file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        raise IOError(f"json_read_file: failed to read '{path}' - {e}")


def json_write_file(path: str, obj, indent: Optional[int] = 2) -> None:
    """Write JSON to file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=indent)
    except (IOError, TypeError) as e:
        raise IOError(f"json_write_file: failed to write '{path}' - {e}")


__all__ = [
    'File', 'file_open', 'file_read', 'file_write', 'file_append',
    'file_exists', 'file_delete', 'file_copy', 'file_rename',
    'file_size', 'file_modified_time',
    'dir_exists', 'dir_create', 'dir_delete', 'dir_list', 'dir_walk',
    'dir_current', 'dir_change',
    'path_join', 'path_basename', 'path_dirname', 'path_extension',
    'path_without_extension', 'path_absolute', 'path_normalize',
    'path_exists', 'path_is_file', 'path_is_dir',
    'print', 'println', 'read_line', 'read_char',
    'flush_stdout', 'flush_stderr',
    'Stream', 'stream',
    'json_parse', 'json_stringify', 'json_read_file', 'json_write_file'
]
