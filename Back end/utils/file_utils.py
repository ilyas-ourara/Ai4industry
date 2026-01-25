"""File handling utilities."""

import hashlib
import re
from pathlib import Path
from typing import Optional, Union
import unicodedata


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha256, etc.)
        
    Returns:
        Hex digest of hash
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Convert string to safe filename.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename
    """
    if not filename:
        return "unnamed"
    
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ASCII", "ignore").decode("ASCII")
    
    filename = re.sub(r"[^\w\s\-.]", "", filename)
    filename = re.sub(r"\s+", "_", filename)
    filename = re.sub(r"_+", "_", filename)
    
    if len(filename) > max_length:
        name, ext = Path(filename).stem, Path(filename).suffix
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename.strip("_") or "unnamed"


def get_file_size_human(file_path: Union[str, Path]) -> str:
    """
    Get human-readable file size.
    
    Args:
        file_path: Path to file
        
    Returns:
        Human-readable size string
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return "0 B"
    
    size = file_path.stat().st_size
    
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    
    return f"{size:.1f} PB"


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False,
) -> list:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory path
        pattern: Glob pattern
        recursive: Search recursively
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def read_file_safe(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    fallback_encodings: Optional[list] = None,
) -> Optional[str]:
    """
    Read file with encoding fallbacks.
    
    Args:
        file_path: Path to file
        encoding: Primary encoding
        fallback_encodings: List of fallback encodings
        
    Returns:
        File content or None if failed
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    encodings = [encoding] + (fallback_encodings or ["latin-1", "cp1252"])
    
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    return None
