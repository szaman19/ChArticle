# ChArticle

ChArticle is a AI-Agent assisted tool that summarizes chats to generate articles and summaries.

## Features
- Real time summarization of chat conversations when new messages are added.
- Summarizes chat conversations into well-structured articles.
- Generates concise summaries of chat content.
- Allows multiple users to collaborate on article creation.
- Can be easily hosted on firebase for private use.

## Not Features
- No protection against malicious prompts.
- Not designed for high traffic production use.
- Not optimized for large-scale deployments.
- Did not focus on security or UI/UX design.

## Intended Use
- As a template for building more interesting AI-powered applications.
- Maybe could double as a personal tool
- For learning and experimentation with AI agents and Firebase.


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ChArticle.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ChArticle
   ```

3. Install the required dependencies:
   ```bash
   npm install firebase-tools
   ```

4. Initialize a new Firebase project for Hosting and set up Firestore.
   [Firebase Documentation](https://firebase.google.com/docs/hosting)

5. Configure your Firebase credentials in the project.

6. Make sure `public/index.html` exists.
7. Deploy to Firebase:
   ```bash
   firebase deploy 
   ```

## Attaching an AI-Agent Service

The idea is that you can have your own backend AI-Agent server that handles the summarization and article generation when given access to the chat data in Firestore. As most agents use `Python`, you can interact with the Cloud Firestore using the `firebase-admin` library.

1. Set up a Python environment and install the `firebase-admin` library:
   ```bash
   pip install firebase-admin
   ```
2. Obtain service account credentials from your Firebase project settings and initialize the Firebase Admin SDK in your Python script:
   ```python
   import firebase_admin
   from firebase_admin import credentials, firestore

   # Initialize the Firebase app with service account credentials
   cred = credentials.Certificate('path/to/serviceAccountKey.json')
   firebase_admin.initialize_app(cred)

   # Get a reference to the Firestore database
   db = firestore.client()
   ```
3. Create a script that runs on your compute server to listen for changes in the Firestore database and processes the chat.
   1. The example I have in `backend/summarizer.py` listens for new messages in a specific Firestore collection and triggers the summarization process. It uses `Ollama` and `Langchain` to handle the LLM interactions.
