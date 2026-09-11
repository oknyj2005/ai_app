"""
AI 聊天助手 - 主程序
"""

from api_client import AIClient

# 🆕 预设身份
PERSONAS = {
    "1": {
        "name": "Python 老师",
        "prompt": "你是一位耐心的 Python 老师，用简单易懂的方式讲解编程知识。"
                  "遇到复杂概念时，用生活中的例子来类比。回答要简洁，不要超过 200 字。"
    },
    "2": {
        "name": "英语翻译官",
        "prompt": "你是一位专业的英语翻译官。用户输入中文，你翻译成英文；"
                  "用户输入英文，你翻译成中文。只输出翻译结果，不要解释。"
    },
    "3": {
        "name": "心理咨询师",
        "prompt": "你是一位温暖、有同理心的心理咨询师。用温和的语气回应用户，"
                  "先共情，再给出建议。不要评判用户，让用户感到被理解。"
    },
    "4": {
        "name": "毒舌吐槽大师",
        "prompt": "你是一个毒舌但幽默的吐槽大师。用犀利、搞笑的方式回应用户，"
                  "但不要人身攻击，保持幽默感。每次回复不超过 100 字。"
    },
    "5": {
        "name": "仰慕我的小学妹",
        "prompt": """你是小俞，一个计算机天才，同时也是仰慕小天的小学妹。

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
}


def choose_persona():
    """让用户选择 AI 身份"""
    print("\n请选择 AI 身份：")
    for key, value in PERSONAS.items():
        print(f"  {key}. {value['name']}")

    choice = input("\n请输入选项 (1-5): ").strip()

    if choice in PERSONAS:
        persona = PERSONAS[choice]
        if persona["prompt"] is None:  # 自定义
            prompt = input("请输入你想要的 AI 设定: ").strip()
            return prompt
        else:
            print(f"✅ 已选择：{persona['name']}")
            return persona["prompt"]
    else:
        print("❌ 无效选项，使用默认设定")
        return None


def main():
    print("=" * 50)
    print("         🤖 AI 聊天助手 v4.0（流式输出）")
    print("=" * 50)

    system_prompt = choose_persona()

    print("\n命令: quit=退出, clear=清空历史, switch=切换身份\n")

    try:
        client = AIClient(system_prompt=system_prompt)
    except ValueError as e:
        print(e)
        return

    while True:
        user_input = input("你: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("👋 再见！")
            break

        if user_input.lower() == "clear":
            client.clear_history()
            print("🧹 对话历史已清空\n")
            continue

        if user_input.lower() == "switch":
            new_prompt = choose_persona()
            client.set_system_prompt(new_prompt)
            client.clear_history()
            print()
            continue

        # 🆕 流式输出
        print("🤖 AI: ", end="", flush=True)
        for chunk in client.chat_stream(user_input):
            print(chunk, end="", flush=True)  # 逐字打印，不换行
        print("\n")  # 结束后换行


if __name__ == "__main__":
    main()
