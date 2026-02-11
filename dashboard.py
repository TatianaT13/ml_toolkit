"""
Real-time Malware Detection Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

st.set_page_config(page_title="🛡️ Real-time Malware Detection", layout="wide")

# Header
st.title("🛡️ Real-time Malware Detection Dashboard")
st.markdown("Live monitoring of malware detection system")

# Metrics en temps réel
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Files Scanned Today", "1,247", "+23")
with col2:
    st.metric("Malware Detected", "156", "+5")
with col3:
    st.metric("Detection Rate", "98.5%", "+0.2%")
with col4:
    st.metric("Avg Response Time", "0.15s", "-0.02s")

# Graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Detections Last 24h")
    
    # Générer données fake en temps réel
    hours = list(range(24))
    detections = [random.randint(5, 25) for _ in hours]
    
    fig = px.line(
        x=hours, 
        y=detections,
        labels={'x': 'Hour', 'y': 'Detections'},
        title="Malware detections per hour"
    )
    fig.update_traces(line_color='#FF4B4B')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Detection by Type")
    
    data = pd.DataFrame({
        'Type': ['Trojan', 'Ransomware', 'Spyware', 'Adware', 'Worm'],
        'Count': [45, 28, 22, 18, 12]
    })
    
    fig = px.pie(data, values='Count', names='Type', title='Malware types detected today')
    st.plotly_chart(fig, use_container_width=True)

# Live feed
st.subheader("📡 Live Detection Feed")

# Container pour le feed
feed_container = st.container()

with feed_container:
    # Tableau des dernières détections
    recent_data = pd.DataFrame({
        'Time': [(datetime.now() - timedelta(minutes=i)).strftime('%H:%M:%S') for i in range(5)],
        'File': [f'suspicious_{i}.exe' for i in range(5)],
        'Type': random.choices(['Trojan', 'Ransomware', 'Spyware'], k=5),
        'Confidence': [f"{random.randint(85, 99)}%" for _ in range(5)],
        'Action': ['🔴 Quarantined'] * 5
    })
    
    st.dataframe(recent_data, use_container_width=True)

# Auto-refresh
st.markdown("---")
auto_refresh = st.checkbox("🔄 Auto-refresh (every 5s)")

if auto_refresh:
    time.sleep(5)
    st.rerun()

# Sidebar - Filters
with st.sidebar:
    st.header("⚙️ Filters")
    
    date_range = st.date_input("Date Range", [datetime.now().date()])
    
    confidence_threshold = st.slider("Confidence Threshold", 0, 100, 85)
    
    malware_types = st.multiselect(
        "Malware Types",
        ['Trojan', 'Ransomware', 'Spyware', 'Adware', 'Worm'],
        default=['Trojan', 'Ransomware']
    )
    
    st.markdown("---")
    st.markdown("### 📈 System Health")
    st.success("🟢 All systems operational")
    st.info(f"⚡ API Latency: 150ms")
    st.info(f"💾 DB Connection: Healthy")
