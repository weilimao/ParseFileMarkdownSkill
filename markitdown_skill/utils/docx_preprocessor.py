import os
import re
import zipfile
import tempfile
from ..utils.logger import setup_logger

logger = setup_logger("markitdown_skill.docx_preprocessor")

ALTERNATE_CONTENT_PATTERN = re.compile(
    r'<mc:AlternateContent>(.*?)</mc:AlternateContent>',
    re.DOTALL
)

CHOICE_PATTERN = re.compile(
    r'<mc:Choice[^>]*>(.*?)</mc:Choice>',
    re.DOTALL
)

def fix_xml_alternate_content(xml_content: bytes) -> bytes:
    """
    Scans XML content for <mc:AlternateContent> blocks, extracting the first <mc:Choice>
    content to replace the block. This allows mammoth to parse w:drawing elements
    inside Choice blocks rather than fallback w:pict elements.
    """
    try:
        content_str = xml_content.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.warning(f"Failed to decode XML content, skipping pre-processing: {e}")
        return xml_content

    def replace_alternate(match):
        inner_content = match.group(1)
        choice_match = CHOICE_PATTERN.search(inner_content)
        if choice_match:
            # Return the Choice content, unwrapped
            return choice_match.group(1)
        return match.group(0) # Keep original if Choice is not found

    fixed_str = ALTERNATE_CONTENT_PATTERN.sub(replace_alternate, content_str)
    return fixed_str.encode('utf-8')

def preprocess_docx(file_path: str) -> str:
    """
    Unzips the DOCX file, processes XML files containing potential AlternateContent
    elements (such as document.xml, footnotes.xml, endnotes.xml), writes them to
    a new temporary docx file, and returns the path to the temporary file.
    
    If the file is not a valid zip or error occurs, returns the original path.
    """
    if not os.path.exists(file_path):
        return file_path
        
    try:
        if not zipfile.is_zipfile(file_path):
            return file_path
    except Exception:
        return file_path

    # The files that might contain AlternateContent elements
    pre_process_files = [
        "word/document.xml",
        "word/footnotes.xml",
        "word/endnotes.xml",
    ]

    try:
        # Create a temp file to store the preprocessed docx
        temp_dir = tempfile.gettempdir()
        fd, temp_docx_path = tempfile.mkstemp(suffix=".docx", dir=temp_dir)
        os.close(fd) # Close file descriptor so we can write using zipfile

        with zipfile.ZipFile(file_path, 'r') as zip_in:
            with zipfile.ZipFile(temp_docx_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_out:
                for item in zip_in.infolist():
                    data = zip_in.read(item.filename)
                    if item.filename in pre_process_files:
                        try:
                            data = fix_xml_alternate_content(data)
                        except Exception as e:
                            logger.error(f"Error preprocessing {item.filename}: {e}")
                    zip_out.writestr(item, data)
        
        logger.info(f"Successfully preprocessed docx for pasted images: {temp_docx_path}")
        return temp_docx_path
    except Exception as e:
        logger.error(f"Failed to preprocess docx file {file_path}: {e}", exc_info=True)
        # If preprocessing fails, fallback to original file
        if 'temp_docx_path' in locals() and os.path.exists(temp_docx_path):
            try:
                os.remove(temp_docx_path)
            except Exception:
                pass
        return file_path
