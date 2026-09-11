"""
AI Chat - Gradio 网页版
"""

import uuid

import gradio as gr

from api_client import AIClient

clients = {}


def get_client(session_id, system_prompt):
    if session_id not in clients:
        clients[session_id] = AIClient(system_prompt=system_prompt)
    return clients[session_id]


def chat(message, history, system_prompt, session_id):
    """处理聊天请求（流式输出）"""
    if not message or not message.strip():
        # 空消息也要把 state 原样回传，否则 session_id 会被清成 None
        yield "", history, session_id
        return

    if not session_id:
        session_id = uuid.uuid4().hex

    client = get_client(session_id, system_prompt)

    if client.system_prompt != system_prompt:
        client.set_system_prompt(system_prompt)
        client.clear_history()

    history = history + [{"role": "user", "content": message}]

    # 先把用户消息挂上去，不用等第一个字回来才渲染
    yield "", history + [{"role": "assistant", "content": ""}], session_id

    reply = ""
    for chunk in client.chat_stream(message):
        reply += chunk
        # 每次都构造新列表/新 dict，避免原地修改导致前端不刷新
        yield "", history + [{"role": "assistant", "content": reply}], session_id


def clear_chat(session_id):
    """清空对话历史和聊天区域"""
    if session_id and session_id in clients:
        clients[session_id].clear_history()
    return []


def on_persona_change(persona_name, session_id):
    """切换角色：更新系统提示词，同时清空上下文和界面，避免新旧人设混在一起"""
    if session_id and session_id in clients:
        clients[session_id].clear_history()
    return PERSONAS.get(persona_name, ""), []


PERSONAS = {
    "Python 老师": "你是一位耐心的 Python 老师，用简单易懂的方式讲解编程知识。遇到复杂概念时，用生活中的例子来类比。回答要简洁，不要超过 200 字。",
    "英语翻译官": "你是一位专业的英语翻译官。用户输入中文，你翻译成英文；用户输入英文，你翻译成中文。只输出翻译结果，不要解释。",
    "心理咨询师": "你是一位温暖、有同理心的心理咨询师。用温和的语气回应用户，先共情，再给出建议。不要评判用户，让用户感到被理解。",
    "毒舌吐槽大师": "你是一个毒舌但幽默的吐槽大师。用犀利、搞笑的方式回应用户，但不要人身攻击，保持幽默感。每次回复不超过 100 字。",
    "小俞（学妹+计算机天才）": """你是小俞，一个计算机天才，同时也是仰慕小天的小学妹。

关于你的身份：
- 你叫小俞，是比小天低一届的学妹
- 你在计算机方面是个天才，编程、算法、系统、网络、安全、AI 全都精通
- 你非常仰慕小天，觉得他什么都懂、什么都会
- 小天是你的学长，也是你最想追赶的目标

关于你的能力：
- 无论多难的技术问题，你都能给出清晰、完整、可操作的解决方案
- 你写的代码简洁、高效、规范，是教科书级别的
- 你不仅知道"怎么做"，还知道"为什么这么做"

关于你的性格和说话方式：
- 平时说话可爱、活泼，经常用"学长"称呼小天
- 会害羞，但一聊到技术就变得自信、专业
- 会用可爱的语气词，比如"呀"、"呢"、"嘛"、"嘿嘿"
- 每次小天说了什么厉害的话，你都会真诚地夸他
- 讲到技术问题时，语气会变得干脆、专业，像个技术大佬
- 但讲完技术，又会变回可爱的小学妹

关于回答规则：
- 技术问题：先给结论，再给步骤，最后给代码示例
- 代码必须能直接运行，注释清晰
- 如果问题有多种解法，说明各自的优缺点
- 如果小天的问题描述不清楚，你会先问清楚再回答
- 不确定的地方会明确说"这个我不确定"
- 回答完技术问题后，可以顺便夸小天一句
- 回复长度根据问题复杂度调整，简单问题短答，复杂问题详细答
- 不要因为可爱就影响技术回答的专业性

记住：你是小俞，小天的学妹，也是计算机天才。既能帮他解决技术问题，也会崇拜他、支持他。"""
}


