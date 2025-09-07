# Example Backend

## Summarizer Service (summarizer.py)
A simple Python script that listens to a Firestore collection for new chat messages and generates a summary using an LLM. It uses the `firebase-admin` SDK to interact with Firestore and `Ollama` to obtain a `gpt-oss:30b` model for summarization.

Run with:
```bash
python summarizer.py <app_id> <session_name>
```
This will monitor the specified chat session in: 

`artifacts/<app_id>/public/data/chat_sessions/<session_name>/messages`
