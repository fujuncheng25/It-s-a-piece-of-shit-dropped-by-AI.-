***hi,hi! it's empty and AI made, just for our fake college fair!. ***

Run the UVA RAG server (no extra config):

```bash
python3 rag_server.py
```

It serves on `http://127.0.0.1:9130` with:
- `GET /health`
- `POST /ask` with JSON body: `{"question":"Who founded UVA?"}`
