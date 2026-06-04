import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
 
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
    "Beras":         {"col": "rice",          "emoji": "🌾", "warna": "#2ECC71", "unit": "/kg"},
    "Cabai":         {"col": "chili",         "emoji": "🌶️", "warna": "#E74C3C", "unit": "/kg"},
    "Telur":         {"col": "eggs",          "emoji": "🥚", "warna": "#F39C12", "unit": "/kg"},
    "Minyak Goreng": {"col": "oil",           "emoji": "💧", "warna": "#3498DB", "unit": "/L"},
    "Gula":          {"col": "sugar",         "emoji": "🍬", "warna": "#9B59B6", "unit": "/kg"},
    "Ayam":          {"col": "meat_chicken",  "emoji": "🍗", "warna": "#E67E22", "unit": "/kg"},
    "Daging Sapi":   {"col": "meat_beef",     "emoji": "🥩", "warna": "#C0392B", "unit": "/kg"},
    "Bawang Merah":  {"col": "onions",        "emoji": "🧅", "warna": "#D35400", "unit": "/kg"},
    "Bawang Putih":  {"col": "garlic",        "emoji": "🧄", "warna": "#8E44AD", "unit": "/kg"},
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
 
def gen_forecast(last_price, n=6, start_date=None):
    """Forecast simulasi n bulan ke depan — ganti dengan model ML.
    start_date: titik awal forecast (default = akhir data historis).
    """
    np.random.seed(99)
    # Mulai tepat dari tanggal akhir data historis agar tidak ada gap
    if start_date is not None:
        start = pd.Timestamp(start_date).to_period("M").to_timestamp()
    else:
        start = pd.Timestamp.now().to_period("M").to_timestamp()
    dates  = [start + pd.DateOffset(months=i) for i in range(n)]
    prices = [last_price]
    upper  = [last_price]
    lower  = [last_price]
    for i in range(1, n):
        chg = 0.003 + np.random.normal(0, 0.008)
        prices.append(prices[-1] * (1 + chg))
        upper.append(prices[-1] * (1 + 0.025 * (i / n)))
        lower.append(prices[-1] * (1 - 0.025 * (i / n)))
    return dates, prices, upper, lower
 
 
# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 PASTI")
    st.markdown("---")
 
    st.markdown("**NAVIGASI**")
    page = st.radio(
        "nav",
        ["🏠  Dashboard", "📈  Prediksi Harga", "🗺️  Peta Wilayah", "🕐  Riwayat", "⚙️  Pengaturan"],
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
    st.caption(f"Dataset: World Bank RTFP\n{len(df_raw):,} baris · 223 pasar\n2007 – Apr 2026")
 
 
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
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="badge-on">● Live Data</span>', unsafe_allow_html=True)
 
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
        st.markdown('<div class="sec-title">Tren & Forecast Harga</div>', unsafe_allow_html=True)
        kom_chart = st.selectbox("Pilih komoditas chart", selected, label_visibility="collapsed")
        info = KOMODITAS_MAP[kom_chart]
 
        n_map = {"6 Bulan": 6, "12 Bulan": 12, "24 Bulan": 24, "Semua Data": 999}
        tren = get_tren_bulanan(wilayah_filter, info["col"], n_map[periode_filter])
 
        if tren.empty:
            st.warning(f"Data {kom_chart} tidak tersedia untuk {wilayah_filter.title()}")
        else:
            last_price = tren.iloc[-1][info["col"]]
            last_date  = tren.iloc[-1]["price_date"]
            # Forecast dimulai tepat dari tanggal akhir data — tidak ada gap
            fc_dates, fc_prices, fc_up, fc_dn = gen_forecast(last_price, n=7, start_date=last_date)
            today_x = last_date.strftime("%Y-%m-%d")
 
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fc_dates + fc_dates[::-1], y=fc_up + fc_dn[::-1],
                fill="toself", fillcolor="rgba(30,45,64,0.10)",
                line=dict(color="rgba(0,0,0,0)"), name="Interval 95%",
            ))
            fig.add_trace(go.Scatter(
                x=tren['price_date'], y=tren[info["col"]],
                mode="lines+markers",
                line=dict(color=info["warna"], width=2.5),
                marker=dict(size=4),
                name="Harga aktual",
            ))
            fig.add_trace(go.Scatter(
                x=fc_dates, y=fc_prices, mode="lines",
                line=dict(color=info["warna"], width=2.5, dash="dot"),
                name="Forecast (simulasi)",
            ))
            fig.add_shape(
                type="line", x0=today_x, x1=today_x, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="#9ca3af", width=1, dash="dash"),
            )
            fig.add_annotation(
                x=today_x, y=0.98, xref="x", yref="paper",
                text="Hari ini", showarrow=False,
                font=dict(size=10, color="#9ca3af"), xanchor="left",
            )
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
 
    pct_beras = hitung_pct_change(wilayah_filter, "rice")
    pct_cabai = hitung_pct_change(wilayah_filter, "chili")
    pct_minyak = hitung_pct_change(wilayah_filter, "oil")
 
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
            Forecast saat ini masih simulasi — hubungkan model ML untuk prediksi nyata.</div>
        </div>""", unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────
#  HALAMAN: PREDIKSI
# ─────────────────────────────────────────────
elif "Prediksi" in page:
    st.markdown('<div class="page-title">📈 Prediksi Harga</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Lihat & prediksi harga berdasarkan rentang bulan · {wilayah_filter.title()}</div>', unsafe_allow_html=True)

    # Buat daftar semua bulan yang tersedia di dataset
    semua_bulan = sorted(df_raw["price_date"].dt.to_period("M").unique())
    bulan_str   = [str(b) for b in semua_bulan]  # format: "2007-01", "2007-02", dst

    # Fungsi bantu: format bulan jadi label ramah
    def fmt(b): 
        return pd.Period(b, "M").to_timestamp().strftime("%B %Y")

    bulan_label = [fmt(b) for b in bulan_str]
    label_to_str = dict(zip(bulan_label, bulan_str))

    with st.form("form_prediksi"):
        c1, c2 = st.columns(2)
        with c1: kom   = st.selectbox("Komoditas", list(KOMODITAS_MAP.keys()))
        with c2: wil   = st.selectbox("Wilayah", PROVINSI_LIST,
                           index=PROVINSI_LIST.index(wilayah_filter))

        c3, c4, c5 = st.columns(3)
        with c3:
            # Default: 12 bulan lalu
            default_start = max(0, len(bulan_label) - 22)
            bulan_mulai_lbl = st.selectbox("Bulan Mulai", bulan_label,
                                           index=default_start)
        with c4:
            default_end = len(bulan_label) - 1
            bulan_akhir_lbl = st.selectbox("Bulan Akhir", bulan_label,
                                           index=default_end)
        with c5:
            model = st.selectbox("Model ML", ["LSTM (belum ada)", "XGBoost (belum ada)", "Simulasi"])

        run = st.form_submit_button("🚀 Tampilkan & Prediksi", use_container_width=True)

    if run:
        info = KOMODITAS_MAP[kom]

        # Konversi label → period string → timestamp
        bulan_mulai_str  = label_to_str[bulan_mulai_lbl]
        bulan_akhir_str  = label_to_str[bulan_akhir_lbl]
        tgl_mulai = pd.Period(bulan_mulai_str, "M").to_timestamp()
        tgl_akhir = pd.Period(bulan_akhir_str, "M").to_timestamp() + pd.offsets.MonthEnd(0)

        if tgl_mulai > tgl_akhir:
            st.error("⚠️ Bulan Mulai tidak boleh lebih besar dari Bulan Akhir!")
        else:
            # Ambil data historis pada rentang yang dipilih
            df_range = df_raw[
                (df_raw["adm1_name"] == wil) &
                (df_raw["price_date"] >= tgl_mulai) &
                (df_raw["price_date"] <= tgl_akhir)
            ][["price_date", info["col"]]].dropna()

            if df_range.empty:
                st.warning(f"Tidak ada data {kom} untuk {wil.title()} pada rentang {bulan_mulai_lbl} – {bulan_akhir_lbl}")
            else:
                # Rata-rata per bulan
                df_range = df_range.set_index("price_date").resample("MS").mean().reset_index()

                harga_awal  = df_range.iloc[0][info["col"]]
                harga_akhir = df_range.iloc[-1][info["col"]]
                selisih     = harga_akhir - harga_awal
                pct_chg     = round(selisih / harga_awal * 100, 1) if harga_awal > 0 else 0
                n_bulan_range = len(df_range)

                # Ambil tanggal dan harga terakhir dari data historis yang sudah diresample
                tgl_data_akhir = df_range.iloc[-1]["price_date"]

                # Forecast dimulai TEPAT dari bulan terakhir data historis
                fc_dates, fc_prices, fc_up, fc_dn = gen_forecast(harga_akhir, n=7, start_date=tgl_data_akhir)

                # ── Metric cards ──
                r1, r2, r3, r4 = st.columns(4)
                with r1:
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-label">Harga Awal ({bulan_mulai_lbl})</div>
                        <div class="metric-value">Rp {harga_awal:,.0f}</div>
                        <div class="chg-nt">{kom} · {wil.title()}</div>
                    </div>""", unsafe_allow_html=True)
                with r2:
                    chg_cls = "chg-up" if selisih >= 0 else "chg-down"
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-label">Harga Akhir ({bulan_akhir_lbl})</div>
                        <div class="metric-value">Rp {harga_akhir:,.0f}</div>
                        <div class="{chg_cls}">{"+" if selisih>=0 else ""}Rp {selisih:,.0f}</div>
                    </div>""", unsafe_allow_html=True)
                with r3:
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-label">Perubahan Periode</div>
                        <div class="metric-value">{'+' if pct_chg>=0 else ''}{pct_chg}%</div>
                        <div class="chg-nt">{n_bulan_range} bulan data</div>
                    </div>""", unsafe_allow_html=True)
                with r4:
                    pred_next = round(fc_prices[1], 0) if len(fc_prices) > 1 else harga_akhir
                    selisih_fc = pred_next - harga_akhir
                    chg_fc = "chg-up" if selisih_fc >= 0 else "chg-down"
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-label">Forecast Bulan Berikutnya</div>
                        <div class="metric-value">Rp {pred_next:,.0f}</div>
                        <div class="{chg_fc}">{"+" if selisih_fc>=0 else ""}Rp {selisih_fc:,.0f}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Chart historis + forecast ──
                st.markdown(
                    f'<div class="sec-title">{info["emoji"]} {kom} · {wil.title()}</div>'
                    f'<div class="sec-sub">{bulan_mulai_lbl} – {bulan_akhir_lbl}</div>',
                    unsafe_allow_html=True
                )
                today_x = tgl_data_akhir.strftime("%Y-%m-%d")
                fig2 = go.Figure()

                # Confidence band forecast
                fig2.add_trace(go.Scatter(
                    x=fc_dates + fc_dates[::-1], y=fc_up + fc_dn[::-1],
                    fill="toself", fillcolor="rgba(30,45,64,0.10)",
                    line=dict(color="rgba(0,0,0,0)"), name="Interval 95%"
                ))
                # Data historis rentang terpilih
                fig2.add_trace(go.Scatter(
                    x=df_range["price_date"], y=df_range[info["col"]],
                    mode="lines+markers",
                    line=dict(color=info["warna"], width=2.5),
                    marker=dict(size=5),
                    name=f"Harga aktual ({bulan_mulai_lbl} – {bulan_akhir_lbl})"
                ))
                # Forecast — titik pertama = harga akhir historis agar tersambung
                fig2.add_trace(go.Scatter(
                    x=fc_dates, y=fc_prices,
                    mode="lines",
                    line=dict(color=info["warna"], width=2.5, dash="dot"),
                    name="Forecast (simulasi)"
                ))
                # Garis pemisah historis vs forecast
                fig2.add_shape(type="line", x0=today_x, x1=today_x, y0=0, y1=1,
                    xref="x", yref="paper",
                    line=dict(color="#9ca3af", width=1, dash="dash"))
                fig2.add_annotation(x=today_x, y=0.98, xref="x", yref="paper",
                    text="Akhir data", showarrow=False,
                    font=dict(size=10, color="#9ca3af"), xanchor="left")

                fig2.update_layout(
                    height=320, margin=dict(l=0,r=0,t=8,b=0),
                    paper_bgcolor="white", plot_bgcolor="white",
                    font=dict(family="Plus Jakarta Sans", size=12),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    xaxis=dict(showgrid=False, linecolor="#e5e7eb"),
                    yaxis=dict(showgrid=True, gridcolor="#f3f4f6",
                               tickformat=",", tickprefix="Rp ", linecolor="#e5e7eb"),
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

                # ── Tabel ringkasan per bulan ──
                st.markdown('<div class="sec-title">Rincian Harga Per Bulan</div>', unsafe_allow_html=True)
                df_show = df_range.copy()
                df_show["Bulan"]  = df_show["price_date"].dt.strftime("%B %Y")
                df_show["Harga"]  = df_show[info["col"]].apply(lambda x: f"Rp {x:,.0f}")
                df_show["Δ MoM"]  = df_show[info["col"]].pct_change().mul(100).round(1)
                df_show["Δ MoM"]  = df_show["Δ MoM"].apply(
                    lambda x: f"+{x}%" if x > 0 else (f"{x}%" if pd.notna(x) else "-")
                )
                st.dataframe(
                    df_show[["Bulan","Harga","Δ MoM"]].rename(columns={"Δ MoM":"Perubahan MoM"}),
                    hide_index=True, use_container_width=True
                )

                # ── Rekomendasi bisnis ──
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="sec-title">Rekomendasi Bisnis</div>', unsafe_allow_html=True)
                if pct_chg > 0:
                    st.markdown(f"""<div class="ai-box">
                        <div class="ai-box-title">📦 Tren Naik Selama Periode</div>
                        <div class="ai-box-text">Harga {kom} di {wil.title()} naik <b>+{pct_chg}%</b>
                        dari {bulan_mulai_lbl} ke {bulan_akhir_lbl} (Rp {harga_awal:,.0f} → Rp {harga_akhir:,.0f}).
                        Forecast bulan berikutnya: <b>Rp {pred_next:,.0f}</b>.
                        Pertimbangkan stok lebih awal jika tren kenaikan berlanjut.</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="ai-box">
                        <div class="ai-box-title">📉 Tren Turun Selama Periode</div>
                        <div class="ai-box-text">Harga {kom} di {wil.title()} turun <b>{pct_chg}%</b>
                        dari {bulan_mulai_lbl} ke {bulan_akhir_lbl} (Rp {harga_awal:,.0f} → Rp {harga_akhir:,.0f}).
                        Forecast bulan berikutnya: <b>Rp {pred_next:,.0f}</b>.
                        Waktu yang baik untuk pembelian jika tren penurunan berlanjut.</div>
                    </div>""", unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────
#  HALAMAN: PETA
# ─────────────────────────────────────────────
elif "Peta" in page:
    st.markdown('<div class="page-title">🗺️ Peta Sebaran Harga</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Harga per pasar berdasarkan data terbaru · 223 pasar Indonesia</div>', unsafe_allow_html=True)
 
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
 
    with st.expander("🤖 Konfigurasi Model ML", expanded=True):
        st.selectbox("Default Model", ["LSTM","XGBoost","ARIMA","Random Forest"])
        st.slider("Horizon Prediksi Default (bulan)", 1, 24, 6)
        st.slider("Threshold Confidence Minimum (%)", 50, 95, 75)
        st.markdown(
            '<div style="font-size:12px;color:#9ca3af;margin-top:8px;">'
            '⚙️ Untuk menggunakan model ML yang sesungguhnya, ganti fungsi '
            '<code>gen_forecast()</code> di <code>app.py</code> dengan output model '
            'yang telah dilatih (format .pkl / .h5 / .joblib).'
            '</div>',
            unsafe_allow_html=True
        )
 
    with st.expander("📊 Informasi Dataset", expanded=True):
        st.write(f"**File:** IDN_RTFP_mkt_2007_2026-04-08__1_.csv")
        st.write(f"**Total baris:** {len(df_raw):,}")
        st.write(f"**Rentang tanggal:** {df_raw['price_date'].min().strftime('%B %Y')} – {df_raw['price_date'].max().strftime('%B %Y')}")
        st.write(f"**Jumlah pasar:** {df_raw['mkt_name'].nunique()}")
        st.write(f"**Jumlah provinsi:** {df_raw['adm1_name'].nunique() - 1}")
        st.write(f"**Sumber:** World Bank RTFP · IDN_2021_RTFP_V02_M")
 
    with st.expander("🌾 Komoditas Tersedia"):
        for nama, info in KOMODITAS_MAP.items():
            total = df_raw[info["col"]].notna().sum()
            st.write(f"{info['emoji']} **{nama}** (`{info['col']}`) — {total:,} data poin")