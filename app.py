import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import ast
import os

from datetime import datetime
from langchain_community.utilities import SQLDatabase
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
 
# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PASTI — Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
 
/* Sidebar background */
section[data-testid="stSidebar"] > div:first-child {
    background-color: #1e2d40;
    padding-top: 20px;
}
 
/* Semua teks di sidebar jadi putih */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: rgba(255,255,255,0.85) !important;
}
 
/* Radio button aktif */
section[data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"] > div:first-child {
    background-color: #2563eb !important;
    border-color: #2563eb !important;
}
 
/* Selectbox di sidebar */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: white !important;
}
 
/* Multiselect di sidebar */
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}
 
/* Tombol collapse sidebar bawaan Streamlit */
section[data-testid="stSidebar"] button[kind="header"],
button[data-testid="stSidebarCollapseButton"] {
    color: white !important;
    background-color: rgba(255,255,255,0.15) !important;
}
 
/* Tombol expand (saat sidebar tertutup) */
button[data-testid="stBaseButton-header"] {
    background-color: #1e2d40 !important;
    color: white !important;
}
 
/* Main area */
.main .block-container {
    padding: 24px 32px;
    background-color: #f8fafc;
}
 
/* Metric card */
.metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.metric-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.5px;
}
.chg-up   { font-size:12px; font-weight:700; color:#16a34a; margin-top:4px; }
.chg-down { font-size:12px; font-weight:700; color:#dc2626; margin-top:4px; }
.chg-nt   { font-size:12px; font-weight:700; color:#9ca3af; margin-top:4px; }
 
/* Section title */
.sec-title {
    font-size: 17px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.3px;
    margin-bottom: 4px;
}
.sec-sub {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 500;
    margin-bottom: 14px;
}
 
/* Page title */
.page-title {
    font-size: 24px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.5px;
}
.page-sub {
    font-size: 13px;
    color: #9ca3af;
    font-weight: 500;
    margin-bottom: 24px;
}
 
/* AI Box */
.ai-box {
    background: linear-gradient(135deg, #1e2d40, #243352);
    border-radius: 14px;
    padding: 18px 20px;
    border: 1px solid rgba(255,255,255,0.07);
}
.ai-box-title { font-size:13px; font-weight:700; color:#fff; margin-bottom:6px; }
.ai-box-text  { font-size:12px; color:rgba(255,255,255,0.65); line-height:1.6; }
 
/* Badge */
.badge-on {
    display:inline-block;
    background:#dcfce7; color:#15803d;
    font-size:11px; font-weight:700;
    padding:4px 12px; border-radius:20px;
}
 
/* Confidence */
.conf-high   { background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:6px; font-weight:700; font-size:11px; }
.conf-med    { background:#fef9c3; color:#a16207; padding:2px 8px; border-radius:6px; font-weight:700; font-size:11px; }
.conf-low    { background:#ffedd5; color:#c2410c; padding:2px 8px; border-radius:6px; font-weight:700; font-size:11px; }
.sel-up      { color:#16a34a; font-weight:700; }
.sel-down    { color:#dc2626; font-weight:700; }
 
footer, #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────
#  LOAD DATA DARI CSV
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("IDN_RTFP_mkt_2007_2026-04-08__1_.csv")
    df['price_date'] = pd.to_datetime(df['price_date'])
    df = df[df['adm1_name'] != 'Market Average']

    # ── Penyamaan nama kolom dengan NOTEBOOK (acuan) ──
    # Notebook memakai kolom harga ber-prefix "c_" (c_rice, c_chili, ...).
    # Baris di bawah memastikan dashboard memakai konvensi yang sama, apa pun
    # nama kolom di CSV (baik "rice" maupun yang sudah "c_rice").
    base_cols = ["rice", "chili", "eggs", "oil", "sugar",
                 "meat_chicken", "meat_beef", "onions", "garlic"]
    for b in base_cols:
        if f"c_{b}" not in df.columns and b in df.columns:
            df = df.rename(columns={b: f"c_{b}"})

    return df
 
try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ File CSV tidak ditemukan! Pastikan **IDN_RTFP_mkt_2007_2026-04-08__1_.csv** ada di folder yang sama dengan app.py")
    st.stop()
 
# ─────────────────────────────────────────────
#  MAPPING KOMODITAS
# ─────────────────────────────────────────────
KOMODITAS_MAP = {
    "Beras":         {"col": "c_rice",          "emoji": "🌾", "warna": "#2ECC71", "unit": "/kg"},
    "Cabai":         {"col": "c_chili",         "emoji": "🌶️", "warna": "#E74C3C", "unit": "/kg"},
    "Telur":         {"col": "c_eggs",          "emoji": "🥚", "warna": "#F39C12", "unit": "/kg"},
    "Minyak Goreng": {"col": "c_oil",           "emoji": "💧", "warna": "#3498DB", "unit": "/L"},
    "Gula":          {"col": "c_sugar",         "emoji": "🍬", "warna": "#9B59B6", "unit": "/kg"},
    "Ayam":          {"col": "c_meat_chicken",  "emoji": "🍗", "warna": "#E67E22", "unit": "/kg"},
    "Daging Sapi":   {"col": "c_meat_beef",     "emoji": "🥩", "warna": "#C0392B", "unit": "/kg"},
    "Bawang Merah":  {"col": "c_onions",        "emoji": "🧅", "warna": "#D35400", "unit": "/kg"},
    "Bawang Putih":  {"col": "c_garlic",        "emoji": "🧄", "warna": "#8E44AD", "unit": "/kg"},
}
 
PROVINSI_LIST = sorted(df_raw['adm1_name'].dropna().unique().tolist())
 
# ─────────────────────────────────────────────
#  FUNGSI HELPER
# ─────────────────────────────────────────────
def get_harga_terkini(provinsi, kolom):
    subset = df_raw[df_raw['adm1_name'] == provinsi][['price_date', kolom]].dropna()
    if subset.empty:
        return None, None
    latest = subset.sort_values('price_date').iloc[-1]
    return latest[kolom], latest['price_date']
 
def get_tren_bulanan(provinsi, kolom, n_bulan=12):
    subset = df_raw[df_raw['adm1_name'] == provinsi][['price_date', kolom]].dropna()
    if subset.empty:
        return pd.DataFrame()
    subset = subset.set_index('price_date').sort_index()
    monthly = subset.resample('MS').mean().reset_index()
    if n_bulan < 999:
        monthly = monthly.tail(n_bulan)
    return monthly
 
def hitung_pct_change(provinsi, kolom):
    subset = df_raw[df_raw['adm1_name'] == provinsi][['price_date', kolom]].dropna()
    if len(subset) < 2:
        return 0
    monthly = subset.set_index('price_date').resample('MS').mean()
    if len(monthly) < 2:
        return 0
    prev = monthly.iloc[-2][kolom]
    curr = monthly.iloc[-1][kolom]
    if prev == 0:
        return 0
    return round((curr - prev) / prev * 100, 1)
 
# ─────────────────────────────────────────────
#  MODEL ML — LOADER & FORECAST ASLI
# ─────────────────────────────────────────────
FITUR_MODEL = ['adm1_name', 'adm2_name', 'mkt_name', 'commodity',
               'lag_1', 'lag_2', 'rolling_mean_3', 'lag_12', 'rolling_mean_12',
               'gas_lag2', 'is_idul_fitri', 'is_imlek', 'is_natal', 'is_tahun_baru']

@st.cache_resource
def load_model_artifacts():
    """Muat model XGBoost + encoder. Kembalikan (None, None) jika file belum ada."""
    try:
        model = joblib.load("model_harga_pangan.pkl")
        encoders = joblib.load("label_encoders.pkl")
        return model, encoders
    except Exception:
        return None, None

@st.cache_data
def load_pred_data():
    """Data per-pasar lengkap (dataset_bersih.csv) untuk menghitung fitur prediksi."""
    try:
        df = pd.read_csv("dataset_bersih.csv", parse_dates=["price_date"])
        return df.sort_values("price_date")
    except Exception:
        return None

def get_holiday_flags(year, month):
    """Flag hari besar untuk satu (tahun, bulan) — logika sama dengan notebook."""
    try:
        import holidays as _hol
        id_hol = _hol.Indonesia(years=[year])
        names = " ".join(name.lower() for d, name in id_hol.items() if d.month == month)
    except Exception:
        names = ""
    return {
        'is_idul_fitri': int('eid al-fitr' in names),
        'is_imlek':      int('lunar new year' in names),
        'is_natal':      int('christmas day' in names),
        'is_tahun_baru': int("new year's day" in names),
    }

def _encode(encoders, col, value):
    le = encoders[col]
    return int(le.transform([value])[0]) if value in le.classes_ else -1

def forecast_recursive(model, encoders, hist, gas_lookup, adm1, adm2, mkt, commodity_model, n_steps=2):
    """Prediksi rekursif n_steps bulan ke depan untuk satu pasar+komoditas.
    hist: DataFrame terurut waktu dgn kolom 'price' & 'price_date' (>= 12 baris).
    Mengembalikan list berisi (timestamp, harga_prediksi)."""
    prices = hist['price'].tolist()
    last_date = pd.Timestamp(hist['price_date'].iloc[-1]).to_period('M').to_timestamp()

    adm1_e = _encode(encoders, 'adm1_name', adm1)
    adm2_e = _encode(encoders, 'adm2_name', adm2)
    mkt_e  = _encode(encoders, 'mkt_name', mkt)
    com_e  = _encode(encoders, 'commodity', commodity_model)
    gas_terakhir = list(gas_lookup.values())[-1] if gas_lookup else np.nan

    hasil = []
    cur_date = last_date
    for _ in range(n_steps):
        f_date = cur_date + pd.DateOffset(months=1)
        flags = get_holiday_flags(f_date.year, f_date.month)
        g_date = f_date - pd.DateOffset(months=2)   # gas_lag2 = bensin 2 bln sebelum bln forecast
        gas_lag2 = gas_lookup.get((g_date.year, g_date.month), gas_terakhir)

        X = pd.DataFrame([[
            adm1_e, adm2_e, mkt_e, com_e,
            prices[-1], prices[-2], float(np.mean(prices[-3:])),
            prices[-12], float(np.mean(prices[-12:])),
            gas_lag2,
            flags['is_idul_fitri'], flags['is_imlek'], flags['is_natal'], flags['is_tahun_baru']
        ]], columns=FITUR_MODEL)

        pred = float(model.predict(X)[0])
        hasil.append((f_date, pred))
        prices.append(pred)         # feed-back untuk langkah berikutnya
        cur_date = f_date
    return hasil
 

# ─────────────────────────────────────────────
#  MODEL REKOMENDASI RESEP
# ─────────────────────────────────────────────
class RecipeRecommender:
    def __init__(self, df_recipes):
        self.df = df_recipes
        self.commodity_mapping = {
            'meat_beef': 'beef', 'meat_chicken': 'chicken', 
            'meat_chicken_broiler': 'chicken', 'eggs': 'egg',     
            'onions': 'onion', 'chili': 'chili', 'garlic': 'garlic',
            'oil': 'oil', 'rice': 'rice', 'sugar': 'sugar'
        }

    def _normalize_input(self, user_inputs):
        return set([self.commodity_mapping.get(item, item) for item in user_inputs])

    def recommend(self, user_inputs):
        input_set = self._normalize_input(user_inputs)
        df_model = self.df.copy()

        df_model['matched_ingredients'] = df_model['RecipeIngredientParts'].apply(
            lambda x: list(input_set.intersection(set(x))) if isinstance(x, list) else []
        )
        df_model['match_count'] = df_model['matched_ingredients'].apply(len)
        
        candidates = df_model[df_model['match_count'] > 0].copy()
        candidates['missing_count'] = candidates['RecipeIngredientParts'].apply(
            lambda x: len(set(x) - input_set) if isinstance(x, list) else 0
        )
        candidates['missing_ingredients'] = candidates['RecipeIngredientParts'].apply(
            lambda x: list(set(x) - input_set) if isinstance(x, list) else []
        )

        return candidates.sort_values(by=['match_count', 'missing_count'], ascending=[False, True])

@st.cache_data
def load_resep_data():
    try:
        # 1. Cari tahu lokasi persis file app.py ini berada
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Gabungkan dengan folder 'data' dan nama file CSV
        path_csv = os.path.join(BASE_DIR, "data", "resep_bersih.csv")
        
        # 3. Baca file menggunakan path yang sudah dinamis
        df = pd.read_csv(path_csv)
        
        df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(
            lambda x: ast.literal_eval(x) if pd.notna(x) else []
        )
        return df
    except Exception as e:
        # Menampilkan pesan error di terminal/layar jika file tidak ditemukan
        print(f"Gagal memuat resep_bersih.csv: {e}")
        return None
 
# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 PASTI")
    st.markdown("---")
 
    st.markdown("**NAVIGASI**")
    page = st.radio(
        "nav",
        ["🏠  Dashboard", "📈  Prediksi Harga", "🗺️  Peta Wilayah", "🧭 lokasi", "🍲  Rekomendasi Resep", "💬  Chatbot LLM", "📦 Gudang", "🕐  Riwayat", "⚙️  Pengaturan"],
        label_visibility="collapsed"
    )
 
    st.markdown("---")
    st.markdown("**FILTER**")
    wilayah_filter = st.selectbox(
        "Provinsi",
        PROVINSI_LIST,
        index=PROVINSI_LIST.index("JAWA TENGAH") if "JAWA TENGAH" in PROVINSI_LIST else 0
    )
    periode_filter = st.selectbox("Periode", ["6 Bulan", "12 Bulan", "24 Bulan", "Semua Data"])
 
    st.markdown("---")
    st.markdown("**KOMODITAS**")
    komoditas_filter = st.multiselect(
        "kom",
        list(KOMODITAS_MAP.keys()),
        default=["Beras", "Cabai", "Telur", "Minyak Goreng"],
        label_visibility="collapsed"
    )
 
    st.markdown("---")
    st.caption(f"Dataset: World Bank RTFP\n{len(df_raw):,} baris · {df_raw['mkt_name'].nunique()} pasar\n2007 – Apr 2026")
 
 
# ─────────────────────────────────────────────
#  HALAMAN: DASHBOARD
# ─────────────────────────────────────────────
if "Dashboard" in page:
 
    # Header
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown('<div class="page-title">Overview Dashboard</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="page-sub">Data harga pangan · {wilayah_filter.title()} · Update: {df_raw["price_date"].max().strftime("%B %Y")}</div>',
            unsafe_allow_html=True
        )
    
 
    # Metric cards
    selected = komoditas_filter if komoditas_filter else ["Beras", "Cabai", "Telur", "Minyak Goreng"]
    cols = st.columns(len(selected))
 
    for i, nama in enumerate(selected):
        info = KOMODITAS_MAP[nama]
        harga, tgl = get_harga_terkini(wilayah_filter, info["col"])
        pct = hitung_pct_change(wilayah_filter, info["col"])
 
        if harga is None:
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{info['emoji']} {nama}</div>
                    <div class="metric-value" style="font-size:16px">Data N/A</div>
                    <div class="chg-nt">Tidak tersedia</div>
                </div>""", unsafe_allow_html=True)
            continue
 
        if pct > 0:
            chg = f'<div class="chg-up">↑ {pct}% MoM</div>'
        elif pct < 0:
            chg = f'<div class="chg-down">↓ {abs(pct)}% MoM</div>'
        else:
            chg = '<div class="chg-nt">→ Stabil</div>'
 
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{info['emoji']} {nama}</div>
                <div class="metric-value">Rp {harga:,.0f}</div>
                {chg}
            </div>""", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # Chart + Tabel
    col_chart, col_tabel = st.columns([1.4, 1], gap="large")
 
    with col_chart:
        st.markdown('<div class="sec-title">Tren Harga</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Prediksi per pasar tersedia di halaman <b>Prediksi Harga</b></div>', unsafe_allow_html=True)
        kom_chart = st.selectbox("Pilih komoditas chart", selected, label_visibility="collapsed")
        info = KOMODITAS_MAP[kom_chart]

        n_map = {"6 Bulan": 6, "12 Bulan": 12, "24 Bulan": 24, "Semua Data": 999}
        tren = get_tren_bulanan(wilayah_filter, info["col"], n_map[periode_filter])

        if tren.empty:
            st.warning(f"Data {kom_chart} tidak tersedia untuk {wilayah_filter.title()}")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tren['price_date'], y=tren[info["col"]],
                mode="lines+markers",
                line=dict(color=info["warna"], width=2.5),
                marker=dict(size=4),
                name="Harga aktual",
            ))
            fig.update_layout(
                height=280, margin=dict(l=0, r=0, t=8, b=0),
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="Plus Jakarta Sans", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                xaxis=dict(showgrid=False, linecolor="#e5e7eb"),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6",
                           tickformat=",", tickprefix="Rp ", linecolor="#e5e7eb"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
 
    with col_tabel:
        st.markdown('<div class="sec-title">Ringkasan Harga Terkini</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-sub">{wilayah_filter.title()}</div>', unsafe_allow_html=True)
 
        rows = []
        for nama in selected:
            info = KOMODITAS_MAP[nama]
            harga, tgl = get_harga_terkini(wilayah_filter, info["col"])
            pct = hitung_pct_change(wilayah_filter, info["col"])
            if harga is not None:
                rows.append({
                    "Komoditas":  f"{info['emoji']} {nama}",
                    "Harga Kini": f"Rp {harga:,.0f}",
                    "Perubahan":  f"{'+'if pct>=0 else ''}{pct}%",
                    "Update":     tgl.strftime("%b %Y") if tgl is not None else "-",
                })
 
        if rows:
            df_tabel = pd.DataFrame(rows)
            def style_pct(v):
                if v.startswith("+"): return "color:#16a34a;font-weight:700"
                elif v.startswith("-"): return "color:#dc2626;font-weight:700"
                return ""
            st.dataframe(
                df_tabel.style.map(style_pct, subset=["Perubahan"]),
                hide_index=True, use_container_width=True
            )
        else:
            st.warning("Tidak ada data untuk komoditas yang dipilih.")
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # AI Insight
    st.markdown('<div class="sec-title">Analisis AI</div>', unsafe_allow_html=True)
    ai1, ai2, ai3 = st.columns(3)
 
    pct_beras = hitung_pct_change(wilayah_filter, "c_rice")
    pct_cabai = hitung_pct_change(wilayah_filter, "c_chili")
    pct_minyak = hitung_pct_change(wilayah_filter, "c_oil")
 
    with ai1:
        arah = "naik" if pct_beras > 0 else ("turun" if pct_beras < 0 else "stabil")
        saran = "Pertimbangkan stok lebih awal." if pct_beras > 0 else ("Waktu yang baik untuk pembelian." if pct_beras < 0 else "Pantau terus perkembangannya.")
        st.markdown(f"""<div class="ai-box">
            <div class="ai-box-title">🌾 Beras — Tren {arah.title()}</div>
            <div class="ai-box-text">Harga beras di {wilayah_filter.title()} {arah} {abs(pct_beras)}% bulan ini.
            {saran}</div>
        </div>""", unsafe_allow_html=True)
 
    with ai2:
        arah2 = "naik" if pct_cabai > 0 else ("turun" if pct_cabai < 0 else "stabil")
        st.markdown(f"""<div class="ai-box">
            <div class="ai-box-title">🌶️ Cabai — Tren {arah2.title()}</div>
            <div class="ai-box-text">Harga cabai {arah2} {abs(pct_cabai)}% di {wilayah_filter.title()}.
            Cabai sangat sensitif terhadap cuaca dan musim panen — pantau setiap bulan.</div>
        </div>""", unsafe_allow_html=True)
 
    with ai3:
        arah3 = "naik" if pct_minyak > 0 else ("turun" if pct_minyak < 0 else "stabil")
        st.markdown(f"""<div class="ai-box">
            <div class="ai-box-title">💧 Minyak Goreng — {arah3.title()}</div>
            <div class="ai-box-text">Harga minyak goreng {arah3} {abs(pct_minyak)}% di {wilayah_filter.title()}.
            Prediksi harga 2 bulan ke depan kini tersedia di halaman Prediksi Harga (per pasar).</div>
        </div>""", unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────
#  HALAMAN: PREDIKSI
# ─────────────────────────────────────────────
elif "Prediksi" in page:
    st.markdown('<div class="page-title">📈 Prediksi Harga — Model XGBoost</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Prediksi harga 2 bulan ke depan per pasar menggunakan machine learning</div>', unsafe_allow_html=True)

    model_ml, encoders_ml = load_model_artifacts()
    df_pred = load_pred_data()

    if model_ml is None or df_pred is None:
        st.warning(
            "⚠️ File model belum lengkap. Pastikan ketiga file ini ada di repo "
            "(sejajar app.py): **model_harga_pangan.pkl**, **label_encoders.pkl**, dan "
            "**dataset_bersih.csv**."
        )
    else:
        # ── Pilihan: Provinsi → Pasar → Komoditas ──
        c1, c2, c3 = st.columns(3)
        with c1:
            prov_opsi = sorted(df_pred['adm1_name'].dropna().unique().tolist())
            idx_prov = prov_opsi.index(wilayah_filter) if wilayah_filter in prov_opsi else 0
            prov_sel = st.selectbox("Provinsi", prov_opsi, index=idx_prov)
        with c2:
            pasar_opsi = sorted(
                df_pred[df_pred['adm1_name'] == prov_sel]['mkt_name'].dropna().unique().tolist()
            )
            pasar_sel = st.selectbox("Pasar", pasar_opsi)
        with c3:
            kom_sel = st.selectbox("Komoditas", list(KOMODITAS_MAP.keys()))

        info = KOMODITAS_MAP[kom_sel]
        commodity_model = info["col"].replace("c_", "", 1)   # "c_rice" -> "rice"

        # ── Riwayat pasar+komoditas ──
        hist = df_pred[
            (df_pred['mkt_name'] == pasar_sel) &
            (df_pred['commodity'] == commodity_model)
        ].sort_values('price_date').reset_index(drop=True)

        if len(hist) < 12:
            st.warning(
                f"Riwayat {kom_sel} di {pasar_sel} kurang dari 12 bulan "
                f"({len(hist)} bulan) — tidak cukup untuk prediksi musiman."
            )
        else:
            adm1 = hist['adm1_name'].iloc[-1]
            adm2 = hist['adm2_name'].iloc[-1]

            # Lookup harga bensin nasional per (tahun, bulan)
            gas_lookup = (
                df_pred.dropna(subset=['price_gas_rupiah'])
                       .drop_duplicates(['year', 'month'])
                       .set_index(['year', 'month'])['price_gas_rupiah']
                       .to_dict()
            )

            hasil = forecast_recursive(
                model_ml, encoders_ml, hist, gas_lookup,
                adm1, adm2, pasar_sel, commodity_model, n_steps=2
            )

            harga_akhir = float(hist['price'].iloc[-1])
            tgl_akhir   = pd.Timestamp(hist['price_date'].iloc[-1])
            (tgl_p1, p1), (tgl_p2, p2) = hasil[0], hasil[1]

            # ── Metric cards ──
            r1, r2, r3 = st.columns(3)
            with r1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Harga Terakhir ({tgl_akhir.strftime('%b %Y')})</div>
                    <div class="metric-value">Rp {harga_akhir:,.0f}</div>
                    <div class="chg-nt">{info['emoji']} {kom_sel} · {pasar_sel}</div>
                </div>""", unsafe_allow_html=True)
            with r2:
                d1 = p1 - harga_akhir
                cls1 = "chg-up" if d1 >= 0 else "chg-down"
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Prediksi {tgl_p1.strftime('%B %Y')}</div>
                    <div class="metric-value">Rp {p1:,.0f}</div>
                    <div class="{cls1}">{"+" if d1>=0 else ""}Rp {d1:,.0f} vs terakhir</div>
                </div>""", unsafe_allow_html=True)
            with r3:
                d2 = p2 - p1
                cls2 = "chg-up" if d2 >= 0 else "chg-down"
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Prediksi {tgl_p2.strftime('%B %Y')}</div>
                    <div class="metric-value">Rp {p2:,.0f}</div>
                    <div class="{cls2}">{"+" if d2>=0 else ""}Rp {d2:,.0f} vs bln-1</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Chart: 18 bulan terakhir + 2 bulan prediksi ──
            st.markdown(
                f'<div class="sec-title">{info["emoji"]} {kom_sel} · {pasar_sel}</div>'
                f'<div class="sec-sub">Riwayat 18 bulan terakhir + prediksi 2 bulan</div>',
                unsafe_allow_html=True
            )
            hist_plot = hist.tail(18)
            fc_x = [tgl_akhir, tgl_p1, tgl_p2]   # sambungkan titik aktual terakhir ke prediksi
            fc_y = [harga_akhir, p1, p2]
            today_x = tgl_akhir.strftime("%Y-%m-%d")

            figp = go.Figure()
            figp.add_trace(go.Scatter(
                x=hist_plot['price_date'], y=hist_plot['price'],
                mode="lines+markers",
                line=dict(color=info["warna"], width=2.5),
                marker=dict(size=5),
                name="Harga aktual",
            ))
            figp.add_trace(go.Scatter(
                x=fc_x, y=fc_y, mode="lines+markers",
                line=dict(color=info["warna"], width=2.5, dash="dot"),
                marker=dict(size=8, symbol="diamond"),
                name="Prediksi model",
            ))
            figp.add_shape(type="line", x0=today_x, x1=today_x, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="#9ca3af", width=1, dash="dash"))
            figp.add_annotation(x=today_x, y=0.98, xref="x", yref="paper",
                text="Akhir data", showarrow=False,
                font=dict(size=10, color="#9ca3af"), xanchor="left")
            figp.update_layout(
                height=340, margin=dict(l=0, r=0, t=8, b=0),
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="Plus Jakarta Sans", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                xaxis=dict(showgrid=False, linecolor="#e5e7eb"),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6",
                           tickformat=",", tickprefix="Rp ", linecolor="#e5e7eb"),
            )
            st.plotly_chart(figp, use_container_width=True, config={"displayModeBar": False})

            # ── Tabel prediksi ──
            st.markdown('<div class="sec-title">Rincian Prediksi</div>', unsafe_allow_html=True)
            baris_tabel = [
                {"Bulan": tgl_akhir.strftime("%B %Y"), "Harga": f"Rp {harga_akhir:,.0f}", "Status": "Aktual"},
                {"Bulan": tgl_p1.strftime("%B %Y"),    "Harga": f"Rp {p1:,.0f}",          "Status": "Prediksi (bulan +1)"},
                {"Bulan": tgl_p2.strftime("%B %Y"),    "Harga": f"Rp {p2:,.0f}",          "Status": "Prediksi (bulan +2)"},
            ]
            st.dataframe(pd.DataFrame(baris_tabel), hide_index=True, use_container_width=True)

            # ── Catatan jujur ──
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div class="ai-box">
                <div class="ai-box-title">ℹ️ Tentang prediksi ini</div>
                <div class="ai-box-text">
                Prediksi dihasilkan model XGBoost (rata-rata error sekitar 3,4% pada data uji).
                Prediksi bulan ke-2 dibangun di atas prediksi bulan ke-1, sehingga ketidakpastiannya
                sedikit lebih besar. Untuk komoditas yang harganya bergejolak (cabai, bawang, ayam)
                error bisa lebih tinggi. Gunakan angka ini sebagai bahan pertimbangan, bukan kepastian.
                </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HALAMAN: PETA
# ─────────────────────────────────────────────
elif "Peta" in page:
    st.markdown('<div class="page-title">🗺️ Peta Sebaran Harga</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Harga per pasar berdasarkan data terbaru · {df_raw["mkt_name"].nunique()} pasar Indonesia</div>', unsafe_allow_html=True)
 
    kom_peta = st.selectbox("Pilih Komoditas", list(KOMODITAS_MAP.keys()))
    info_peta = KOMODITAS_MAP[kom_peta]
 
    # Ambil data terbaru per pasar (3 bulan terakhir)
    cutoff = df_raw['price_date'].max() - pd.DateOffset(months=3)
    df_peta = df_raw[df_raw['price_date'] >= cutoff].groupby(
        ['mkt_name', 'adm1_name', 'lat', 'lon']
    )[info_peta["col"]].mean().reset_index().dropna()
 
    if not df_peta.empty:
        fig_map = go.Figure(go.Scattermapbox(
            lat=df_peta['lat'], lon=df_peta['lon'],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=12, color=df_peta[info_peta["col"]],
                colorscale=[[0,"#2ECC71"],[0.5,"#F39C12"],[1,"#E74C3C"]],
                colorbar=dict(title=f"Harga (Rp{info_peta['unit']})", tickformat=","),
                opacity=0.85,
            ),
            text=[
                f"<b>{row['mkt_name']}</b><br>{row['adm1_name'].title()}<br>Rp {row[info_peta['col']]:,.0f}{info_peta['unit']}"
                for _, row in df_peta.iterrows()
            ],
            hoverinfo="text",
        ))
        fig_map.update_layout(
            mapbox_style="carto-positron",
            mapbox=dict(center=dict(lat=-2.5, lon=117.5), zoom=4),
            height=480, margin=dict(l=0,r=0,t=0,b=0),
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
 
        c1, c2, c3 = st.columns(3)
        with c1:
            idx_min = df_peta[info_peta['col']].idxmin()
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Harga Terendah</div>
                <div class="metric-value" style="font-size:20px">Rp {df_peta[info_peta['col']].min():,.0f}</div>
                <div class="chg-nt">{df_peta.loc[idx_min,'mkt_name']}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Harga Rata-rata</div>
                <div class="metric-value" style="font-size:20px">Rp {df_peta[info_peta['col']].mean():,.0f}</div>
                <div class="chg-nt">{len(df_peta)} pasar</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            idx_max = df_peta[info_peta['col']].idxmax()
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Harga Tertinggi</div>
                <div class="metric-value" style="font-size:20px">Rp {df_peta[info_peta['col']].max():,.0f}</div>
                <div class="chg-nt">{df_peta.loc[idx_max,'mkt_name']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning(f"Data lokasi untuk {kom_peta} tidak tersedia.")
 
 
# ─────────────────────────────────────────────
#  HALAMAN: REKOMENDASI RESEP
# ─────────────────────────────────────────────
elif "Rekomendasi Resep" in page:
    st.markdown('<div class="page-title">🍳 Cari Resep dari Bahanmu!</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Pilih 1 hingga 3 komoditi yang kamu miliki di dapur untuk mendapatkan rekomendasi hidangan.</div>', unsafe_allow_html=True)

    df_resep = load_resep_data()
    
    if df_resep is None:
        st.error("⚠️ File resep_bersih.csv tidak ditemukan di path lokal yang ditentukan.")
    else:
        model_resep = RecipeRecommender(df_resep)

        UI_TO_MODEL = {
            "Daging Sapi": "meat_beef", "Ayam": "meat_chicken", "Telur": "eggs",
            "Bawang Merah": "onions", "Cabai": "chili", "Bawang Putih": "garlic",
            "Minyak Goreng": "oil", "Beras": "rice", "Gula": "sugar"
        }
        
        daftar_komoditi_ui = list(UI_TO_MODEL.keys())

        input_ui = st.multiselect(
            "Pilih Komoditi:", 
            options=daftar_komoditi_ui,
            max_selections=3
        )

        if st.button("Cari Resep Sekarang!", type="primary"):
            if not input_ui:
                st.warning("Pilih minimal 1 bahan terlebih dahulu!")
            else:
                
                input_model = [UI_TO_MODEL[item] for item in input_ui]
                st.success(f"Mencari resep untuk bahan: {', '.join(input_ui)}...")
                
                hasil = model_resep.recommend(input_model)
                
                if hasil.empty:
                    st.error("Maaf, tidak ada resep yang cocok dengan bahan tersebut.")
                else:
                    st.markdown(f'<div class="sec-title">Ditemukan {len(hasil)} resep yang cocok!</div><br>', unsafe_allow_html=True)
                    
                    for index, row in hasil.head(50).iterrows():
                        
                        st.markdown('<div class="metric-card" style="margin-bottom: 16px;">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 2.5])
                        
                        with col1:
                            if pd.notna(row['Images']) and str(row['Images']).startswith('http'):
                                st.image(row['Images'], use_container_width=True)
                            else:
                                st.info("Gambar tidak tersedia")
                                
                        with col2:
                            st.markdown(f'<div class="sec-title" style="font-size: 18px;">{row["Name"]}</div>', unsafe_allow_html=True)
                            st.write(f"✅ **Bahan kamu yang terpakai:** {', '.join(row['matched_ingredients']).title()}")
                            st.write(f"🛒 **Bahan yang perlu dibeli ({row['missing_count']}):** {', '.join(row['missing_ingredients']).title()}")
                        
                            with st.expander("Lihat Cara Memasak"):
                                st.markdown(row['RecipeInstructions'])
                                
                        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HALAMAN: CHATBOT LLM
# ─────────────────────────────────────────────
elif "Chatbot LLM" in page:
    st.markdown('<div class="page-title">💬 Chatbot AI Asisten Pangan</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Asisten pintar untuk menganalisis tren harga dan dataset pangan langsung dari database</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("💡 **Tips:** Coba tanyakan harga tertinggi atau terendah komoditas.")
    with col2:
        st.info("📈 **Tips:** Tanyakan perbandingan tren harga antar komoditas.")
    with col3:
        st.info("📍 **Tips:** Spesifikkan nama kota atau provinsi agar pencarian akurat.")

    st.markdown("<br>", unsafe_allow_html=True)

    @st.cache_resource
    def inisialisasi_agen():
        
        # Ambil API key dari Secrets (lokal: file .streamlit/secrets.toml)
        if "MISTRAL_API_KEY" in st.secrets:
        os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]
        elif not os.environ.get("MISTRAL_API_KEY"):
        st.error("MISTRAL_API_KEY belum diatur. Tambahkan di Streamlit Secrets atau .streamlit/secrets.toml.")
        st.stop()
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path_str = os.path.join(BASE_DIR, "data", "pangan.db")
        db_path = f"sqlite:///{db_path_str.replace('\\', '/')}"

        db = SQLDatabase.from_uri(db_path)

        llm = ChatMistralAI(model="mistral-large-2512", temperature=0)
        
        def get_schema(_):
            return db.get_table_info()
        
        def bersihkan_sql(teks):
            return teks.replace("```sql", "").replace("```", "").strip()

        sql_prompt = PromptTemplate.from_template(
            "Kamu adalah ahli SQLite. Tulis query SQL yang valid untuk menjawab pertanyaan ini.\n"
            "Gunakan skema tabel berikut:\n{schema}\n\n"
            "Pertanyaan: {question}\n"
            "Hanya kembalikan query SQL-nya saja, tanpa markdown, penjelasan, atau teks lainnya."
        )

        generate_query_chain = (
            RunnablePassthrough.assign(schema=get_schema)
            | sql_prompt
            | llm
            | StrOutputParser()
            | bersihkan_sql
        )

        execute_query = QuerySQLDataBaseTool(db=db)

        answer_prompt = PromptTemplate.from_template(
            "Jawab pertanyaan pengguna berdasarkan data asli dari database di bawah ini.\n"
            "Jawablah dengan bahasa Indonesia.\n\n"
            "Pertanyaan: {question}\n"
            "Query SQL: {query}\n"
            "Data Database: {result}\n\n"
            "Jawaban Anda:"
        )

        chain = (
            RunnablePassthrough.assign(query=generate_query_chain)
            .assign(result=lambda x: execute_query.invoke(x["query"]))
            | answer_prompt
            | llm
            | StrOutputParser()
        )

        return chain


    try:
        agen_pangan = inisialisasi_agen()
    except Exception as e:
        st.error(f"⚠️ Gagal memuat database atau model AI. Pastikan file 'pangan.db' tersedia di lokasi path. Pesan error: {e}")
        st.stop()

    if "pesan_chat" not in st.session_state:
        st.session_state.pesan_chat = [
            {"role": "assistant", "content": "Halo! Saya adalah asisten pintar PASTI. Komoditas apa yang ingin kamu cek harganya di dalam database hari ini?"}
        ]

    for pesan in st.session_state.pesan_chat:
        with st.chat_message(pesan["role"]):
            st.markdown(pesan["content"])

    if pertanyaan := st.chat_input("Ketik pertanyaanmu di sini..."):
        st.session_state.pesan_chat.append({"role": "user", "content": pertanyaan})
        with st.chat_message("user"):
            st.markdown(pertanyaan)

        with st.chat_message("assistant"):
            with st.spinner("Sedang mengecek brankas data..."):
                try:
                    jawaban_bersih = agen_pangan.invoke({"question": pertanyaan})
                    
                    st.markdown(jawaban_bersih)
                    st.session_state.pesan_chat.append({"role": "assistant", "content": jawaban_bersih})
                    
                except Exception as e:
                    st.error(f"Error detail: {e}")


# ─────────────────────────────────────────────
#  HALAMAN: RIWAYAT
# ─────────────────────────────────────────────
elif "Riwayat" in page:
    st.markdown('<div class="page-title">🕐 Data Historis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Riwayat harga · {wilayah_filter.title()} · 2007 – 2026</div>', unsafe_allow_html=True)
 
    kom_hist = st.selectbox("Komoditas", list(KOMODITAS_MAP.keys()))
    info_hist = KOMODITAS_MAP[kom_hist]
 
    df_hist = df_raw[df_raw['adm1_name'] == wilayah_filter][
        ['price_date', 'mkt_name', info_hist["col"]]
    ].dropna().sort_values('price_date', ascending=False)
 
    if not df_hist.empty:
        df_show = df_hist.copy()
        df_show.columns = ['Tanggal', 'Nama Pasar', f'Harga {kom_hist} (Rp)']
        df_show['Tanggal'] = df_show['Tanggal'].dt.strftime('%B %Y')
        df_show[f'Harga {kom_hist} (Rp)'] = df_show[f'Harga {kom_hist} (Rp)'].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(df_show.head(100), hide_index=True, use_container_width=True)
        st.caption(f"Menampilkan 100 data terbaru dari total {len(df_hist):,} baris")
    else:
        st.warning(f"Data {kom_hist} tidak tersedia untuk {wilayah_filter.title()}")
 
 
# ─────────────────────────────────────────────
#  HALAMAN: PENGATURAN
# ─────────────────────────────────────────────
elif "Pengaturan" in page:
    st.markdown('<div class="page-title">⚙️ Pengaturan</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Konfigurasi model dan koneksi dataset</div>', unsafe_allow_html=True)
 
    with st.expander("🤖 Status Model ML", expanded=True):
        _model_ok, _ = load_model_artifacts()
        _data_ok = load_pred_data() is not None
        if _model_ok is not None and _data_ok:
            st.success("✅ Model XGBoost aktif dan terhubung ke halaman Prediksi Harga.")
        else:
            st.warning("⚠️ Model belum lengkap — tambahkan file model ke repo.")
        st.write("**Algoritma:** XGBoost Regressor (prediksi harga per pasar)")
        st.write("**Horizon prediksi:** 2 bulan ke depan (rekursif)")
        st.write("**Rata-rata error (MAPE) data uji:** sekitar 3,4%")
        st.markdown(
            '<div style="font-size:12px;color:#9ca3af;margin-top:8px;">'
            'File yang dipakai: <code>model_harga_pangan.pkl</code>, '
            '<code>label_encoders.pkl</code>, <code>dataset_bersih.csv</code>.'
            '</div>',
            unsafe_allow_html=True
        )
 
    with st.expander("📊 Informasi Dataset", expanded=True):
        st.write(f"**File:** IDN_RTFP_mkt_2007_2026-04-08__1_.csv")
        st.write(f"**Total baris:** {len(df_raw):,}")
        st.write(f"**Rentang tanggal:** {df_raw['price_date'].min().strftime('%B %Y')} – {df_raw['price_date'].max().strftime('%B %Y')}")
        st.write(f"**Jumlah pasar:** {df_raw['mkt_name'].nunique()}")
        st.write(f"**Jumlah provinsi:** {df_raw['adm1_name'].nunique()}")
        st.write(f"**Sumber:** World Bank RTFP · IDN_2021_RTFP_V02_M")
 
    with st.expander("🌾 Komoditas Tersedia"):
        for nama, info in KOMODITAS_MAP.items():
            total = df_raw[info["col"]].notna().sum()
            st.write(f"{info['emoji']} **{nama}** (`{info['col']}`) — {total:,} data poin")
