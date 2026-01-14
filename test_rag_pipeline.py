from app import init_systems

if __name__ == "__main__":
    print("Testing RAG Pipeline Initialization (Cold Start)...")
    try:
        # Mock streamlit cache for testing context? 
        # Actually init_systems is decorated. Streamlit might complain if run outside st context.
        # But @st.cache_resource usually works if we dont use st.sidebar inside the function.
        # Wait, app.py has st.sidebar lines. init_systems DOES NOT have streamlit calls inside it.
        # It should be safe to import and run IF the decorators don't block execution.
        
        # However, imports in app.py might trigger top-level st commands.
        # app.py has st.set_page_config at top level. This WILL fail if not run via streamlit.
        
        # SCRIPT STRATEGY CHANGE:
        # I cannot import app.py directly because of top-level streamlit calls.
        # I should copy the logic to this test script.
        
        import firebase_admin
        from firebase_admin import credentials
        from google.cloud import firestore
        from src.rag import PokotRAG
        from src.translator import PokotTranslator
        
        print("1. initializing Firestore...")
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {'projectId': 'auth-4eef8'})
            
        db = firestore.Client(project='auth-4eef8')
        print("2. fetching documents...")
        docs = list(db.collection('pokot_verses').stream())
        documents = [d.to_dict() for d in docs]
        print(f"Fetched {len(documents)} documents.")
        
        if len(documents) == 0:
            print("WARNING: No documents fetched. Check Firestore.")
        
        print("3. Initializing RAG...")
        rag = PokotRAG()
        rag.index_documents(documents)
        
        print("4. Initializing Translator...")
        translator = PokotTranslator(rag_system=rag)
        
        print("SUCCESS: Pipeline initialized correctly.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
