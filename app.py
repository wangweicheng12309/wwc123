import streamlit as st
import time
import threading
from datetime import datetime, timedelta
import pandas as pd

# 页面配置
st.set_page_config(
    page_title="无人机心跳包监控",
    page_icon="📡",
    layout="wide"
)

# 初始化会话状态（Streamlit全局变量）
if "heartbeat_data" not in st.session_state:
    # 存储所有心跳数据：序号、发送时间、接收时间、状态
    st.session_state.heartbeat_data = []
if "last_received_time" not in st.session_state:
    st.session_state.last_received_time = datetime.now()
if "is_connected" not in st.session_state:
    st.session_state.is_connected = True
if "running" not in st.session_state:
    st.session_state.running = False
if "seq_num" not in st.session_state:
    st.session_state.seq_num = 0

# 标题
st.title("📡 无人机心跳包实时监控系统")
st.divider()

# 控制面板
col1, col2, col3 = st.columns(3)
with col1:
    start_btn = st.button("启动心跳监控", type="primary")
with col2:
    stop_btn = st.button("停止监控", type="secondary")
with col3:
    st.metric("当前连接状态", "正常" if st.session_state.is_connected else "超时", 
              delta="连接正常" if st.session_state.is_connected else "连接超时",
              delta_color="normal" if st.session_state.is_connected else "inverse")

# 核心：心跳包发送/接收函数（后台线程运行）
def heartbeat_task():
    while st.session_state.running:
        # 1. 生成心跳包：序号 + 时间
        current_time = datetime.now()
        st.session_state.seq_num += 1
        seq = st.session_state.seq_num
        send_time = current_time.strftime("%H:%M:%S.%f")[:-3]  # 格式化时间
        
        # 2. 模拟自发自收
        receive_time = current_time.strftime("%H:%M:%S.%f")[:-3]
        st.session_state.last_received_time = current_time
        
        # 3. 保存心跳数据
        st.session_state.heartbeat_data.append({
            "心跳序号": seq,
            "发送时间": send_time,
            "接收时间": receive_time,
            "状态": "正常"
        })
        
        # 每秒发送一次心跳
        time.sleep(1)

# 超时检测函数
def check_timeout():
    while st.session_state.running:
        now = datetime.now()
        # 3秒未收到心跳 → 标记超时
        if now - st.session_state.last_received_time > timedelta(seconds=3):
            st.session_state.is_connected = False
        else:
            st.session_state.is_connected = True
        time.sleep(0.1)

# 按钮逻辑
if start_btn:
    if not st.session_state.running:
        st.session_state.running = True
        # 启动后台线程：心跳发送 + 超时检测
        threading.Thread(target=heartbeat_task, daemon=True).start()
        threading.Thread(target=check_timeout, daemon=True).start()
        st.success("✅ 已启动心跳监控，每秒发送一次心跳包")

if stop_btn:
    st.session_state.running = False
    st.info("⏹️ 已停止心跳监控")

st.divider()

# 数据展示与可视化
tab1, tab2 = st.tabs(["📊 实时折线图", "📋 心跳数据列表"])

with tab1:
    st.subheader("心跳包序号随时间变化趋势")
    if st.session_state.heartbeat_data:
        df = pd.DataFrame(st.session_state.heartbeat_data)
        # 绘制折线图：X轴时间，Y轴心跳序号
        st.line_chart(
            data=df,
            x="接收时间",
            y="心跳序号",
            color="#FF4B4B",
            use_container_width=True
        )
    else:
        st.info("点击「启动心跳监控」开始生成数据")

with tab2:
    st.subheader("完整心跳包数据")
    if st.session_state.heartbeat_data:
        df = pd.DataFrame(st.session_state.heartbeat_data)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("暂无心跳数据，启动后自动生成")

# 实时状态提示
st.divider()
if not st.session_state.is_connected and st.session_state.running:
    st.error("🔴 连接超时！3秒未收到无人机心跳包！")
elif st.session_state.is_connected and st.session_state.running:
    st.success("🟢 连接正常，心跳包接收稳定")
