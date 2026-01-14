'''
This module implements the Retrieval-Augmented Generation (RAG) component of the translator.
It uses Qdrant for vector storage and Sentence-Transformers for generating embeddings.
'''
import os
import pandas as pd
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class PokotRAG:
    '''Handles the retrieval of similar Pokot-English verse pairs.'''
    def __init__(self, collection_name="pokot_verses", model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        # Use an in-memory Qdrant client for simplicity. For production, you might use a Dockerized instance.
        self.client = QdrantClient(":memory:")
        self.collection_name = collection_name
        print(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.vector_size = self.model.get_sentence_embedding_dimension()

        # Initialize the collection in the vector database
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
        )
        print(f"Qdrant collection '{self.collection_name}' created.")

    def index_documents(self, documents):
        '''Indexes a list of verse dictionaries into the vector database.'''
        if not documents:
            print("No documents to index.")
            return

        print(f"Indexing {len(documents)} documents...")
        texts = [doc['pokot'] for doc in documents]
        
        print("Generating embeddings for Pokot verses...")
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)

        print("Indexing verses into Qdrant...")
        points = [
            models.PointStruct(
                id=idx,
                vector=embeddings[idx].tolist(),
                payload={
                    "pokot": doc['pokot'],
                    "english": doc['english'],
                    "reference": f"{doc.get('book', 'N/A')} {doc.get('chapter', 'N/A')}:{doc.get('verse', 'N/A')}"
                }
            )
            for idx, doc in enumerate(tqdm(documents, desc="Upserting points"))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )
        print(f"Successfully indexed {len(points)} verses into Qdrant.")

    def index_data(self, csv_path):
        '''Indexes the parallel corpus from a CSV file into the vector database.'''
        if not os.path.exists(csv_path):
            print(f"Error: Data file not found at {csv_path}. Please run the scraper first.")
            return

        print(f"Reading data from {csv_path}...")
        df = pd.read_csv(csv_path).dropna(subset=['pokot', 'english'])
        documents = df.to_dict('records')
        self.index_documents(documents)

    def retrieve_similar(self, query_text, top_k=3):
        '''Retrieves the top-k most similar verses for a given Pokot text.'''
        if not query_text:
            return []
            
        query_vector = self.model.encode(query_text).tolist()

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )

        results = [
            {
                "pokot": hit.payload["pokot"],
                "english": hit.payload["english"],
                "reference": hit.payload["reference"],
                "score": hit.score
            }
            for hit in search_result
        ]
        return results

if __name__ == "__main__":
    # This is an example of how to use the PokotRAG class.
    # 1. Create a dummy CSV for testing
    dummy_data = {
        'book': ['GEN', 'GEN'],
        'chapter': [1, 1],
        'verse': [1, 2],
        'pokot': ['Yomunto, kitɔrɔt Kɔkɔ Pɛlɛl kɔ ayɛng', 'Kɔ ayɛng kɔ mɔtin kɔ kumuy, kɔ rinyo kɔpa pɔ'],
        'english': ['In the beginning God created the heavens and the earth.', 'And the earth was without form, and void; and darkness was upon the face of the deep.']
    }
    dummy_df = pd.DataFrame(dummy_data)
    os.makedirs('data', exist_ok=True)
    dummy_csv_path = 'data/dummy_parallel_corpus.csv'
    dummy_df.to_csv(dummy_csv_path, index=False)

    # 2. Initialize RAG and index the data
    rag_system = PokotRAG()
    rag_system.index_data(dummy_csv_path)

    # 3. Perform a retrieval
    test_query = "Yomunto, kitɔrɔt Kɔkɔ"
    similar_verses = rag_system.retrieve_similar(test_query, top_k=1)

    print(f"\nQuery: \"{test_query}\"")
    print("Retrieved similar verses:")
    for verse in similar_verses:
        print(verse)
