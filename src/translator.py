'''
This module handles the translation logic, combining RAG with an LLM (Claude Haiku via OpenAI-compatible API).
'''
import vertexai
from vertexai.generative_models import GenerativeModel
from src.rag import PokotRAG

class PokotTranslator:
    '''Translates Pokot text to English using a RAG-enhanced LLM approach with Vertex AI.'''
    def __init__(self, rag_system=None, project_id="auth-4eef8", location="us-central1"):
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        # Use the newer, stable model version
        self.model = GenerativeModel("gemini-2.5-flash")
        self.rag = rag_system if rag_system else PokotRAG()
        
    def construct_prompt(self, pokot_text, context_verses):
        '''Constructs a prompt for the LLM with retrieved context.'''
        context_str = ""
        if context_verses:
            context_str = "Use the following similar biblical verses as context for vocabulary and style:\n\n"
            for i, verse in enumerate(context_verses):
                context_str += f"Example {i+1} (Reference: {verse['reference'] if 'reference' in verse else 'N/A'}):\nPokot: {verse.get('pokot', '')}\nEnglish: {verse.get('english', '')}\n\n"

        prompt = f"""You are an expert translator specializing in the Pokot language (a Nilotic language spoken in Kenya and Uganda).
Your task is to translate the following Pokot text into English.

{context_str}
Pokot text to translate:
"{pokot_text}"

Provide only the English translation. Do not include any explanations or additional text.
English Translation:"""
        return prompt

    def translate(self, pokot_text, use_rag=True):
        '''
        Translates Pokot text to English using Gemini Flash.
        '''
        context_verses = []
        if use_rag:
            try:
                context_verses = self.rag.retrieve_similar(pokot_text, top_k=3)
            except Exception as e:
                print(f"RAG retrieval error: {e}")

        prompt = self.construct_prompt(pokot_text, context_verses)

        try:
            response = self.model.generate_content(prompt)
            translation = response.text.strip()
            
            # Remove quotes if the model included them
            if translation.startswith('"') and translation.endswith('"'):
                translation = translation[1:-1]
                
            return {
                "translation": translation,
                "context": context_verses
            }
        except Exception as e:
            print(f"Translation error: {e}")
            return {
                "translation": f"Error occurred during translation: {str(e)}",
                "context": context_verses
            }

if __name__ == "__main__":
    # Example usage (requires API key and indexed RAG)
    # 1. Initialize RAG and index some dummy data
    rag = PokotRAG()
    # rag.index_data('data/parallel_corpus.csv')
    
    # 2. Initialize Translator
    translator = PokotTranslator(rag_system=rag)
    
    # 3. Translate
    # result = translator.translate("Yomunto, kitɔrɔt Kɔkɔ Pɛlɛl")
    # print(f"Translation: {result['translation']}")