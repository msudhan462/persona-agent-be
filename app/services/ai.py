from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
import torch
from pinecone import Pinecone
from pathlib import Path


model_name = "BAAI/bge-large-en-v1.5"
models_dir = Path(__file__).parent.parent.absolute().joinpath(".cache")
print(models_dir)

tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=models_dir)
model = AutoModel.from_pretrained(model_name, cache_dir=models_dir)
print("embedding model max length",tokenizer.model_max_length)



def get_embeddings(text):
    
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    sentence_embedding = outputs.last_hidden_state.mean(dim=1)

    return sentence_embedding

def chunk_text(text, chunk_size = 1000, combine_chunk=100, type="heirarchal"):
    si = 0
    ei = chunk_size
    total_length = len(text)

    total_chunks =  []
    chunk_count = 0
    while ei < total_length:
        if si == 0:
            chunk = text[si : ei]
        else:
            chunk = text[si-combine_chunk : ei]
        
        si = ei
        ei += chunk_size
        chunk_count += 1
        total_chunks.append(chunk)
    
    return total_chunks


# with open("sachin_tendulkar.txt") as f:
#     t = f.read()
#     chunks = chunk_text(t)
#     for chunk_count, ch in enumerate(chunks, start=1):
#         emds = get_embeddings(ch)[0]
#         id = uuid4()
#         data = {
#             "id":str(id),
#             "values":emds,
#             "metadata":{"text":ch}
#         }
#         vector_db.insert(data)
#         print(chunk_count)

#     print("Done")
