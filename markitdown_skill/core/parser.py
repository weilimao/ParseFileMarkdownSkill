import os
import mimetypes
import time
import tempfile
from typing import Union, Optional, Any, Dict
from markitdown import MarkItDown
from .exceptions import FileConversionError, ParserInitializationError
from ..utils.logger import setup_logger

logger = setup_logger("markitdown_skill.parser")

class MarkItDownParser:
    """
    Core wrapper around Microsoft's MarkItDown library.
    """
    def __init__(self, llm_client: Optional[Any] = None, llm_model: Optional[str] = None):
        """
        Initializes the parser.
        
        :param llm_client: Optional LLM client (e.g. OpenAI) to enable multimodal enhancements.
        :param llm_model: Optional LLM model (e.g. "gpt-4o") for multimodal enhancements.
        """
        try:
            if llm_client:
                logger.info(f"Initializing MarkItDown with LLM support using model: {llm_model or 'default'}")
                self.md = MarkItDown(llm_client=llm_client, llm_model=llm_model)
            else:
                logger.info("Initializing MarkItDown in standard offline mode")
                self.md = MarkItDown()
        except Exception as e:
            logger.error("Failed to initialize MarkItDown engine", exc_info=True)
            raise ParserInitializationError("Failed to initialize MarkItDown", e)

    def parse(self, source: Union[str, bytes], file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses a document file path or file bytes into Markdown content and metadata.

        :param source: The file path (str) or raw file bytes (bytes)
        :param file_name: Optional filename, required if parsing bytes source to preserve type
        :return: A dictionary containing 'content' (Markdown string) and 'metadata' (Dict)
        """
        temp_file_created = False
        target_path = ""
        resolved_file_name = file_name or ""

        if isinstance(source, bytes):
            if not resolved_file_name:
                raise ValueError("file_name must be provided when parsing from bytes.")
            
            # Preserve the extension for MarkItDown format routing
            _, ext = os.path.splitext(resolved_file_name)
            try:
                # delete=False is needed on Windows to ensure we can close the file and let MarkItDown open it
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                    temp_file.write(source)
                    target_path = temp_file.name
                temp_file_created = True
                logger.debug(f"Created temp file for byte parsing: {target_path}")
            except Exception as e:
                raise FileConversionError("Failed to prepare raw bytes for conversion", e)
        else:
            target_path = os.path.abspath(source)
            if not os.path.exists(target_path):
                raise FileNotFoundError(f"Source file not found at: {target_path}")
            resolved_file_name = os.path.basename(target_path)

        start_time = time.time()
        try:
            logger.info(f"Parsing document: {resolved_file_name}")
            result = self.md.convert(target_path)
            duration_ms = int((time.time() - start_time) * 1000)

            # Gather metadata
            _, ext = os.path.splitext(resolved_file_name)
            ext = ext.lower()
            mime_overrides = {
                '.csv': 'text/csv',
                '.json': 'application/json',
                '.md': 'text/markdown',
                '.markdown': 'text/markdown',
            }
            if ext in mime_overrides:
                mime_type = mime_overrides[ext]
            else:
                mime_type, _ = mimetypes.guess_type(resolved_file_name)
                if not mime_type:
                    mime_type = "application/octet-stream"

            file_size = os.path.getsize(target_path)

            metadata: Dict[str, Any] = {
                "fileName": resolved_file_name,
                "fileSize": file_size,
                "mimeType": mime_type,
                "parsedDurationMs": duration_ms
            }

            # If markitdown extracted a title, include it
            if hasattr(result, 'title') and result.title:
                metadata["title"] = result.title

            return {
                "content": result.text_content,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"MarkItDown conversion failed for file: {resolved_file_name}", exc_info=True)
            raise FileConversionError(f"MarkItDown conversion failed for file: {resolved_file_name}", e)
        finally:
            if temp_file_created and os.path.exists(target_path):
                try:
                    os.remove(target_path)
                    logger.debug(f"Removed temp file: {target_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {target_path}: {e}")
