# AI 聊天助手

一个基于 DeepSeek API 的命令行 AI 聊天助手，支持多轮对话、角色扮演、流式输出。

## 功能

- 多轮对话（记住上下文）
- 多个预设角色（Python 老师、心理咨询师、毒舌吐槽大师、小俞等）
- 自定义角色（输入自己的系统提示词）
- 流式输出（逐字显示）
- 清空历史、切换角色

## 环境要求

- Python 3.10+
- DeepSeek API Key

## 安装

1. 创建虚拟环境
   ```bash
   python -m venv venv
   venv\Scripts\activate
   
2. 安装依赖
    ```bash
   pip install -r requirements.txt

3. 配置API Key
    在项目根目录创建 .env文件:
    DEEPSEEK_API_KEY=你的API_KEY
