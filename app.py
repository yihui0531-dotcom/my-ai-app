import streamlit as st
import pandas as pd
import plotly.express as px
import re
import json
from openai import OpenAI

st.set_page_config(page_title="AI带货话术评估系统", layout="wide")

# ================= 🔒 网页密码设置中心 =================
# 可以在下方双引号里，改成你想设置的任何密码（比如 "666888"）
WEB_PASSWORD = "1" 

# 初始化网页密码状态
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def check_password():
    if st.session_state["password_input"] == WEB_PASSWORD:
        st.session_state["password_correct"] = True
        del st.session_state["password_input"]  # 清除输入框内容
    else:
        st.session_state["password_correct"] = False
        st.error("🔑 密码错误，请重新输入！")

# 如果没输入过正确密码，直接锁死网页，强制展示登录界面
if not st.session_state["password_correct"]:
    st.title("🔒 欢迎使用系统（请先登录）")
    st.text_input("请输入专用的系统访问密码：", type="password", key="password_input", on_change=check_password)
    st.stop() # 密码不对就卡在这里，不向下执行
# =====================================================

# 🔓 密码正确，正式放行进入系统
st.title("🏆 顶级直播带货话术 AI 评估系统 (火山引擎直连版)")

# --- ⚙️ 左侧配置中心 ---
st.sidebar.header("⚙️ 评估配置中心")

ark_key = st.sidebar.text_input("1. 火山引擎 API_KEY", type="password", help="以 vapi- 开头的密钥")
ark_endpoint = st.sidebar.text_input("2. 模型接入点 ID (Endpoint)", placeholder="ep-2026xxxxxxxx-xxxxx")

default_criteria = "体验策略、功能策略、信任策略、稀缺性策略、激励策略、定位策略、承诺策略"
criteria = st.sidebar.text_area("自定义评判维度", value=default_criteria, height=100)
sensitive_words = st.sidebar.text_input("敏感词词库（用逗号隔开）", value="第一,最好,绝无仅有")

# --- 主界面 ---
text_input = st.text_area("请粘贴需要评估的主播话术文本：", height=300)

if st.button("🔥 开始全维度 AI 诊断"):
    if not text_input:
        st.warning("请先输入话术文本！")
    elif not ark_key or not ark_endpoint:
        st.error("请先在左侧配置中心填写你在火山引擎申请的『API_KEY』和『接入点ID』！")
    else:
        with st.spinner("火山引擎 DeepSeek 正在全力解析中，请稍候..."):
            try:
                client = OpenAI(
                    api_key=ark_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3"
                )
                
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
    "功能策略": "结合话术原文举例并深入点评...",
    "信任策略": "结合话术原文举例并深入点评...",
    "稀缺性策略": "结合话术原文举例并深入点评...",
    "激励策略": "结合话术原文举例并深入点评...",
    "定位策略": "结合话术原文举例并深入点评...",
    "承诺策略": "结合话术原文举例并深入点评..."
  }},
  "sensitive_risk": "发现敏感词或写无风险",
  "suggestions": ["建议1", "建议2"]
}}
"""
                completion = client.chat.completions.create(
                    model=ark_endpoint,
                    messages=[
                        {"role": "system", "content": "You are a professional livestreaming coach."},
                        {"role": "user", "content": master_prompt}
                    ],
                    temperature=0.3
                )
                
                ai_output = completion.choices[0].message.content
                
                if "</think>" in ai_output:
                    ai_output = ai_output.split("</think>")[-1]

                match = re.search(r'\{.*\}', ai_output, re.DOTALL)
                json_str = match.group(0) if match else ai_output
                res_json = json.loads(json_str)
                
                v_list = [k.strip() for k in criteria.replace("，", "、").replace(",", "、").split("、") if k.strip()]
                if "radar_data" not in res_json or not isinstance(res_json["radar_data"], dict):
                    res_json["radar_data"] = {k: 3 for k in v_list}

                st.balloons()
                st.success(f"🚀 诊断成功！综合评分：{res_json.get('total_score', 80)} 分")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("📊 策略雷达图分析")
                    r_values = [float(res_json["radar_data"].get(k, 3)) for k in v_list]
                    radar_df = pd.DataFrame(dict(r=r_values, theta=v_list))
                    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
                    st.plotly_chart(fig)
                    
                with col2:
                    st.subheader("🚫 敏感词合规风险")
                    st.warning(res_json.get("sensitive_risk", "无风险"))
                    
                st.subheader("📝 各维度详细举例点评")
                if isinstance(res_json.get("comments"), dict) and res_json.get("comments"):
                    for k, v in res_json.get("comments", {}).items():
                        st.markdown(f"**【{k}】**：{v}")
                else:
                    st.text(ai_output)
                    
                st.subheader("💡 导师优化建议")
                sugs = res_json.get("suggestions", [])
                for sug in sugs: 
                    st.info(sug)
                    
            except Exception as e:
                st.error(f"连接火山引擎出错，请检查配置参数是否正确。错误详情: {e}")
