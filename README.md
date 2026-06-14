# PASTI (Prediksi Harga Pasar Terkini) — Prediksi & Rekomendasi Harga Pangan

[](https://ibb.co.com/vCPR9cND)

> 🔗 **Live App:** [pasti-rekomendasi-harga-pangan.streamlit.app](https://pasti-rekomendasi-harga-pangan.streamlit.app/)

## About PASTI
**PASTI** is a web-based dashboard for monitoring and forecasting staple food commodity prices across markets in Indonesia. It combines a machine-learning model (XGBoost) that predicts prices up to two months ahead with an interactive dashboard, a price map, and an AI assistant powered by a large language model.

**PASTI** adalah dashboard berbasis web untuk memantau dan memprediksi harga komoditas pangan pokok di berbagai pasar di Indonesia. Aplikasi ini menggabungkan model machine learning (XGBoost) yang memprediksi harga hingga dua bulan ke depan dengan dashboard interaktif, peta sebaran harga, dan asisten AI berbasis large language model.

## Key Features
- 📊 **Overview Dashboard** — ringkasan harga terkini per komoditas beserta perubahan bulanannya.
- 📈 **Prediksi Harga** — prediksi harga 2 bulan ke depan untuk tiap pasar menggunakan XGBoost (prediksi rekursif).
- 🗺️ **Peta Harga** — sebaran harga komoditas di pasar-pasar seluruh Indonesia.
- 🤖 **AI Chatbot** — asisten tanya-jawab seputar harga pangan, ditenagai Mistral AI.

## Resources

### Tools
- Google Colab (pelatihan & eksperimen model)
- Visual Studio Code
- GitHub
- Streamlit Community Cloud (deployment)

### Programming Language
- Python

### Libraries & Frameworks
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib & Seaborn (EDA)
- Scikit-Learn
- XGBoost
- Joblib
- holidays

### Machine Learning
- **XGBoost Regressor** — model produksi untuk prediksi harga 2 bulan ke depan
- Pipeline pendukung: LabelEncoder, TimeSeriesSplit, GridSearchCV

### LLM / Chatbot API
- [Mistral AI](https://mistral.ai/) — model `mistral-large-2512`

### Data Sources
- **World Bank — Real-Time Food Prices (RTFP), Indonesia** ([microdata.worldbank.org/catalog/6166](https://microdata.worldbank.org/index.php/catalog/6166)) — data harga pangan utama.
- **Harga Bensin Indonesia** ([Trading Economics](https://id.tradingeconomics.com/indonesia/gasoline-prices)) — fitur indikator ekonomi.
- **Hari besar nasional Indonesia** — library Python `holidays`.

## Model Overview
- **Target:** harga komoditas pangan (rupiah).
- **Fitur:** lag harga (1, 2, dan 12 bulan), rata-rata bergerak (3 & 12 bulan), harga bensin (lag 2 bulan), flag hari besar (Idul Fitri, Imlek, Natal, Tahun Baru), serta lokasi pasar (provinsi, kabupaten, nama pasar).
- **Horizon:** 2 bulan ke depan (prediksi rekursif).
- **Rata-rata error (MAPE) pada data uji:** sekitar 3,4%.

## How to Run Locally
1. Clone repository

```
git clone https://github.com/MelaniS00/Project-Capstone-Tempa.git
cd Project-Capstone-Tempa
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Atur API key Mistral untuk fitur chatbot. Buat file `.streamlit/secrets.toml` lalu isi:

```
MISTRAL_API_KEY = "your_api_key_here"
```

4. Jalankan aplikasi

```
streamlit run app.py
```

Atau langsung kunjungi versi online:
#### [**Buka PASTI di sini**](https://pasti-rekomendasi-harga-pangan.streamlit.app/)

> ⚠️ **Catatan keamanan:** jangan pernah menulis API key langsung di dalam `app.py`. Simpan di `secrets.toml` (lokal) atau di menu *Secrets* Streamlit Cloud, dan pastikan `secrets.toml` masuk ke `.gitignore` agar tidak ikut ter-push ke GitHub.

## Project Structure
```
Project-Capstone-Tempa/
├── .streamlit/
│   └── config.toml                       # tema tampilan (light mode)
├── app.py                                # aplikasi dashboard Streamlit
├── requirements.txt                      # daftar dependensi
├── model_harga_pangan.pkl                # model XGBoost terlatih
├── label_encoders.pkl                    # encoder kategori
├── dataset_bersih.csv                    # data per-pasar (fitur prediksi)
├── IDN_RTFP_mkt_2007_2026-04-08__1_.csv  # data mentah World Bank RTFP
└── README.md
```

## Dataset Citation
Andrée, B. P. J. (2021). *Monthly food price estimates by product and market* (IDN_2021_RTFP_v02_M). Washington, DC: World Bank Microdata Library. https://doi.org/10.48529/2ZH0-JF55

## Our Team

<!-- Lengkapi nama, ID, dan peran tiap anggota -->
1. [@MelaniS00](https://github.com/MelaniS00) — AIC283B6X0046 - Melani Siyamafiroh
2. [@NaufalN](https://github.com/NaufalN-creator) — AIC283B6Y0011 - Naufal Nadhif
3. [@ridhozh](https://github.com/ridhozh) — AIC308B6Y0031 - Ridho Zikril Hidayatullah
4. [@NathAdr](https://github.com/NathAdr) — AIC244B6Y0050 - Nathan Adrian Chandra
