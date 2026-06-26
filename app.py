import streamlit as st
import pandas as pd
import plotly.express as px
import re
import json
from openai import OpenAI

st.set_page_config(page_title="AI带货话术评估系统", layout="wide")

# ================= 🔒 网页密码设置中心 =================
# 在下方双引号里，改成你想设置的任何密码（例如 "888888"）
WEB_PASSWORD = "888888" 
# =====================================================

st.title("🏆 顶级直播带货话术 AI 评估系统 (火山引擎直连版)")

# --- ⚙️ 左侧配置中心 ---
st.sidebar.header("⚙️ 评估配置中心")

# 1. 在左侧最上方加入密码框
input_web_password = st.sidebar.text_input("🔑 系统访问密码", type="password")
st.sidebar.caption("💡 提示：内部系统，需填写正确密码方可激活诊断。")

st.sidebar.markdown("---") # 分割线

ark_key = st.sidebar.text_input("1. 火山引擎 API_KEY", type="password", help="以 vapi- 开头的密钥")
ark_endpoint = st.sidebar.text_input("2. 模型接入点 ID (Endpoint)", placeholder="ep-2026xxxxxxxx-xxxxx")

default_criteria = "体验策略、功能策略、信任策略、稀缺性策略、激励策略、定位策略、承诺策略"
criteria = st.sidebar.text_area("自定义评判维度", value=default_criteria, height=100)
sensitive_words = st.sidebar.text_input("敏感词词库（用逗号隔开）", value="第一,最好,绝无仅有")

# --- 主界面 ---
text_input = st.text_area("请粘贴需要评估的主播话术文本：", height=300)

if st.button("🔥 开始全维度 AI 诊断"):
    # 🤫 优雅拦截核心逻辑：只有密码完全正确，且输入了文本和配置，才会向下执行大模型调用。
    # 如果密码不对，网页只会安静地刷新，绝不报错、绝不吐出红字，也绝不调用大模型。
    if input_web_password == WEB_PASSWORD and text_input and ark_key and ark_endpoint:
        
        with st.spinner("火山引擎 DeepSeek 正在全力解析中，请稍候..."):
            try:
                # 初始化火山引擎 Ark 客户端
                client = OpenAI(
                    api_key=ark_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3"
                )
                
                # 组装完美提示词
                master_prompt = f"""你是一个顶级的旅游直播带货话术教练。请对以下话术进行全维度深度评估。

【待评估的话术文本】：
{text_input}

【评估维度】：
{criteria}

【合规敏感词（若话术中包含以下词汇，请在 sensitive_risk 中指出）】：
{sensitive_words}

【核心死命令】：
你必须且只能输出严格的 JSON 格式。直接以大括号 {{ 开头，以大括号 }} 结尾，千万不要包含任何 ```json 等Markdown标记！

必须严格按照以下标准的 JSON 格式输出：
{{
  "total_score": 85,
  "radar_data": {{
    "体验策略": 4,
    "功能策略": 3,
    "信任策略": 5,
    "稀缺性策略": 4,
    "激励策略": 4,
    "定位策略": 3,
    "承诺策略": 2
  }},
  "comments": {{
    "体验策略": "结合话术原文举例并深入点评...",
    "功能策略": "结合话术
