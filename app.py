import streamlit as st
import pandas as pd
import os
from src.scraper import PokotScraper
from src.rag import PokotRAG
from src.translator import PokotTranslator

# Page configuration
st.set_page_config(page_title="Pokot-English Translator", page_icon="🌍", layout="wide")

st.title("🌍 Pokot-English Neural Translator")
st.markdown("""
This application demonstrates a **Retrieval-Augmented Generation (RAG)** approach to translating the low-resource **Pokot** language.
By leveraging biblical verse alignments, the system provides high-quality contextual examples to a Large Language Model to improve translation accuracy.
""")

# Sidebar for configuration and data management
st.sidebar.header("Project Controls")
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

# Initialize RAG and Translator with Firestore Data
@st.cache_resource
def init_systems():
    # 1. Initialize Firestore
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': 'auth-4eef8',
        })
    
    db = firestore.Client(project='auth-4eef8')
    print("Fetching documents from Firestore...")
    docs = db.collection('pokot_verses').stream()
    documents = [doc.to_dict() for doc in docs]
    print(f"Fetched {len(documents)} documents.")

    # 2. Initialize and Index RAG
    rag = PokotRAG()
    if documents:
        rag.index_documents(documents)
    
    # 3. Initialize Translator (Vertex AI)
    translator = PokotTranslator(rag_system=rag)
    
    return rag, translator, documents

rag_system, translator_system, documents = init_systems()

# Data Management in Sidebar
st.sidebar.success(f"✅ Loaded {len(documents)} verses from Firestore.")
if st.sidebar.button("🔄 Re-fetch & Re-index"):
    st.cache_resource.clear()
    st.rerun()

# Main Translation Interface
st.subheader("Translation Interface")
pokot_input = st.text_area("Enter Pokot text to translate:", 
                           placeholder="e.g., Yomunto, kitɔrɔt Kɔkɔ Pɛlɛl kɔ ayɛng",
                           height=150)

col1, col2 = st.columns([1, 3])
with col1:
    use_rag = st.checkbox("Enable RAG", value=True, help="Use similar biblical verses to guide the translation.")
    translate_btn = st.button("Translate ➡️", type="primary")

if translate_btn:
    if pokot_input:
        with st.spinner("Processing translation..."):
            result = translator_system.translate(pokot_input, use_rag=use_rag)
            
            st.markdown("### English Translation:")
            st.info(result['translation'])
            
            if use_rag and result['context']:
                with st.expander("🔍 View Retrieved Context (Similar Verses)"):
                    st.markdown("The following verses were retrieved from the corpus to assist the translation:")
                    for i, ctx in enumerate(result['context']):
                        st.markdown(f"**Example {i+1}** (Ref: `{ctx['reference']}`, Score: `{ctx['score']:.4f}`)")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"*Pokot:* {ctx['pokot']}")
                        with c2:
                            st.markdown(f"*English:* {ctx['english']}")
                        st.divider()
    else:
        st.warning("Please enter some Pokot text to translate.")

# Data Overview Section
st.divider()
st.subheader("📊 Parallel Corpus Overview")
if documents:
    df = pd.DataFrame(documents)
    st.write(f"The current dataset contains **{len(df)}** parallel verse pairs from Firestore.")
    st.dataframe(df.head(10), use_container_width=True)
else:
    st.info("No data found in Firestore.")

# Footer
st.markdown("---")
st.markdown("Built for the Pokot Language Preservation Project.")