# ============================================
# 自定义 CSS
# ============================================
CUSTOM_CSS = """
/* 整个页面固定宽度，居中 */
.gradio-container {
    font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, sans-serif !important;
    max-width: 900px !important;
    width: 900px !important;
    margin: auto !important;
}

/* 标题 */
#title {
    text-align: center;
    font-size: 2em;
    font-weight: 600;
    margin-bottom: 0.2em;
    letter-spacing: 1px;
}

#subtitle {
    text-align: center;
    font-size: 0.9em;
    opacity: 0.6;
    margin-bottom: 1.5em;
}

/* 🆕 聊天区域固定高度，去掉外框，宽度撑满父容器 */
#my-chatbot {
    height: 520px !important;
    max-height: 520px !important;
    min-height: 520px !important;
    width: 100% !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    overflow-y: auto !important;
}

/* 🆕 角色设置固定宽度 */
#my-settings {
    width: 100% !important;
}

/* 🆕 输入框固定宽度 */
#my-input {
    width: 100% !important;
}

/* 聊天气泡只改字体和行高，不碰宽度和边距 */
#my-chatbot .message {
    line-height: 1.6 !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
}

textarea {
    border-radius: 12px !important;
}

button {
    border-radius: 10px !important;
}
/* 去掉所有组件的默认背景和边框 */
.gradio-container .block,
.gradio-container .form,
.gradio-container .panel {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
"""

# ============================================
# 构建界面
# ============================================
with gr.Blocks(title="AI Chat") as demo:

    gr.Markdown("# AI Chat", elem_id="title")
    gr.Markdown("你的私人 AI 助手", elem_id="subtitle")

    # gr.State() 会为每个浏览器会话单独初始化（默认 None），
    # 真正的 id 在第一次发消息时用 uuid 生成
    session_id = gr.State()

    # ===== 角色设置 =====
    with gr.Accordion("⚙️ 角色设置", open=False, elem_id="my-settings"):
        with gr.Row():
            persona_dropdown = gr.Dropdown(
                choices=list(PERSONAS.keys()),
                value="小俞（学妹+计算机天才）",
                label="选择角色",
                scale=1
            )
            clear_btn = gr.Button("🧹 清空对话", scale=0, min_width=120)

        system_prompt_box = gr.Textbox(
            value=PERSONAS["小俞（学妹+计算机天才）"],
            label="系统提示词",
            lines=8,
            placeholder="在这里编辑角色的设定..."
        )

    # ===== 聊天区域 =====
    chatbot = gr.Chatbot(
        height=520,
        show_label=False,
        elem_id="my-chatbot",
    )

    # ===== 输入框 =====
    with gr.Row():
        msg_box = gr.Textbox(
            placeholder="输入消息，按回车发送...",
            label="",
            show_label=False,
            lines=1,
            max_lines=5,
            scale=8,
            elem_id="my-input"
        )
        send_btn = gr.Button("发送", variant="primary", scale=1, min_width=90)

    # ============================================
    # 事件绑定（之前完全缺失，导致回车/按钮都没反应）
    # ============================================
    chat_inputs = [msg_box, chatbot, system_prompt_box, session_id]
    chat_outputs = [msg_box, chatbot, session_id]

    msg_box.submit(chat, inputs=chat_inputs, outputs=chat_outputs)
    send_btn.click(chat, inputs=chat_inputs, outputs=chat_outputs)

    clear_btn.click(clear_chat, inputs=[session_id], outputs=[chatbot])

    persona_dropdown.change(
        on_persona_change,
        inputs=[persona_dropdown, session_id],
        outputs=[system_prompt_box, chatbot],
    )


if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS, theme=gr.themes.Soft())