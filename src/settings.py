INFERENCE_ENDPOINT = "http://10.10.78.11:8081"
INFERENCE_HEALTH_ENDPOINT = "http://10.10.78.11:8081/health"
# RETRIEVAL_ENDPOINT = "http://rag:6000/search" # Access RAG in Docker network
RETRIEVAL_ENDPOINT = "http://localhost:6000/search"
# ALIGNSCORE_ENDPOINT = "http://alignscore:5000/base_model" # Access AlignScore in Docker network
ALIGNSCORE_ENDPOINT = "http://localhost:5000/base_model"
FACTCHECKING = False
