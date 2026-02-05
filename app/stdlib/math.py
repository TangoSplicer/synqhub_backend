"""
SynQ Standard Library - Math Module

Provides mathematical operations including trigonometry, logarithms,
statistics, and linear algebra operations.
"""

import math
from typing import List, Tuple, Union
from dataclasses import dataclass


# ============================================================================
# Trigonometric Functions
# ============================================================================

def sin(x: float) -> float:
    """Calculate sine of x (in radians)."""
    return math.sin(x)


def cos(x: float) -> float:
    """Calculate cosine of x (in radians)."""
    return math.cos(x)


def tan(x: float) -> float:
    """Calculate tangent of x (in radians)."""
    return math.tan(x)


def asin(x: float) -> float:
    """Calculate arcsine of x."""
    if not -1 <= x <= 1:
        raise ValueError("asin domain error: x must be in [-1, 1]")
    return math.asin(x)


def acos(x: float) -> float:
    """Calculate arccosine of x."""
    if not -1 <= x <= 1:
        raise ValueError("acos domain error: x must be in [-1, 1]")
    return math.acos(x)


def atan(x: float) -> float:
    """Calculate arctangent of x."""
    return math.atan(x)


def atan2(y: float, x: float) -> float:
    """Calculate arctangent of y/x."""
    return math.atan2(y, x)


# ============================================================================
# Exponential and Logarithmic Functions
# ============================================================================

def exp(x: float) -> float:
    """Calculate e^x."""
    return math.exp(x)


def log(x: float, base: float = math.e) -> float:
    """Calculate logarithm of x with given base (default: natural log)."""
    if x <= 0:
        raise ValueError("log domain error: x must be positive")
    return math.log(x, base)


def log10(x: float) -> float:
    """Calculate base-10 logarithm of x."""
    if x <= 0:
        raise ValueError("log10 domain error: x must be positive")
    return math.log10(x)


def log2(x: float) -> float:
    """Calculate base-2 logarithm of x."""
    if x <= 0:
        raise ValueError("log2 domain error: x must be positive")
    return math.log2(x)


def pow(x: float, y: float) -> float:
    """Calculate x^y."""
    return math.pow(x, y)


def sqrt(x: float) -> float:
    """Calculate square root of x."""
    if x < 0:
        raise ValueError("sqrt domain error: x must be non-negative")
    return math.sqrt(x)


def cbrt(x: float) -> float:
    """Calculate cube root of x."""
    if x >= 0:
        return math.pow(x, 1/3)
    else:
        return -math.pow(-x, 1/3)


# ============================================================================
# Rounding and Absolute Value Functions
# ============================================================================

def floor(x: float) -> int:
    """Round down to nearest integer."""
    return math.floor(x)


def ceil(x: float) -> int:
    """Round up to nearest integer."""
    return math.ceil(x)


def round(x: float, ndigits: int = 0) -> Union[int, float]:
    """Round to nearest integer or n decimal places."""
    if ndigits == 0:
        return int(round(x))
    return round(x, ndigits)


def trunc(x: float) -> int:
    """Truncate to integer (remove decimal part)."""
    return math.trunc(x)


def abs(x: Union[int, float]) -> Union[int, float]:
    """Return absolute value."""
    return abs(x)


def sign(x: Union[int, float]) -> int:
    """Return sign of x (-1, 0, or 1)."""
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


# ============================================================================
# Statistical Functions
# ============================================================================

