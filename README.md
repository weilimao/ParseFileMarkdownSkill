# MarkItDown Document Parser Skill (AI 文档统一解析技能)

这是一个基于 Microsoft 开源 `markitdown` 引擎构建的高工程化、开箱即用的 AI 文档解析 Skill。旨在将市面上绝大部分常见文档（PDF、Word .docx、Excel .xlsx、PowerPoint .pptx、HTML、CSV、JSON 等）一键并高效地解析为结构清晰、token 消耗低的 **Markdown 格式**，以便于大语言模型（LLM）更好地消化和提取内容，省去 AI 每次阅读文件时自己写脚本提取内容的步骤。

本 Skill 已提供命令行工具 (CLI)、Python API 调用、以及专门适配 Gemini/Antigravity 架构的 **Native Skill (本地技能插件)** 配置文件。

---

## 核心特性
* **超强格式兼容**：支持 PDF、Word (.docx)、Excel (.xlsx)、PowerPoint (.pptx)、HTML、TXT、CSV、JSON 等各类日常办公与开发文档。
* **智能结构优化**：利用 `markitdown` 进行语义解析，精准还原文档的表格线、标题层级、无序/有序列表等。
* **支持 Native Skill 模式**：内置 Antigravity 的技能配置，安装后任何对接该配置的 AI 工具（例如 Antigravity 2.0、Claude Code 等）都将自动获得该技能，并在分析文件时自动在后台调用，无需用户下达解析指令。
* **支持 Stdio MCP 模式**：适配 Model Context Protocol，可无缝注册为 Cursor、Claude Desktop 等主流 AI 平台的工具。
* **原生支持 `bytes` 级解析**：底层对二进制流与文件路径兼容，可通过临时文件安全转接，解决流式传输场景下的解析需求。

---

## 项目结构
```
e:/GPT/ParseFileSkill/
├── requirements.txt           # 项目运行依赖
├── pyproject.toml             # Python 现代打包配置（可将 CLI 脚本注册到系统 PATH）
├── README.md                  # 本说明文档
├── markitdown_skill/          # 核心代码包
│   ├── __init__.py            # 公共 API 导出
│   ├── cli.py                 # 终端命令行工具接口
│   ├── mcp_server.py          # Model Context Protocol (MCP) 适配服务端
│   ├── core/
│   │   ├── exceptions.py      # 统一的异常定义
│   │   └── parser.py          # MarkItDownParser 核心包装器
│   └── utils/
│       └── logger.py          # 结构化日志输出工具
└── tests/
    └── test_parser.py         # 自动化单元与集成测试套件
```

---

## 快速开始

### 1. 环境准备与安装
首先在项目根目录下，安装依赖包并以本地可编辑模式安装该 Skill。这会将 `markitdown-skill` 和 `markitdown-mcp` 的可执行文件自动注册到您的 Python 可执行文件路径下：

```bash
# 安装底层解析依赖
pip install -r requirements.txt

# 以本地可编辑包形式安装本 Skill
pip install -e .
```

> **注意**：如果您在安装时遇到 `WARNING: The scripts ... are installed in '...' which is not on PATH`，请将相应的 `Scripts` 文件夹路径添加至您系统的环境变量 `PATH` 中。

---

## 使用指南

### 1. 命令行测试 (CLI)
安装完成后，您可以在系统的任意位置直接通过命令行调用此工具解析文档：

```bash
# 解析文档并直接输出 Markdown 纯文本到控制台
markitdown-skill path/to/document.pdf

# 解析文档并将结果保存为 Markdown 文件（会在当前文件夹下生成 document_parsed.md）
markitdown-skill path/to/document.docx --save

# 启用 LLM 视觉辅助解析（比如提取 PPTX/PDF 中的图片描述。需配置 OPENAI_API_KEY）
markitdown-skill path/to/presentation.pptx --llm
```

### 2. 在 Python 代码中集成
您可以将本包引入您的 Python AI Agent 项目中作为工具调用：

```python
from markitdown_skill import MarkItDownParser

# 1. 实例化解析器 (可传入可选的 llm_client 和 llm_model 进行视觉增强)
parser = MarkItDownParser()

# 2. 传入本地路径解析
result = parser.parse("E:/report.xlsx")
print("文件名:", result["metadata"]["fileName"])
print("MIME 类型:", result["metadata"]["mimeType"])
print("内容:\n", result["content"])  # 输出已格式化为 Markdown 表格的 Excel 内容

# 3. 传入二进制流 bytes 进行内存解析 (必须指定 file_name 以辅助确定解析格式)
raw_bytes = b"Name,Age,Role\nAlice,30,Engineer"
byte_result = parser.parse(raw_bytes, file_name="data.csv")
print(byte_result["content"])
```

---

## AI 自动调用集成配置

### 方案 A：集成到 Antigravity / Gemini 平台 (Native Skill)
如果您希望本地的 **Antigravity CLI、Antigravity 2.0、Antigravity IDE** 等 AI 工具自动识别并调用该 Skill：

请拷贝本仓库中自带的 `plugins/markitdown-parser-plugin` 目录至您的本地 `.gemini` 插件配置目录下：
1. 复制源目录：本仓库中的 [plugins/markitdown-parser-plugin/](file:///e:/GPT/ParseFileSkill/plugins/markitdown-parser-plugin)
2. 本地目标配置目录：`C:\Users\韦礼貌\.gemini\config\plugins\markitdown-parser-plugin\`
3. **效果**：将文件夹复制过去并重启 AI 后，AI 系统载入时会自动加载 `parse_document` 技能，当您让它分析文档时，它便会自动调度该 Skill 获取内容。


### 方案 B：集成到 Claude Code (CLAUDE.md Skill 配置)
如果您希望 **Claude Code** 命令行工具在分析文档时自动调用本 Skill：
1. 请拷贝本仓库根目录下的 [CLAUDE.md](file:///e:/GPT/ParseFileSkill/CLAUDE.md) 规则文件至您具体开发项目的根目录下。
2. **效果**：Claude Code 在启动时会自动读取该文件中的指导规则。当您让它分析或总结 PDF、Word、Excel 等文件时，它会自觉在后台运行 `markitdown-skill <file_path>` 并读取转换后的 Markdown 内容，不再需要您手动告诉它去运行。

### 方案 C：集成到 Cursor / CodeX 编译器 (.cursorrules Skill 配置)
如果您希望 **Cursor** 或 **CodeX** 编辑器中的 AI 自动调用本 Skill：
1. 请拷贝本仓库根目录下的 [.cursorrules](file:///e:/GPT/ParseFileSkill/.cursorrules) 规则文件至您开发项目的根目录下。
2. **效果**：Cursor/CodeX 的 AI 助手在处理非纯文本文件时，会根据规则指示，自动通过终端命令 `markitdown-skill` 去获取结构化 Markdown，实现全自动的解析与阅读。

---

## 运行测试
项目带有内置的 `unittest` 测试，它将自动生成临时测试文件并调用接口校验转化后的 Markdown 内容：
```bash
python -m unittest tests/test_parser.py
```
