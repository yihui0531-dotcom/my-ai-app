import streamlit as st
import pandas as pd
import plotly.express as px
import re
import json
from openai import OpenAI

st.set_page_config(page_title="AI带货话术评估系统", layout="wide")

# ================= 🔒 网页密码设置中心 =================
# 你可以在下方双引号里，改成你想设置的任何密码（例如 "888888"）
WEB_PASSWORD = "1" 
# =====================================================

st.title("🏆 直播带货话术 AI 评估系统 (专业级直连版)")

# --- ⚙️ 左侧配置中心 ---
st.sidebar.header("⚙️ 评估配置中心")

# 1. 在左侧最上方加入网页访问密码框
input_web_password = st.sidebar.text_input("🔑 系统访问密码", type="password")

st.sidebar.markdown("---") 

# 🚀 自动填上你专属的 KEY 和 ID 作为默认值
ark_key = st.sidebar.text_input(
    "1. 火山引擎 API_KEY", 
    type="password", 
    value="ark-a266d71a-6ec6-4a57-bba0-bd517e6474b3-55690"
)
ark_endpoint = st.sidebar.text_input(
    "2. 模型接入点 ID", 
    value="ep-20260626232937-5x6hg"
)

default_criteria = "体验策略、功能策略、信任策略、稀缺性策略、激励策略、定位策略、承诺策略"
criteria = st.sidebar.text_area("自定义评判维度", value=default_criteria, height=100)
sensitive_words = st.sidebar.text_input("敏感词词库（用逗号隔开）", value="第一,最好,绝无仅有")

# --- 主界面逻辑控制 ---
if input_web_password != WEB_PASSWORD:
    st.markdown("### ")
    st.info("👈 **【系统未解锁】** 请先在左侧侧边栏输入正确的『**系统访问密码**』，解锁后即可开启主播话术评估系统。")
    st.stop()

# 🔓 密码正确，展示主界面
text_input = st.text_area("请粘贴需要评估的主播话术文本：", height=300)

if st.button("🔥 开始全维度 AI 诊断"):
    if not text_input:
        st.warning("请先输入话术文本！")
    elif not ark_key or not ark_endpoint:
        st.error("请先在左侧配置中心填写API_KEY和接入点ID！")
    else:
        with st.spinner("百亿级带货操盘手 DeepSeek 正在深度审计话术，请稍候..."):
            try:
                client = OpenAI(
                    api_key=ark_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3"
                )
                
                # 🧠 顶级MCN操盘手级别提示词（彻底剥离 f-string 避免语法冲突）
                master_prompt = (
                    "你是一个拥有10年电商直播经验、带货GMV超百亿的『顶级旅游直播带货操盘手/话术总监』。\n"
                    "请对以下话术文本进行毒舌、严苛、极其专业的全维度深度审计。\n\n"
                    "【当前待评估的话术文本】:\n" + str(text_input) + "\n\n"
                    "【核心评判维度与硬性指标】:\n" + str(criteria) + "\n"
                    "（注意：点评时必须严格围绕上述维度。在分析时，请将这些维度与“邮轮、高端度假、海岛游、境外游”等旅游产品特质深度绑定。）\n\n"
                    "【合规审查词库】:\n" + str(sensitive_words) + "\n\n"
                    "【🔥 打分与点评的专业度硬性死命令（思维钢印）】:\n"
                    "1. 严苛打分：拒绝通货膨胀！字面流畅但缺乏逼单钩子的平庸话术一律判为不及格（50分左右）。只有包含“场景画面、多重信任背书、极强迫切感、无法拒绝的无忧承诺”的现象级话术才能获得 85 分以上。\n"
                    "2. 拒绝空话：在 comments 字段中，每个维度的点评必须包含“金句摘录”与“心理学拆解”。格式必须是：【话术诊断】指出具体哪一句话写得好或差 + 【用户心理】拆解这句话触动了消费者的什么痛点 + 【改写方案】如果是你来带货，这句话应该怎么升级。\n"
                    "3. 纯净 JSON：你必须且只能输出严格的 JSON 格式，以大括号 { 开头，以大括号 } 结尾，绝对不能包含 ```json 标记。\n\n"
                    "必须严格按照以下标准的 JSON 格式输出（字段键名必须完全一致）:\n"
                    "{\n"
                    '  "total_score": 58,\n'
                    '  "radar_data": {\n'
                    '    "体验策略": 3,\n'
                    '    "功能策略": 2,\n'
                    '    "信任策略": 4,\n'
                    '    "稀缺性策略": 2,\n'
                    '    "激励策略": 3,\n'
                    '    "定位策略": 3,\n'
                    '    "承诺策略": 1\n'
                    "  },\n"
                    '  "comments": {\n'
                    '    "体验策略": "【话术诊断】主播提到了‘躺在阳台看海’，但缺乏画面细节。【用户心理】度假消费者买的是对美好生活的向往，不仅要看海，还要有痛点对比。【改写方案】建议升级为：‘想象一下，当别人还在写字楼里挤电梯，你已经躺在皇家加勒比的阳台房里，海风吹着，手里冰可乐冒着气泡...’",\n'
                    '    "功能策略": "结合话术原文举例，进行【话术诊断】+【用户心理】+【改写方案】层层拆解...",\n'
                    '    "信任策略": "结合话术原文举例，进行【话术诊断】+【用户心理】+【改写方案】层层拆解...",\n'
                    '    "稀缺性策略": "结合话术原文举例，进行【话术诊断】+【用户心理】+【改写方案】层层拆解...",\n'
                    '    "激励策略": "结合话术原文举例，进行【话术诊断】+【用户心理】+【改写方案】层层拆解...",\n'
                    '    "定位策略": "结合话术原文举例，进行【话术诊断】+【用户心理】+【改写方案】层层拆解...",\n'
                    '    "承诺策略": "结合话术原文举例，进行【话术诊断】+【用户心理】+【改写方案】层层拆解..."\n'
                    "  },\n"
                    '  "sensitive_risk": "例：发现‘第一’涉嫌违反广告法；或写无风险",\n'
                    '  "suggestions": [\n'
                    '    "高阶操盘手建议1：在话术第X段引入‘痛点对比法’，先放大日常工作的劳累，再切入邮轮的松弛感。",\n'
                    '    "高阶操盘手建议2：当前承诺策略几乎为零，必须强调‘不激活全额退、过期自动退’来降低下单抗拒点。"\n'
                    "  ]\n"
                    "}"
                )

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

                # --- 🎨 前端渲染 ---
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
                    
                st.subheader("📝 操盘手级各维度详细审计")
                if isinstance(res_json.get("comments"), dict) and res_json.get("comments"):
                    for k, v in res_json.get("comments", {}).items():
                        st.markdown(f"**【{k}】**：{v}")
                else:
                    st.text(ai_output)
                    
                st.subheader("💡 导师高阶优化建议")
                sugs = res_json.get("suggestions", [])
                for sug in sugs: 
                    st.info(sug)
                    
            except Exception as e:
                st.error(f"分析失败，请检查参数或大模型返回格式。错误详情: {e}")
