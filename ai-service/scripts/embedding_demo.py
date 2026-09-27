from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


model = SentenceTransformer(
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


texts = [
    "服务器无法建立TCP连接",
    "TCP连接建立失败",
    "今天天气非常不错"
]


embeddings = model.encode(
    texts,
    convert_to_tensor=True
)


similarity_ab = cos_sim(
    embeddings[0],
    embeddings[1]
)

similarity_ac = cos_sim(
    embeddings[0],
    embeddings[2]
)


print(
    "TCP vs TCP:",
    similarity_ab.item()
)

print(
    "TCP vs Weather:",
    similarity_ac.item()
)