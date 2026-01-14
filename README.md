# Pokot-English Neural Translator

This project implements a neural translation system for the Pokot language, a low-resource Nilotic language. It uses a hybrid approach combining **Retrieval-Augmented Generation (RAG)** and Large Language Models (LLMs) to provide accurate translations even with limited training data.

## Features
- **Bible Scraping:** Automated collection of parallel Pokot-English verses from Bible.com.
- **RAG Architecture:** Uses Qdrant vector database and multilingual embeddings to retrieve relevant context for translation.
- **LLM Integration:** Leverages state-of-the-art LLMs for high-quality translation generation.
- **Streamlit UI:** A user-friendly interface for real-time translation and data management.

## Project Structure
```
pokot_translator/
├── app.py              # Streamlit web application
├── data/               # Directory for parallel corpus (CSV)
├── src/
│   ├── scraper.py      # Web scraping logic
│   ├── rag.py          # Vector indexing and retrieval
│   └── translator.py   # Translation logic (LLM + RAG)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Environment Setup

### 1. Prerequisites
- **Python 3.10+**: Ensure you have a modern Python environment.
- **API Access**: An OpenAI-compatible API key is required for the translation engine.

### 2. Installation
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Configuration
The system uses environment variables for API configuration. You can set them in your shell or a `.env` file:
```bash
export OPENAI_API_KEY='your_api_key'
# Optional: export OPENAI_BASE_URL='your_custom_base_url'
```

## Usage

### Running the Application
Launch the Streamlit interface with the following command:
```bash
streamlit run app.py
```

### Workflow
1. **Scrape Data:** Use the "Scrape Sample Data" button in the sidebar to build an initial parallel corpus.
2. **Index Data:** The system automatically indexes the scraped verses into an in-memory Qdrant collection.
3. **Translate:** Enter Pokot text in the input area. The system will:
   - Embed your input.
   - Retrieve the most similar Pokot-English pairs from the corpus.
   - Construct a prompt for the LLM including these examples.
   - Generate and display the English translation.

## Technical Components
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers) for cross-lingual mapping.
- **Vector Database:** Qdrant (In-memory mode for portability).
- **Translation Engine:** GPT-4.1-mini (or Claude Haiku equivalent) via OpenAI API.

## Ethical Considerations
This project is designed for language preservation and educational purposes. To ensuring respectful usage of data sources, the scraper implements the following mechanisms to avoid overloading servers:
- **Rate Limiting:** Randomized delays (1.5 - 3.5 seconds) are enforced between every request to mimic human behavior and reduce server load.
- **Sequential Processing:** Requests are made sequentially rather than in parallel to prevent traffic spikes.
- **User-Agent Headers:** Requests identify themselves as a standard browser to ensures compatibility and transparency.
- **Limited Scope:** The scraper is designed to fetch only necessary parallel texts for corpus creation, not to clone entire websites.
