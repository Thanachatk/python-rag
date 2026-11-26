import os 
from langchain_community.document_loaders  import TextLoader ,DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from data.vector_store import insert_chunks, client 
from dotenv import load_dotenv
import uuid
import ollama 

load_dotenv()

def load_file (docs_path) : 
    print ("Load file")
    if not os.path.exists(docs_path) : 
        raise FileNotFoundError(f"The {docs_path} cannot be loaded")
    loader = DirectoryLoader(
        path=docs_path ,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    if len(documents) == 0 :
        raise FileNotFoundError(f"No .txt files found in {docs_path}. Please add company document.")
    return documents
def split_document (documents, chunk_size = 1000 ,chunk_overlap =0) :
    print("Spliting documents into Chunk .... ")
    text_spliter = CharacterTextSplitter (
        chunk_size =chunk_size, 
        chunk_overlap = chunk_overlap, 
    )
    chunks = text_spliter.split_documents(documents)
    return chunks 
def main () :
    print("Main Function")
    documents = load_file(docs_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs"))
    for document in documents:
        document_id = str(uuid.uuid4())
        chunks = split_document([document])
        response = ollama.embed(
            model="nomic-embed-text:latest",
            input=[chunk.page_content for chunk in chunks],
        )
        insert_chunks(
            chunks=chunks,
            embeddings=response["embeddings"],
            document_id=document_id,
            filename=os.path.basename(document.metadata.get("source", "unknown")),
        )

if __name__ == "__main__" :
    try:
        main()
    finally:
        client.close()
