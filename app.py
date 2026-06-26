import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="AI带货话术评估系统", layout="wide")
st.title("🏆 顶级直播带货话术 AI 评估系统")

# 侧边栏配置
st.sidebar.header("⚙️ 评估配置中心")
password = st.sidebar.text_input("请输入访问密码", type="password")

default_criteria = "体验策略、功能策略、信任策略、稀缺性策略、激励策略、定位策略、承诺策略"
criteria = st.sidebar.text_area("自定义评判维度", value=default_criteria, height=100)
sensitive_words = st.sidebar.text_input("敏感词词库（用逗号隔开）", value="第一,最好,绝无仅有")

# Dify API 配置（记得把下面这行换成你自己的 Dify 密钥！）
DIFY_API_URL = "https://api.dify.ai/v1/workflows/run"
DIFY_API_KEY = "app-W35824eSzCai116xo9IecS8h"

if password == "123456": # 网页访问密码
    text_input = st.text_area("请粘贴需要评估的主播话术文本：", height=300)
    
    if st.button("🔥 开始全维度 AI 诊断"):
        if not text_input:
            st.warning("请先输入话术文本！")
        else:
            with st.spinner("AI 正在深度解析中，请稍候..."):
                headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
                data = {
                    "inputs": {"text": text_input, "criteria": criteria, "sensitive_words": sensitive_words},
                    "response_mode": "blocking",
                    "user": "streamlit_user"
                }
                try:
                    response = requests.post(DIFY_API_URL, json=data, headers=headers)
                    result = response.json()
                    
                    # 检查 Dify 的原始返回
                    if 'data' not in result or 'outputs' not in result['data']:
                        st.error(f"Dify未正常返回数据，请检查Dify工作流的END节点是否配置了输出。Dify返回信息：{result}")
                        st.stop()
                        
                    # 全自动兼容搜索：不管 Dify 把答案装在哪个口袋，全抓出来
ai_output = ""
if 'data' in result and 'outputs' in result['data']:
    outputs = result['data']['outputs']
    # 尝试所有可能的口袋名字
    ai_output = outputs.get('text') or outputs.get('answer') or outputs.get('output') or str(outputs)

# 如果工作流是 Chatflow 模式，答案可能会直接在最外层的 answer 里
if not ai_output and 'answer' in result:
    ai_output = result['answer']
                    
                    if not ai_output:
                        st.error("Dify输出的文本为空，请检查大模型节点或END节点设置。")
                        st.stop()

                    # 核心防崩溃清洗逻辑：用正则表达式强行提取 JSON 括号内的内容
                    match = re.search(r'\{.*\}', ai_output, re.DOTALL)
                    if match:
                        json_str = match.group(0)
                    else:
                        json_str = ai_output
                    
                    res_json = json.loads(json_str)
                    
                    # --- 开始前端渲染 ---
                    st.balloons()
                    st.success(f"评估完成！综合评分：{res_json.get('total_score')} 分")
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.subheader("📊 策略雷达图分析")
                        radar_df = pd.DataFrame(dict(
                            r=list(res_json['radar_data'].values()),
                            theta=list(res_json['radar_data'].keys())
                        ))
                        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
                        st.plotly_chart(fig)
                        
                    with col2:
                        st.subheader("🚫 敏感词合规风险")
                        st.warning(res_json.get("sensitive_risk"))
                        
                    st.subheader("📝 各维度详细举例点评")
                    for k, v in res_json.get("comments", {}).items():
                        st.markdown(f"**【{k}】**：{v}")
                        
                    st.subheader("💡 导师优化建议")
                    for sug in res_json.get("suggestions", []):
                        st.info(sug)
                except Exception as e:
                    st.error(f"解析出错，错误信息: {e}")
                    if 'result' in locals():
                        st.write("调试后台原始数据：", result)
else:
    st.info("请输入正确的访问密码以解锁系统。")
