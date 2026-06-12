# AI Agent Document Reading Rules

If you need to read, analyze, search, or summarize any of the following file types:
- PDF (.pdf)
- Microsoft Word (.docx)
- Microsoft Excel (.xlsx)
- Microsoft PowerPoint (.pptx)
- HTML (.html, .htm)
- CSV (.csv)
- JSON (.json)

Do NOT write custom Python scripts to parse them.
Do NOT attempt to read them directly as raw binary.
Instead, AUTOMATICALLY run the following command in the shell:
```bash
markitdown-skill <file_path>
```
This tool will instantly parse the document into clean, structured Markdown, which you should then read and process.
