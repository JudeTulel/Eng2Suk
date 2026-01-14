import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import sys
import os

# Initialize Firestore
def initialize_firestore(project_id):
    if not firebase_admin._apps:
        # Use Application Default Credentials (ADC)
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': project_id,
        })
    return firestore.client()

def upload_csv_to_firestore(csv_path, project_id):
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return

    print(f"Initializing Firestore for project: {project_id}...")
    db = initialize_firestore(project_id)
    
    print(f"Reading CSV from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
        # Drop rows where critical fields are missing
        initial_count = len(df)
        df = df.dropna(subset=['pokot', 'english'])
        final_count = len(df)
        if initial_count != final_count:
            print(f"Dropped {initial_count - final_count} rows with missing text data.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    collection_name = 'pokot_verses'
    batch = db.batch()
    counter = 0
    total_uploaded = 0
    
    print(f"Starting upload to collection '{collection_name}'...")
    
    for index, row in df.iterrows():
        # Create a deterministic ID: BOOK_CHAPTER_VERSE (e.g., GEN_1_1)
        if 'book' in row and 'chapter' in row and 'verse' in row:
             doc_id = f"{row['book']}_{row['chapter']}_{row['verse']}"
        else:
             # Fallback to index if columns are missing
             doc_id = str(index)
        
        doc_ref = db.collection(collection_name).document(doc_id)
        
        # Prepare data, converting compatible types (handled by pandas mostly, but good to be safe)
        data = row.to_dict()
        
        batch.set(doc_ref, data)
        counter += 1
        
        # Firestore batches are limited to 500 ops
        if counter >= 400:
            batch.commit()
            print(f"Committed batch of {counter} records. Total so far: {total_uploaded + counter}")
            total_uploaded += counter
            batch = db.batch()
            counter = 0
            
    if counter > 0:
        batch.commit()
        total_uploaded += counter
        print(f"Committed final batch of {counter} records.")
        
    print(f"Upload Complete. Total documents: {total_uploaded}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/scraper_firestore.py <path_to_csv> <project_id>")
        sys.exit(1)
        
    csv_file_path = sys.argv[1]
    gcp_project_id = sys.argv[2]
    
    upload_csv_to_firestore(csv_file_path, gcp_project_id)
