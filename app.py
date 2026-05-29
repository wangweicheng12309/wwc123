import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(page_title="无人机心跳监控", layout="wide")
st.title("📡 无人机心跳包实时监控")

# 初始化全局数据
if "heartbeat_list" not in st.session_state:
    st.session_state.heartbeat_list = []
if "last_beat_time" not in st.session_state:
    st.session_state.last_beat_time = datetime.now()
if "sequence" not in st.session_state:
    st.session_state.sequence = 0

# 控制面板
col1, col2 = st.columns(2)
with col1:
    start = st.button("开始心跳", type="primary")
with col2:
    stop = st.button("停止心跳")

# 停止逻辑
if stop:
    st.session_state.running = False

# 开始逻辑
if start:
    st.session_state.running = True
    st.success("✅ 心跳已启动，每秒发送一次")

# 自动发送心跳（每秒一次）
if st.session_state.get("running", False):
    # 发送心跳
    st.session_state.sequence += 1
    now = datetime.now()
    now_str = now.strftime("%H:%M:%S")
    
    # 保存数据
    st.session_state.heartbeat_list.append({
        "心跳序号": st.session_state.sequence,
        "接收时间": now_str
    })
    st.session_state.last_beat_time = now

    # 刷新页面（实现实时更新）
    st.rerun()

# 超时判断（3秒未收到）
current = datetime.now()
time_diff = (current - st.session_state.last_beat_time).total_seconds()
timeout = time_diff > 3

# 状态显示
if timeout and st.session_state.get("running", False):
    st.error("🔴 连接超时！3秒未收到心跳包！")
else:
    st.success(f"🟢 连接正常 | 最后心跳时间：{st.session_state.last_beat_time.strftime('%H:%M:%S')}")

# 可视化区域
st.divider()
tab1, tab2 = st.tabs(["📈 心跳折线图", "📋 数据列表"])

# 图表
with tab1:
    if st.session_state.heartbeat_list:
        df = pd.DataFrame(st.session_state.heartbeat_list)
        st.line_chart(df, x="接收时间", y="心跳序号", use_container_width=True)
    else:
        st.info("点击「开始心跳」生成数据")

# 数据列表
with tab2:
    if st.session_state.heartbeat_list:
        st.dataframe(pd.DataFrame(st.session_state.heartbeat_list), use_container_width=True, height=400)
    else:
        st.info("暂无数据")
