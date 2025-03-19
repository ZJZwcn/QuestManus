# 🪼 QuestManus  - 求索之路

<div align="center">
  <img src="app\GUI\config\icons\app.png" alt="QuestManus Logo" width="200">
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README_.md) | [中文](README.md)

## 🌟 Project Introduction

QuestManus is a powerful and versatile AI assistant framework developed based on OpenManus. It integrates a variety of tools and large language models, capable of handling various needs ranging from simple queries to complex tasks, including code execution, web search, media processing, etc. Through a multi-model collaboration mechanism, QuestManus can efficiently complete various tasks and provide a smooth user experience.

### Core Features

- **Multi-model Collaboration**：The thinking large language model is responsible for analysis and planning, the execution large language model is responsible for specific operations, and the visual large language model processes image content.
- **Tool Invocation Architecture**： Implements a flexible tool invocation mechanism based on ToolCallAgent.
- **Rich Toolset**：Supports various tools such as Python execution, web browsing, file operation, search, media processing, etc.
- **Media Processing Capability**：Supports image analysis and document processing, and implements a multi-model collaboration processing flow.
- **Friendly Graphical Interface**：Provides an intuitive user interaction experience, supporting file upload and real-time feedback.

## 🚀 Quick Start

### System Requirements

- Python 3.12+
- Windows System
- CUDA support (recommended for acceleration of model inference)

### Installation Steps

1. Clone Repository

```bash
git clone https://github.com/yourusername/Questmanus.git
cd Questmanus
``` 

2. Create Virtual Environment

```bash
conda create -n Questmanus python=3.12
conda activate Questmanus
``` 

3. Install Dependencies

```bash
pip install -r requirements.txt
``` 

4. Configure API Keys

Copy the example configuration file and fill in your API keys:
```bash
config/config.toml
``` 
Edit the config/config.toml file and fill in your API keys and model configurations.

### Launch QuestManus
<div align="center">
  <img src="img\界面.png" alt="Quest">
</div>

Launch the GUI:
```bash
python QuestManus_main.py
``` 

## 🧠 Working Principles

### QuestManus Tool Invocation Architecture:

- User Input Processing: Receives user's text commands or uploaded files
- Tool Selection: Thinking LLM analyzes user needs and selects appropriate tools
- Tool Execution: Invokes corresponding tools to complete tasks, such as executing code, searching information, processing media, etc.
- Result Feedback: Returns execution results to users and provides follow-up suggestions

### Multi-Model Collaboration Mechanism

- Thinking LLM: Responsible for understanding user needs, planning task steps, selecting appropriate tools
- Execution LLM: Responsible for executing specific operations, such as file saving, system operations, etc.
- Vision LLM: Responsible for analyzing image content and extracting visual information

## 🛠️ Main Components

- Manus Agent: System core, inherits from ToolCallAgent, manages tool invocation and execution process
- Tool Collection: Contains various functional tools, such as Python execution, web browsing, media processing, etc.
- LLM Manager: Manages different large model calls, including thinking, execution, and vision models
- GUI Interface: Provides user-friendly interaction experience, supports file upload and real-time feedback

## 📝Usage Examples

### Example 1：Web Search

```bash
Find the latest research progress on quantum computing
``` 
QuestManus will call the search tool to obtain relevant information.

### Example 2: Code Execution

```bash
Write a Python function to calculate the nth term of the Fibonacci sequence and test the result when n = 10
``` 
QuestManus will use the Python execution tool to write and run the code.

### Example 3: Image Analysis

```bash
Analyze the content of this image and provide a detailed description
``` 
QuestManus will use the media processing tool. First, the visual large language model analyzes the image content, and then the thinking large language model beautifies the results.

### Example 4: Document Processing
```bash
Summarize the main content of this document and save the result
``` 
QuestManus will use the media processing tool to analyze the document content and automatically save the processed result.

## 📊 System Architecture

QuestManus adopts a modular design and mainly includes the following core components:

