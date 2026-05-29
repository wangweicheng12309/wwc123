import streamlit as st
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="无人机心跳", layout="wide")
st.title("📡 无人机心跳包监控（稳定版）")

# 初始化
if "data" not in st.session_state:
    st.session_state.data = []
if "last" not in st.session_state:
    st.session_state.last = datetime.now()
if "seq" not in st.session_state:
    st.session_state.seq = 0
if "run" not in st.session_state:
    st.session_state.run = False

# 按钮
c1, c2 = st.columns(2)
with c1:
    if st.button("启动"):
        st.session_state.run = True
with c2:
    if st.button("停止"):
        st.session_state.run = False

# 状态
now = datetime.now()
timeout = (now - st.session_state.last).total_seconds() > 3

if timeout and st.session_state.run:
    st.error("🔴 连接超时！")
else:
    st.success("🟢 正常")

# 每秒生成心跳
if st.session_state.run:
    st.session_state.seq += 1
    t = now.strftime("%H:%M:%S")
    st.session_state.data.append([st.session_state.seq, t])
    st.session_state.last = now
    time.sleep(1)
    st.rerun()

# 显示图表
if st.session_state.data:
    df = [[x[0], x[1]] for x in st.session_state.data]
    st.subheader("心跳序号趋势")
    st.line_chart(df, x_label="时间", y_label="序号")

    st.subheader("数据列表")
    st.dataframe(st.session_state.data, height=300)
