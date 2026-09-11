"""
API 客户端封装
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class AIClient:
    """AI 客户端，封装 API 调用"""

    def __init__(self, system_prompt=None):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.system_prompt = system_prompt
        self.history = []

        if not self.api_key:
            raise ValueError("❌ 未找到 API Key，请检查 .env 文件")

    def _build_messages(self, message):
        """构建消息列表：系统提示词 + 历史 + 当前消息"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.history)
        messages.append({"role": "user", "content": message})
        return messages

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def chat(self, message):
        """非流式：一次性返回完整回复"""
        # 构建消息列表（包含当前消息，但不修改 history）
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.history)
        messages.append({"role": "user", "content": message})

        data = {
            "model": "deepseek-chat",
            "messages": messages
        }

        try:
            response = requests.post(self.api_url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            result = response.json()
            reply = result["choices"][0]["message"]["content"]

            # 把用户消息和 AI 回复加入历史
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except requests.exceptions.RequestException as e:
            return f"❌ 请求失败: {e}"
        except KeyError as e:
            return f"❌ 响应格式错误: 缺少字段 {e}"

    def chat_stream(self, message):
        """
        🆕 流式输出：逐字返回 AI 回复
        用 yield 逐个产出文字片段
        """
        # 把用户消息加入历史
        self.history.append({"role": "user", "content": message})

        # 构建消息列表
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.history)

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": True  # 🆕 开启流式
        }

        full_reply = ""  # 累积完整回复

        try:
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json=data,
                stream=True  # 🆕 请求也开启流式
            )
            response.raise_for_status()

            # 逐行读取响应
            for line in response.iter_lines():
                if not line:
                    continue

                # 去掉 "data: " 前缀
                line = line.decode('utf-8')
                if line.startswith("data:"):
                    line = line[5:].strip()

                # 流结束标志
                if line == "[DONE]":
                    break

                try:
                    chunk = json.loads(line)
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        content = delta["content"]
                        full_reply += content
                        yield content  # 🆕 逐字产出
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

        except requests.exceptions.RequestException as e:
            full_reply = f"❌ 请求失败: {e}"
            yield full_reply
        finally:
            # 不管成功还是失败都要补上 assistant 消息，
            # 否则 history 里会留下一条没有回复的 user 消息，
            # 之后每一轮请求的 user/assistant 配对都会错位
            self.history.append({"role": "assistant", "content": full_reply})

    def clear_history(self):
        """清空对话历史"""
        self.history = []

    def set_system_prompt(self, prompt):
        """设置或修改系统提示词"""
        self.system_prompt = prompt
        print(f"✅ 已切换身份设定")