from src.translator import PokotTranslator

def test_translation():
    print("Initializing PokotTranslator with Vertex AI...")
    try:
        # Initialize without RAG to valid ONLY the LLM part
        translator = PokotTranslator(rag_system=None)
        
        text = "Yomunto, kitɔrɔt Kɔkɔ Pɛlɛl"
        print(f"Translating: '{text}'")
        
        result = translator.translate(text, use_rag=False)
        
        print("\nTranslation Result:")
        print(result)
        
        if "translation" in result and not result["translation"].startswith("Error"):
             print("\nSUCCESS: Vertex AI translation worked.")
        else:
             print("\nFAILURE: Vertex AI translation returned error.")
             
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_translation()
