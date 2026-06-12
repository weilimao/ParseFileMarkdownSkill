---
name: parse_document
description: >
  CRITICAL: Call this tool automatically whenever you need to read, inspect, view, or analyze the content of a document file (such as PDF, Word .docx, Excel .xlsx, PowerPoint .pptx, HTML, CSV, JSON). This tool converts the file into clean, readable Markdown format.
---

# Parse Document

## When to use this skill

Call this skill automatically whenever you need to inspect or read the contents of any non-plain-text document, including PDF, DOCX, XLSX, PPTX, HTML, CSV, and JSON.

## Step 1: Run the parsing command

Execute the following shell command to parse the document:

```bash
markitdown-skill "<file_path>"
```

Replace `<file_path>` with the absolute path of the file to parse. The command will output the parsed Markdown content directly to stdout.
