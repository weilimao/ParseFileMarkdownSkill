class MarkItDownSkillError(Exception):
    """Base exception for all MarkItDown Skill errors."""
    pass

class ParserInitializationError(MarkItDownSkillError):
    """Raised when the parser fails to initialize."""
    pass

class FileConversionError(MarkItDownSkillError):
    """Raised when file conversion fails."""
    pass

class UnsupportedFormatError(MarkItDownSkillError):
    """Raised when the file format is not supported."""
    pass
