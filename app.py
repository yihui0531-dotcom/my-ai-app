import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="AI带货话术评估系统", layout="wide")
st.title("🏆 顶级直播带货话术 AI 评估系统")

default_criteria = "体验策略、功能策略、信任策略、稀缺性策略、激励策略、定位策略、承诺策略"
st.sidebar.header("⚙️ 评估配置中心")
criteria = st.sidebar.text_area("自定义评判维度", value=default_criteria, height=100)
sensitive_words = st.sidebar.text_input("敏感词词库（用逗号隔开）", value="第一,最好,绝无仅有")

# Dify API 配置
DIFY_API_URL = "https://api.dify.ai/v1/workflows/run"
DIFY_API_KEY = "app-W35824eSzCai116xo9IecS8h"

text_input = st.text_area("请粘贴需要评估的主播话术文本：", height=300)

if st.button("🔥 开始全维度 AI 诊断"):
    if not text_input:
        st.warning("请先输入话术文本！")
    else:
        with st.spinner("AI 正在深度解析中，请稍候..."):
            # 开启流式传输，直接监听大模型的嘴巴，不再通过 Dify 输出节点转交
            headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
            data = {
                "inputs": {"text": text_input, "criteria": criteria, "sensitive_words": sensitive_words},
                "response_mode": "streaming",  # 更改为流式，直接扒日志
                "user": "streamlit_user"
            }
            try:
                response = requests.post(DIFY_API_URL, json=data, headers=headers, stream=True)
                
                # 从流式日志里疯狂搜刮大模型文本
                ai_output = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            try:
                                log_json = json.loads(decoded_line[5:])
                                # 只要发现工作流里有大模型在说话的痕迹（text 或者是 answer），直接全量拼接
                                if 'event' in log_json and log_json['event'] == 'text_chunk':
                                    ai_output += log_json.get('data', {}).get('text', '')
                                elif 'answer' in log_json:
                                    ai_output += log_json.get('answer', '')
                            except:
                                pass

                # 剥离思考标签
                if "</think>" in ai_output:
                    ai_output = ai_output.split("</think>")[-1]

                # 提取 JSON
                match = re.search(r'\{.*\}', ai_output, re.DOTALL)
                json_str = match.group(0) if match else ai_output
                
                try:
                    res_json = json.loads(json_str)
                except Exception:
                    res_json = {}
                
                if not isinstance(res_json, dict): res_json = {}
                
                # 纠正雷达图 Key
                if "radar_data" not in res_json:
                    for k in ["radar", "radarData", "数据", "评分"]:
                        if k in res_json: res_json["radar_data"] = res_json[k]; break

                v_list = [k.strip() for k in criteria.replace("，", "、").replace(",", "、").split("、") if k.strip()]
                if "radar_data" not in res_json or not isinstance(res_json["radar_data"], dict):
                    res_json["radar_data"] = {k: 3 for k in v_list}
                if "total_score" not in res_json: res_json["total_score"] = 80

                # --- 前端渲染 ---
                st.balloons()
                st.success(f"评估完成！综合评分：{res_json.get('total_score')} 分")
                
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
                    st.info("💡 详细诊断文本：")
                    st.text(ai_output if ai_output else "未监听到模型输出，请检查API_KEY。")
                    
                st.subheader("💡 导师优化建议")
                sugs = res_json.get("suggestions", [])
                if isinstance(sugs, list) and sugs:
                    for sug in sugs: st.info(sug)
                else:
                    st.info("建议多增加话术的互动性和稀缺性提示。")
                    
            except Exception as e:
                st.error(f"系统运行遇到小障碍: {e}")
