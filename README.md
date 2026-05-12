# 💼 Teman Bisnis AI
**Senior Startup Consultant & Partner Bisnis untuk UMKM Indonesia**

Aplikasi asisten cerdas berbasis AI yang membantu pelaku usaha dalam merancang rencana bisnis, analisis keuangan, hingga pemetaan kode KBLI menggunakan teknologi **RAG (Retrieval-Augmented Generation)**.

## 🚀 Fitur Utama
- **RAG System:** Jawaban akurat berdasarkan database referensi bisnis.
- **Simulasi Keuangan:** Perhitungan estimasi keuntungan dan risiko.
- **Smart Sidebar:** Manajemen riwayat obrolan yang rapi dan fungsional.
- **KBLI Mapper:** Membantu menentukan klasifikasi usaha secara tepat.

## 🛠️ Tech Stack
- **Interface:** Streamlit
- **LLM:** Llama 3.3 (via Groq)
- **Database:** ChromaDB (Vector Store)
- **Embeddings:** HuggingFace All-MiniLM-L6-v2
- **Orchestration:** LangChain

## 📦 Cara Instalasi
1. Clone repositori:
   ```bash
   git clone [https://github.com/AlvinMI/TemanBisnis_AI.git](https://github.com/AlvinMI/TemanBisnis_AI.git)
   cd TemanBisnis_AI

2. Buat & aktifkan Virtual Environment:
python -m venv venv
# Windows:
.\venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

4. Setup Environment Variable:
Buat file .env di root folder dan isi:
GROQ_API_KEY=isi_api_key_groq_lu

5. Jalankan Aplikasi:
streamlit run app.py

---

## 📁 Struktur Proyek
```text
.
├── app.py               # Aplikasi utama (Streamlit)
├── requirements.txt     # Daftar library Python
├── README.md            # Dokumentasi proyek
├── research.ipynb       # Notebook riset data & embedding
├── chat_sessions.json   # Penyimpanan riwayat chat lokal
├── docs/                # Dokumen referensi (KBLI, Template, dll)
├── chroma_db/           # Database Vector (Persist Directory)
├── .gitignore           # Konfigurasi file yang diabaikan Git
└── .env                 # API Key (Konfigurasi sensitif)