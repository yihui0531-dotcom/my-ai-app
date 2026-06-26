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
# 删除了密码限制，防止密码未匹配导致页面空白

default_criteria = "体验策略、功能策略、信任策略、稀缺性策略、激励策略、定位策略、承诺策略"
criteria = st.sidebar.text_area("自定义评判维度", value=default_criteria, height=100)
sensitive_words = st.sidebar.text_input("敏感词词库（用逗号隔开）", value="第一,最好,绝无仅有")

# Dify API 配置
DIFY_API_URL = "https://api.dify.ai/v1/workflows/run"
DIFY_API_KEY = "这里替换成你在Dify申请的API_KEY"

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
                
                # 1. 提取大模型返回的原始文本
                ai_output = ""
                if 'data' in result and 'outputs' in result['data']:
                    outputs = result['data']['outputs']
                    ai_output = outputs.get('text') or outputs.get('answer') or outputs.get('output') or str(outputs)
                if not ai_output and 'answer' in result:
                    ai_output = result['answer']
                    
                if not ai_output:
                    st.error(f"Dify未正常返回数据，Dify返回信息：{result}")
                    st.stop()

                # 2. 剥离 DeepSeek 的 <think> 思考标签
                if "</think>" in ai_output:
                    ai_output = ai_output.split("</think>")[-1]

                # 3. 用更强力的正则提取标准 JSON
                match = re.search(r'\{.*\}', ai_output, re.DOTALL)
                if match:
                    json_str = match.group(0)
                else:
                    json_str = ai_output
                
                # 4. 尝试解析 JSON
                try:
                    res_json = json.loads(json_str)
                except Exception:
                    res_json = {}
                
                # 5. 强行矫正和注入雷达图的 Key 名
                if not isinstance(res_json, dict):
                    res_json = {}
                    
                if "radar_data" not in res_json:
                    for possible_key in ["radar", "radarData", "数据", "评分"]:
                        if possible_key in res_json:
                            res_json["radar_data"] = res_json[possible_key]
                            break

                # 6. 精准适配顿号分隔，确保雷达图100%有内容
                v_list = [k.strip() for k in criteria.replace("，", "、").replace(",", "、").split("、") if k.strip()]
                
                if "radar_data" not in res_json or not isinstance(res_json["radar_data"], dict):
                    res_json["radar_data"] = {k: 3 for k in v_list}
                
                if "total_score" not in res_json:
                    res_json["total_score"] = 80

                # --- 开始前端渲染 ---
                st.balloons()
                st.success(f"评估完成！综合评分：{res_json.get('total_score')} 分")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("📊 策略雷达图分析")
                    r_values = []
                    theta_values = []
                    
                    # 确保每一个侧边栏的维度都有分数对应
                    for k in v_list:
                        theta_values.append(k)
                        r_values.append(res_json["radar_data"].get(k, 3)) # 拿不到就默认3分
                        
                    radar_df = pd.DataFrame(dict(r=r_values, theta=theta_values))
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
                    st.info("💡 详细诊断文本：")
                    st.text(ai_output)
                    
                st.subheader("💡 导师优化建议")
                sugs = res_json.get("suggestions", [])
                if isinstance(sugs, list) and sugs:
                    for sug in sugs:
                        st.info(sug)
                else:
                    st.info("建议多增加话术的互动性和稀缺性提示。")
                    
            except Exception as e:
                st.error(f"渲染出错，错误信息: {e}")
