import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="Teman Bisnis AI",
    page_icon="💼",
    layout="wide",
)

st.markdown("""
<style>
    /* Bikin tombol di sidebar lebih rapat dan nggak makan tempat */
    [data-testid="stSidebar"] .stButton button {
        margin-top: -10px;
        padding: 2px 5px !important;
        height: auto !important;
        min-height: 0px !important;
    }
    /* Memastikan teks tidak numpuk */
    [data-testid="stSidebar"] .stButton p {
        font-size: 13px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* Khusus tombol hapus (X) biar warna merah pas di-hover dan kelihatan */
    [data-testid="stSidebar"] div[data-testid="column"]:nth-child(2) button {
        color: #ff4b4b;
        border-color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
HISTORY_FILE = "./chat_sessions.json"

QUICK_ACTIONS = [
    "Buatkan rencana bisnis awal",
    "Simulasi keuangan 1 tahun",
    "Kode KBLI yang relevan",
    "Template kontrak sewa",
    "Strategi marketing awal",
    "Analisis risiko bisnis",
]

# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load_sessions():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(HISTORY_FILE, "w") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def serialize(history):
    return [
        {"role": "human" if isinstance(m, HumanMessage) else "ai", "content": m.content}
        for m in history
    ]

def deserialize(data):
    return [
        HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
        for m in data
    ]

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for key, val in [
    ("sessions", load_sessions()),
    ("current_session", None),
    ("chat_history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── LOAD RESOURCES ────────────────────────────────────────────────────────────
@st.cache_resource
def load_resources():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="temanbisnis",
    )
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=2048,
    )
    return vector_db, llm

vector_db, llm = load_resources()

# ── AI ────────────────────────────────────────────────────────────────────────
def get_ai_response(query, history):
    docs = vector_db.similarity_search(query, k=4)
    konteks = "\n\n".join([d.page_content for d in docs])

    history_str = "".join(
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}\n"
        for m in history[-6:]
    )

    prompt = f"""
ROLE: Kamu adalah Senior Startup Consultant & Partner Bisnis untuk UMKM Indonesia.
Gaya: Profesional, conversational, to-the-point. Pakai Bahasa Indonesia.

DATA RELEVAN DARI DATABASE:
{konteks}

HISTORY CHAT:
{history_str}

PERTANYAAN: {query}

ATURAN:
1. Langsung eksekusi, bukan teori panjang.
2. Keuangan = simulasi angka nyata.
3. Legal = sebut kode KBLI dari data bila ada.
4. Tawarkan draf (kontrak/rencana/strategi) bila relevan.
5. Pakai markdown: heading dan bullet yang jelas.
"""
    return llm.invoke(prompt)

# ── SESSION HELPERS ────────────────────────────────────────────────────────────
def new_session():
    sid = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.current_session = sid
    st.session_state.chat_history = []
    st.session_state.sessions[sid] = {"title": "Obrolan Baru", "history": []}
    save_sessions(st.session_state.sessions)

def load_session(sid):
    st.session_state.current_session = sid
    st.session_state.chat_history = deserialize(st.session_state.sessions[sid]["history"])

def save_current():
    sid = st.session_state.current_session
    if not sid:
        return
    history = st.session_state.chat_history
    title = next(
        (m.content[:45] + ("..." if len(m.content) > 45 else "") for m in history if isinstance(m, HumanMessage)),
        "Obrolan Baru",
    )
    st.session_state.sessions[sid] = {"title": title, "history": serialize(history)}
    save_sessions(st.session_state.sessions)

def send_message(query):
    if not st.session_state.current_session:
        new_session()
    st.session_state.chat_history.append(HumanMessage(content=query))
    with st.spinner("Menganalisis..."):
        resp = get_ai_response(query, st.session_state.chat_history)
    st.session_state.chat_history.append(AIMessage(content=resp.content))
    save_current()
    st.rerun()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💼 Teman Bisnis AI")
    st.caption("RAG-Powered Business Consultant")
    st.divider()

    if st.button("✏️ Obrolan Baru", use_container_width=True):
        new_session()
        st.rerun()

    st.divider()

    if st.session_state.sessions:
        st.markdown("**Riwayat Chat**")
        
        sorted_keys = sorted(st.session_state.sessions.keys(), reverse=True)
        
        for sid in sorted_keys:
            title = st.session_state.sessions[sid]["title"]
            is_active = (sid == st.session_state.current_session)
            
            # Kita pakai kolom tanpa gap agar tombol X tidak terdorong keluar
            col_txt, col_del = st.columns([5, 1])
            
            with col_txt:
                label = f"🎯 {title}" if is_active else f"💬 {title}"
                if st.button(label, key=f"sess_{sid}", use_container_width=True):
                    load_session(sid)
                    st.rerun()
                
            with col_del:
                # Tombol X kita kasih key unik dan container width biar muncul
                if st.button("X", key=f"del_{sid}", use_container_width=True):
                    del st.session_state.sessions[sid]
                    save_sessions(st.session_state.sessions)
                    if st.session_state.current_session == sid:
                        st.session_state.current_session = None
                        st.session_state.chat_history = []
                    st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────
if not st.session_state.current_session:
    # Landing
    st.title("💼 Teman Bisnis AI")
    st.markdown("Konsultan bisnis berbasis RAG — siap bantu dari riset sampai scale up.")
    st.divider()
    st.markdown("#### ⚡ Mulai dengan topik:")
    cols = st.columns(3)
    for i, action in enumerate(QUICK_ACTIONS):
        with cols[i % 3]:
            if st.button(action, use_container_width=True, key=f"home_{i}"):
                send_message(action)

else:
    # Chat view
    st.title("💼 Teman Bisnis AI")
    st.divider()

    # Render chat history
    for msg in st.session_state.chat_history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # Quick actions (below chat, above input)
    with st.expander("⚡ Aksi Cepat"):
        cols = st.columns(3)
        for i, action in enumerate(QUICK_ACTIONS):
            with cols[i % 3]:
                if st.button(action, use_container_width=True, key=f"qa_{i}"):
                    send_message(action)

    # Chat input
    if user_input := st.chat_input("Tanya soal bisnismu..."):
        send_message(user_input)