``````text
QuestManus/
├── app/
│   ├── __pycache__/
│   ├── agent/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── manus.py
│   │   ├── planning.py
│   │   ├── react.py
│   │   ├── swe.py
│   │   └── toolcall.py
│   ├── flow/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── flow_factory.py
│   │   └── planning.py
│   ├── GUI/
│   │   ├── __pycache__/
│   │   ├── components/
│   │   ├── config/
│   │   ├── workers/
│   │   ├── __init__.py
│   │   └── main_window.py
│   ├── prompt/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── manus.py
│   │   ├── planning.py
│   │   ├── swe.py
│   │   └── toolcall.py
│   ├── tool/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── app_launcher.py
│   │   ├── baidu_search.py
│   │   ├── base.py
│   │   ├── bash.py
│   │   ├── browser_use_tool.py
│   │   ├── create_chat_completion.py
│   │   ├── edge_search.py
│   │   ├── file_saver.py
│   │   ├── google_search.py
│   │   ├── math_tool.py
│   │   ├── media_process.py
│   │   ├── planning.py
│   │   ├── python_execute.py
│   │   ├── qmusic_control.py
│   │   ├── Redbook_summarize.py
│   │   ├── run.py
│   │   ├── str_replace_editor.py
│   │   ├── system_operation.py
│   │   ├── terminate.py
│   │   ├── tool_collection.py
│   │   ├── wechat_message.py
│   │   └── wechat_official_account.py
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── llm.py
│   ├── logger.py
│   └── schema.py
├── config/
│   └── config.toml
├── img/
│   └── 界面.png
├── logs/
│   ├── 20250318224403.log
│   ├── 20250319000819.log
│   ├── 20250319001726.log
│   ├── 20250319002620.log
│   ├── 20250319002653.log
│   ├── 20250319003337.log
│   ├── 20250319003431.log
│   ├── 20250319004821.log
│   ├── 20250319005623.log
│   ├── 20250319010553.log
│   ├── ......
├── temp/
├── explorer.exe
├── LICENSE
├── QuestManus_main.py
├── QuestManus_README.md
├── QuestManus_README_.md
└── requirements.txt

``````

### Core Components

#### Manus Agent (Manus)
- The core agent of the system, inheriting from ToolCallAgent.
- Manages tool invocation and execution processes.
- Provides a unified entry for user instruction processing.

#### LLM 管理器 (LLM)
- Manages the invocation of thinking large language models, execution large language models, and visual large language models.
- Provides a unified model invocation interface.

#### Tool Set (ToolCollection)
- Manages various built-in tools, such as Python execution, web browsing, media processing, etc.
- Provides a unified tool registration and invocation interface.

#### Media Processing Tool (MediaProcessTool)
- Processes image and document files.
- Supports multi-model collaboration: the visual large language model analyzes images, and the thinking large language model processes the results.
- Automatically detects saving needs and executes saving operations.

#### GUI Interface (QuestManusGUI)
- Provides a user-friendly interaction interface.
- Supports file upload and real-time feedback.
- Displays the execution process and results.

### Data Flow
User Input → Manus Agent → Thinking Large Language Model → Tool Selection → Tool Execution → Result Processing → Result Return

## ⚙️ Configuration System

QuestManus uses a TOML format configuration file and supports the following configuration items:

### Model Configuration

```python
[llm]
api_key = "your_api_key"
base_url = "https://api.openai.com/v1"
api_type = "openai"
max_tokens = 4096
temperature = 0.0

[llm.thinking]
model = "deepseek-r1"
base_url = "https://api.deepseek.com/v1"
api_key = "your_deepseek_api_key"
api_type = "openai"
temperature = 0.2

[llm.execution]
model = "qwen-plus"
base_url = "https://api.qwen.ai/v1"
api_key = "your_qwen_api_key"
api_type = "openai"
temperature = 0.0

[llm.vision]
model = "claude-3-5-sonnet"
base_url = "https://api.anthropic.com/v1"
api_key = "your_anthropic_api_key"
api_type = "anthropic"
max_tokens = 4096
temperature = 0.0
```

## 📄  License
This project is licensed under the MIT license - for details, please refer to the LICENSE file.

## 🙏 Acknowledgments
- Thanks to the OpenManus team for providing the basic framework.
- Thanks to the Trae team for providing a powerful IDE.
- Thanks to all the developers who have contributed to this project.
