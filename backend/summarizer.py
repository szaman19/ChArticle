import firebase_admin
from firebase_admin import credentials, firestore
import time
import threading
import argparse
from ollama import Client

client = Client()

system_prompt = (
    "You are a helpful assistant that converts chat conversations into news articles. "
    "Given a chat transcript, you provide a concise summary of the key points discussed. "
    "Write as if you are writing a news article. Add additional information if possible to make it more complete. "
    "Use a journalistic tone and style. Don't just list the messages, but synthesize them into a coherent narrative. "
    "Produce the output in an html format with appropriate tags. This will be added to a <div> element, so don't add preambles like <html> or <body>. "
)


def generate_summary_with_local_llm(chat_transcript: str) -> str:
    """
    Use Ollama to generate a summary.
    
    Args:
        chat_transcript: A single string containing the entire chat history,
                         with each message on a new line (e.g., "Alex: Hello\nJane: Hi there").
    
    Returns:
        A string containing the generated summary.
    """
    print("\n--- Sending transcript to local LLM for summarization ---")
    print(chat_transcript)
    print("----------------------------------------------------------")

    
    response = client.chat(
        model="gpt-oss:20b",
        messages=[
            {
                "role": "user",
                "content": chat_transcript,
            },
            {
                "role": "system",
                "content": system_prompt,
            },
        ],
    )

    if response is None:
        print("No response from the model.")
        return "No response from the model."

    if response.message.content:
        summary = response.message.content
    else:
        summary = "No content in the response message."

    print(f"--- Received summary from LLM ---\n{summary}\n")
    return summary

# --- Firebase Interaction Logic ---

db = None
summary_doc_ref = None
callback_done = threading.Event()

def initialize_firebase(service_account_key_path: str):
    """Initializes the Firebase Admin SDK."""
    try:
        cred = credentials.Certificate(service_account_key_path)
        firebase_admin.initialize_app(cred)
        global db
        db = firestore.client()
        print("Firebase Admin SDK initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Please ensure your serviceAccountKey.json is in the correct path and is valid.")
        return False

def update_summary_in_firestore(summary_text: str):
    """Writes the generated summary to the designated Firestore document."""
    if summary_doc_ref:
        try:
            summary_doc_ref.set({'content': summary_text, 'lastUpdated': firestore.SERVER_TIMESTAMP}, merge=True)
            print(f"Successfully wrote summary to Firestore.")
        except Exception as e:
            print(f"Error writing summary to Firestore: {e}")

# This is the callback function that runs whenever 
# the messages collection changes.
def on_snapshot(col_snapshot, changes, read_time):
    print("New message detected! Re-generating summary...")
    
    # 1. Assemble the chat transcript
    messages = []
    for doc in col_snapshot:
        msg = doc.to_dict()
        # Ensure message has a timestamp and text content
        if msg.get('timestamp') and msg.get('text'):
            messages.append(msg)

    # Sort messages by timestamp to ensure correct order
    messages.sort(key=lambda x: x['timestamp'])
    
    # Format into a simple "User: Message" string
    transcript = "\n".join([f"{msg.get('username', 'Unknown')}: {msg.get('text', '')}" for msg in messages])

    transcript = (
        "This is the chat transcript:\n"
        + transcript
        + "\n\nPlease summarize the key points discussed."
    )
    if not transcript:
        print("No messages to summarize yet.")
        callback_done.set()
        return

    # 2. Call the local LLM to get the summary
    summary = generate_summary_with_local_llm(transcript)
    
    # 3. Write the summary back to Firestore
    update_summary_in_firestore(summary)
    
    callback_done.set()

def main(app_id: str, session_name: str):
    """Main function to start the listener."""
    if not initialize_firebase('serviceAccountKey.json'):
        return

    # Define the Firestore paths
    messages_collection_path = f"artifacts/{app_id}/public/data/chat_sessions/{session_name}/messages"
    summary_document_path = f"artifacts/{app_id}/public/data/chat_sessions/{session_name}/summary/content"

    assert db is not None, "Firestore client is not initialized."

    messages_col_ref = db.collection(messages_collection_path)
    global summary_doc_ref
    summary_doc_ref = db.document(summary_document_path)
    
    print(f"\n🚀 Starting Chat Summarizer Bot...")
    print(f"👂 Listening for new messages in session: {session_name}")
    print(f"✍️  Will write summaries to: {summary_document_path}")
    print("Press Ctrl+C to stop.")

    # Watch the collection for changes
    col_watch = messages_col_ref.on_snapshot(on_snapshot)

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping listener...")
        col_watch.unsubscribe()
        print("Listener stopped. Goodbye!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Real-time Firebase Chat Summarizer")
    parser.add_argument(
        "app_id", type=str, help="The application ID for the Firestore path."
        )
    parser.add_argument(
        "session_code", type=str, help="The chat session code to monitor."
        )
    args = parser.parse_args()
    
    main(args.app_id, args.session_code)