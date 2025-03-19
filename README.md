# 🪼 QuestManus - 求索之路

<div align="center">
  <img src="app\GUI\config\icons\app.png" alt="QuestManus Logo" width="200">
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README_.md) | [中文](README.md)

## 🌟 项目简介

QuestManus 是一个强大的多功能 AI 助手框架，基于 OpenManus 开发，集成了多种工具和大模型，能够处理从简单查询到复杂任务的各种需求，包括代码执行、网络搜索、媒体处理等。通过多模型协作机制，QuestManus 可以高效地完成各类任务，提供流畅的用户体验。

### 核心特性

- **多模型协作**：思考大模型负责分析规划，执行大模型负责具体操作，视觉大模型处理图像内容
- **工具调用架构**：基于 ToolCallAgent 实现灵活的工具调用机制
- **丰富的工具集**：支持 Python 执行、网页浏览、文件操作、搜索、媒体处理等多种工具
- **媒体处理能力**：支持图片分析和文档处理，实现多模型协作处理流程
- **友好的图形界面**：提供直观的用户交互体验，支持文件上传和实时反馈

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Windows 操作系统
- CUDA 支持 (推荐，用于加速模型推理)

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/Questmanus.git
cd Questmanus
``` 

2. 创建虚拟环境

```bash
conda create -n Questmanus python=3.12
conda activate Questmanus
``` 

3. 安装依赖

```bash
pip install -r requirements.txt
``` 

4. 配置 API 密钥

复制示例配置文件并填入您的 API 密钥：
```bash
config/config.toml
``` 
编辑 config/config.toml 文件，填入您的 API 密钥和模型配置。

### 启动QuestManus
<div align="center">
  <img src="img\界面.png" alt="Quest">
</div>

启动图形界面：
```bash
python QuestManus_main.py
``` 

## 🧠 工作原理

### QuestManus 采用了工具调用架构：

- 用户输入处理 ：接收用户的文本指令或上传的文件
- 工具选择 ：思考大模型分析用户需求，选择合适的工具
- 工具执行 ：调用相应工具完成任务，如执行代码、搜索信息、处理媒体等
- 结果反馈 ：将执行结果返回给用户，并提供后续建议

### 多模型协作机制

- 思考大模型 ：负责理解用户需求、规划任务步骤、选择合适工具
- 执行大模型 ：负责执行具体操作，如文件保存、系统操作等
- 视觉大模型 ：负责分析图像内容，提取视觉信息

## 🛠️ 主要组件

- Manus 代理 ：系统核心，继承自 ToolCallAgent，管理工具调用和执行流程
- 工具集合 ：包含各种功能工具，如 Python 执行、网页浏览、媒体处理等
- LLM 管理器 ：管理不同大模型的调用，包括思考、执行和视觉模型
- GUI 界面 ：提供用户友好的交互体验，支持文件上传和实时反馈

## 📝使用示例

### 示例1：网络搜索

```bash
查找关于量子计算的最新研究进展
``` 
QuestManus 将调用搜索工具获取相关信息。

### 示例2：代码执行

```bash
编写一个 Python 函数，计算斐波那契数列的第 n 项，并测试 n=10 的结果
``` 
QuestManus 将使用 Python 执行工具编写和运行代码。

### 示例3：图像分析

```bash
分析这张图片中的内容并提供详细描述
``` 
QuestManus 将使用媒体处理工具，先通过视觉大模型分析图片内容，再由思考大模型美化结果。

### 示例4：文档处理
```bash
总结这份文档的主要内容并保存结果
``` 
QuestManus 将使用媒体处理工具分析文档内容，并自动保存处理结果。

## 📊 系统架构

QuestManus 采用模块化设计，主要包含以下核心组件：

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

### 核心组件

#### Manus 代理 (Manus)
- 系统的核心代理，继承自 ToolCallAgent
- 管理工具调用和执行流程
- 提供统一的用户指令处理入口

#### LLM 管理器 (LLM)
- 管理思考大模型、执行大模型和视觉大模型的调用
- 提供统一的模型调用接口

#### 工具集合 (ToolCollection)
- 管理各种内置工具，如 Python 执行、网页浏览、媒体处理等
- 提供统一的工具注册和调用接口

#### 媒体处理工具 (MediaProcessTool)
- 处理图片和文档文件
- 支持多模型协作：视觉大模型分析图片，思考大模型处理结果
- 自动检测保存需求并执行保存操作

#### GUI 界面 (QuestManusGUI)
- 提供用户友好的交互界面
- 支持文件上传和实时反馈
- 显示执行过程和结果

### 数据流
用户输入 → Manus 代理 → 思考大模型 → 工具选择 → 工具执行 → 结果处理 → 结果返回

## ⚙️ 配置系统 

QuestManus 使用 TOML 格式的配置文件，支持以下配置项：
### 模型配置

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

## 📄 许可证
本项目采用 MIT 许可证 - 详情请参见 LICENSE 文件。

## 🙏 致谢
- 感谢 OpenManus 团队提供的基础框架
- 感谢 Trae 团队提供的强大IDE
- 感谢所有为本项目做出贡献的开发者
