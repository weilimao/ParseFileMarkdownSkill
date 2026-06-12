import argparse
import os
import sys
import logging
from markitdown_skill import MarkItDownParser
from markitdown_skill.utils.logger import setup_logger

logger = setup_logger("markitdown_skill.cli")

def main():
    """
    Main CLI entrypoint for markitdown-skill.
    """
    parser = argparse.ArgumentParser(
        description="MarkItDown Skill: Instantly convert documents to structured Markdown for LLMs."
    )
    parser.add_argument("file_path", help="Path to the document to parse.")
    parser.add_argument("-s", "--save", action="store_true", help="Save the Markdown output next to the source file.")
    parser.add_argument("-o", "--output", help="Explicit path where to save the generated Markdown output.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging.")
    parser.add_argument("--llm", action="store_true", help="Enable LLM enhancement (multimodal OCR/audio transcription). Requires OPENAI_API_KEY.")

    args = parser.parse_args()

    # Set logger level
    skill_logger = logging.getLogger("markitdown_skill")
    if args.verbose:
        skill_logger.setLevel(logging.DEBUG)
        for handler in skill_logger.handlers:
            handler.setLevel(logging.DEBUG)
    else:
        skill_logger.setLevel(logging.INFO)
        for handler in skill_logger.handlers:
            handler.setLevel(logging.INFO)

    file_path = os.path.abspath(args.file_path)
    if not os.path.exists(file_path):
        logger.error(f"Target file not found: {file_path}")
        sys.exit(1)

    llm_client = None
    llm_model = None
    
    if args.llm:
        if not os.environ.get("OPENAI_API_KEY"):
            logger.error("Environment variable OPENAI_API_KEY is not set. Required for --llm mode.")
            sys.exit(1)
        try:
            from openai import OpenAI
            llm_client = OpenAI()
            llm_model = "gpt-4o"
        except ImportError:
            logger.error("The 'openai' python package is required for --llm mode. Install it via pip.")
            sys.exit(1)

    try:
        skill_parser = MarkItDownParser(llm_client=llm_client, llm_model=llm_model)
        result = skill_parser.parse(file_path)

        logger.info(f"Parse successful! Metadata: {result['metadata']}")

        # Determine target output route
        dest_path = None
        if args.output:
            dest_path = os.path.abspath(args.output)
        elif args.save:
            folder = os.path.dirname(file_path)
            base, _ = os.path.splitext(os.path.basename(file_path))
            dest_path = os.path.join(folder, f"{base}_parsed.md")

        if dest_path:
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(result["content"])
            logger.info(f"Saved Markdown file to: {dest_path}")
        else:
            # Print Markdown directly to stdout
            print(result["content"])

    except Exception as e:
        logger.error(f"Error parsing document: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
