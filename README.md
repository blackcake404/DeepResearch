# 基于 Deepseek 的 DeepResearch

该 DeepResearch Repo 基于 Deepseek，旨在实现类似 Manus 的智能研究与报告生成能力，探索不具备深度研究能力的 LLM 在 DeepResearch 中的可能性。

## 项目简介

本项目以 LLM 与 MCP 框架为核心，实现自动化的信息检索、数据分析、资料获取和报告生成。用户只需提出问题，系统会自动选择最合适的工具，分步获取、整合信息，最终输出结构化的报告内容 (Markdown)。支持自定义工具接入和多轮推理，并兼容多种数据源（如网页、图片等）。

## 主要功能

- 基于 Deepseek Chat 实现智能问答和推理
- 可扩展工具链，支持添加自定义数据采集和处理
- 自动调用和组合外部 API 进行多轮信息检索
- 自动生成结构化、可读性强的 Markdown 报告
- 日志记录与调试支持

## 技术栈

- Python
- Deepseek Chat & Qwen-2.5-vl（LLM）
- OpenAI API
- Docker（部分组件如 searxng-docker 支持容器化部署）

## 安装与运行

1. 克隆代码仓库

   ```bash
   git clone https://github.com/blackcake404/DeepResearch.git
   cd DeepResearch
   ```

2. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

3. 运行 DeepResearch MCP Client

   ```bash
   python mcp_client.py
   ```

4. （可选）部署 SearXNG 搜索服务 (https://github.com/searxng/searxng-docker?tab=readme-ov-file)

## 使用方式

- 运行 Client 后，输入问题或任务目标
- 支持多轮问答，自动推理和工具调用
- 结果以 Markdown 格式输出，便于后续整理和分享

## 目录结构

- `mcp_client.py`：主入口
- `mcp4search.py`：核心智能检索与报告生成逻辑
- `prompts.py`：系统提示语与任务流程定义
- `searxng-docker/`：容器化搜索引擎组件

## 许可协议

目前未指定开源协议，部分组件如 searxng-docker 遵循其原有 LICENSE。

## 贡献说明

共同进步共同学习，如有 bug 还望大佬们不吝赐教！欢迎提交 issue 和 PR，一起完善智能研究与报告自动化能力！

---

项目主页：[https://github.com/blackcake404/DeepResearch](https://github.com/blackcake404/DeepResearch)