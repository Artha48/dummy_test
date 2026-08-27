import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Dummy - Tenaga Ahli", layout="centered")

# 1. Cek apakah firebase sudah jalan
if not firebase_admin._apps:
    # 2. Ambil string JSON dari secrets dan ubah jadi dictionary
    kredensial_dict = json.loads(st.secrets["FIREBASE_JSON"])
    
    # 3. Masukkan ke Firebase
    cred = credentials.Certificate(kredensial_dict)
    firebase_admin.initialize_app(cred)

st.success("terkoneksi")

# ============================================
# 1. INISIALISASI FIREBASE ADMIN SDK
# ============================================

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ============================================
# 2. AUTENTIKASI SEDERHANA 
# ============================================
st.title("Dashboard Skrining Kecemasan Sosial (Dummy)")

password = st.text_input("Masukkan kode akses ahli", type="password")
if password != "ahli333":  
    st.warning("Masukkan kode akses yang benar untuk melanjutkan.")
    st.stop()

st.success("Akses diterima.")

# ============================================
# 3. AMBIL DATA DARI FIRESTORE
# ============================================
docs = db.collection("responses").stream()
data = [doc.to_dict() for doc in docs]

if not data:
    st.info("Belum ada data. Coba mainkan game Ren'Py dummy terlebih dahulu.")
    st.stop()

df = pd.DataFrame(data)

st.subheader("Data Mentah (raw data dari Firestore)")
st.dataframe(df)

# ============================================
# 4. TRANSFORMASI DATA -> INFORMASI (chart)
# ============================================
st.subheader("Ringkasan per Sesi")

# Pilih salah satu sesi untuk dilihat detailnya
session_ids = df["session_id"].unique().tolist()
selected_session = st.selectbox("Pilih Sesi", session_ids)

session_data = df[df["session_id"] == selected_session]

total_fear = session_data["skor_fear"].sum()
total_avoidance = session_data["skor_avoidance"].sum()

col1, col2 = st.columns(2)
col1.metric("Total Skor Fear", int(total_fear))
col2.metric("Total Skor Avoidance", int(total_avoidance))

# Radar chart sederhana
fig = go.Figure(data=go.Scatterpolar(
    r=[total_fear, total_avoidance],
    theta=["Fear", "Avoidance"],
    fill='toself'
))
fig.update_layout(title="Profil Skor (Dummy)")
st.plotly_chart(fig)

# Distribusi agregat seluruh sesi
st.subheader("Distribusi Skor Fear - Seluruh Sesi")
agg = df.groupby("session_id")["skor_fear"].sum().reset_index()
st.bar_chart(agg.set_index("session_id"))
