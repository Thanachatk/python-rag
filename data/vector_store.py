from qdrant_client import QdrantClient, models
import uuid
from pathlib import Path
# Initialize local database
client = QdrantClient(path=str(Path(__file__).resolve().parent / "qdrant"))

# Create collection
COLLECTION_NAME = "chunks"

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=768,
            distance=models.Distance.COSINE
        )
    )

print("Qdrant Local Database Ready!")


def insert_chunks(chunks, embeddings, document_id, filename):

    if len(chunks) != len(embeddings):
        raise ValueError("The number of chunks and embeddings must match")

    points = []

    for i, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": i,
                    "text": chunk.page_content
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"Inserted {len(points)} chunks")
