import pandas as pd
from src.rag import PokotRAG
import numpy as np

def test_rag_with_nan():
    print("Testing RAG with NaN values...")
    
    # Simulate data with NaN values
    documents = [
        {'pokot': 'Valid text', 'english': 'Valid english', 'book': 'GEN', 'chapter': 1, 'verse': 1},
        {'pokot': float('nan'), 'english': 'Missing pokot', 'book': 'GEN', 'chapter': 1, 'verse': 2},
        {'pokot': 'Missing english', 'english': float('nan'), 'book': 'GEN', 'chapter': 1, 'verse': 3}
    ]
    
    rag = PokotRAG()
    
    try:
        rag.index_documents(documents)
        print("SUCCESS: RAG indexed documents (or handled errors gracefully).")
    except TypeError as e:
        print(f"CAUGHT EXPECTED ERROR: {e}")
    except Exception as e:
        print(f"CAUGHT UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_rag_with_nan()