def mean(data: List[float]) -> float:
    """Calculate arithmetic mean."""
    if not data:
        raise ValueError("mean: data cannot be empty")
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    """Calculate median value."""
    if not data:
        raise ValueError("median: data cannot be empty")
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 1:
        return sorted_data[n // 2]
    else:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2


def mode(data: List[float]) -> float:
    """Calculate mode (most frequent value)."""
    if not data:
        raise ValueError("mode: data cannot be empty")
    from collections import Counter
    counts = Counter(data)
    return max(counts, key=counts.get)


def variance(data: List[float], sample: bool = False) -> float:
    """Calculate variance."""
    if not data:
        raise ValueError("variance: data cannot be empty")
    m = mean(data)
    n = len(data)
    divisor = n - 1 if sample and n > 1 else n
    return sum((x - m) ** 2 for x in data) / divisor


def stddev(data: List[float], sample: bool = False) -> float:
    """Calculate standard deviation."""
    return math.sqrt(variance(data, sample))


def min(data: List[float]) -> float:
    """Find minimum value."""
    if not data:
        raise ValueError("min: data cannot be empty")
    return min(data)


def max(data: List[float]) -> float:
    """Find maximum value."""
    if not data:
        raise ValueError("max: data cannot be empty")
    return max(data)


def sum(data: List[float]) -> float:
    """Calculate sum of all values."""
    return sum(data)


def product(data: List[float]) -> float:
    """Calculate product of all values."""
    result = 1.0
    for x in data:
        result *= x
    return result


def quantile(data: List[float], q: float) -> float:
    """Calculate q-th quantile (0 <= q <= 1)."""
    if not 0 <= q <= 1:
        raise ValueError("quantile: q must be in [0, 1]")
    if not data:
        raise ValueError("quantile: data cannot be empty")
    sorted_data = sorted(data)
    idx = q * (len(sorted_data) - 1)
    lower = int(idx)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[lower]
    weight = idx - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


# ============================================================================
# Linear Algebra Functions
# ============================================================================

@dataclass
class Matrix:
    """Matrix representation."""
    data: List[List[float]]
    rows: int
    cols: int

    @staticmethod
    def create(data: List[List[float]]) -> 'Matrix':
        """Create matrix from 2D list."""
        if not data:
            raise ValueError("Matrix: data cannot be empty")
        rows = len(data)
        cols = len(data[0])
        if not all(len(row) == cols for row in data):
            raise ValueError("Matrix: all rows must have same length")
        return Matrix(data, rows, cols)

    def __str__(self) -> str:
        """String representation."""
        return '\n'.join(str(row) for row in self.data)


def matrix_add(a: Matrix, b: Matrix) -> Matrix:
    """Add two matrices."""
    if a.rows != b.rows or a.cols != b.cols:
        raise ValueError("matrix_add: matrices must have same dimensions")
    result = [[a.data[i][j] + b.data[i][j] for j in range(a.cols)] 
              for i in range(a.rows)]
    return Matrix.create(result)


def matrix_sub(a: Matrix, b: Matrix) -> Matrix:
    """Subtract two matrices."""
    if a.rows != b.rows or a.cols != b.cols:
        raise ValueError("matrix_sub: matrices must have same dimensions")
    result = [[a.data[i][j] - b.data[i][j] for j in range(a.cols)] 
              for i in range(a.rows)]
    return Matrix.create(result)


def matrix_mul(a: Matrix, b: Matrix) -> Matrix:
    """Multiply two matrices."""
    if a.cols != b.rows:
        raise ValueError("matrix_mul: incompatible dimensions")
    result = [[sum(a.data[i][k] * b.data[k][j] for k in range(a.cols))
               for j in range(b.cols)] for i in range(a.rows)]
    return Matrix.create(result)


def matrix_transpose(m: Matrix) -> Matrix:
    """Transpose a matrix."""
    result = [[m.data[i][j] for i in range(m.rows)] for j in range(m.cols)]
    return Matrix.create(result)


def matrix_determinant(m: Matrix) -> float:
    """Calculate matrix determinant."""
    if m.rows != m.cols:
        raise ValueError("determinant: matrix must be square")
    
    n = m.rows
    if n == 1:
        return m.data[0][0]
    if n == 2:
        return m.data[0][0] * m.data[1][1] - m.data[0][1] * m.data[1][0]
    
    # LU decomposition for larger matrices
    det = 1.0
    matrix = [row[:] for row in m.data]
    
    for i in range(n):
        # Find pivot
        max_row = i
        for k in range(i + 1, n):
            if abs(matrix[k][i]) > abs(matrix[max_row][i]):
                max_row = k
        
        if abs(matrix[max_row][i]) < 1e-10:
            return 0.0
        
        if max_row != i:
            matrix[i], matrix[max_row] = matrix[max_row], matrix[i]
            det *= -1
        
        det *= matrix[i][i]
        
        for k in range(i + 1, n):
            factor = matrix[k][i] / matrix[i][i]
            for j in range(i, n):
                matrix[k][j] -= factor * matrix[i][j]
    
    return det


def matrix_trace(m: Matrix) -> float:
    """Calculate matrix trace (sum of diagonal elements)."""
    if m.rows != m.cols:
        raise ValueError("trace: matrix must be square")
    return sum(m.data[i][i] for i in range(m.rows))


def matrix_rank(m: Matrix) -> int:
    """Calculate matrix rank."""
    matrix = [row[:] for row in m.data]
    rank = 0
    
    for col in range(m.cols):
        # Find pivot
        pivot_row = None
        for row in range(rank, m.rows):
            if abs(matrix[row][col]) > 1e-10:
                pivot_row = row
                break
        
        if pivot_row is None:
            continue
        
        # Swap rows
        matrix[rank], matrix[pivot_row] = matrix[pivot_row], matrix[rank]
        
        # Eliminate
        for row in range(rank + 1, m.rows):
            if abs(matrix[rank][col]) > 1e-10:
                factor = matrix[row][col] / matrix[rank][col]
                for j in range(col, m.cols):
                    matrix[row][j] -= factor * matrix[rank][j]
        
        rank += 1
    
    return rank


def matrix_inverse(m: Matrix) -> Matrix:
    """Calculate matrix inverse."""
    if m.rows != m.cols:
        raise ValueError("inverse: matrix must be square")
    
    det = matrix_determinant(m)
    if abs(det) < 1e-10:
        raise ValueError("inverse: matrix is singular (determinant is zero)")
    
    n = m.rows
    # Create augmented matrix [A | I]
    aug = [m.data[i] + [1.0 if i == j else 0.0 for j in range(n)] 
           for i in range(n)]
    
    # Gauss-Jordan elimination
    for i in range(n):
        # Find pivot
        max_row = i
        for k in range(i + 1, n):
            if abs(aug[k][i]) > abs(aug[max_row][i]):
                max_row = k
        aug[i], aug[max_row] = aug[max_row], aug[i]
        
        # Scale pivot row
        pivot = aug[i][i]
        for j in range(2 * n):
            aug[i][j] /= pivot
        
        # Eliminate column
        for k in range(n):
            if k != i:
                factor = aug[k][i]
                for j in range(2 * n):
                    aug[k][j] -= factor * aug[i][j]
    
    # Extract inverse from augmented matrix
    result = [[aug[i][j + n] for j in range(n)] for i in range(n)]
    return Matrix.create(result)


# ============================================================================
# Constants
# ============================================================================

PI = math.pi
E = math.e
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2


__all__ = [
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
    'exp', 'log', 'log10', 'log2', 'pow', 'sqrt', 'cbrt',
    'floor', 'ceil', 'round', 'trunc', 'abs', 'sign',
    'mean', 'median', 'mode', 'variance', 'stddev',
    'min', 'max', 'sum', 'product', 'quantile',
    'Matrix', 'matrix_add', 'matrix_sub', 'matrix_mul',
    'matrix_transpose', 'matrix_determinant', 'matrix_trace',
    'matrix_rank', 'matrix_inverse',
    'PI', 'E', 'SQRT2', 'SQRT3', 'GOLDEN_RATIO'
]
