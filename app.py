from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

embeddings = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=os.getenv("HF_API"),
    repo_id="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "constitutionDB",
    embeddings,
    allow_dangerous_deserialization=True
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

conversation_history = {}

def is_valid_legal_query(query: str) -> bool:
    legal_keywords = [
        'law', 'legal', 'rights', 'constitution', 'court', 'case', 'crime',
        'punishment', 'article', 'section', 'offense', 'complaint', 'police',
        'lawyer', 'justice', 'sue', 'misuse', 'harassment', 'fraud', 'theft',
        'assault', 'defamation', 'privacy', 'violation', 'illegal', 'fir',
        'cyber', 'arrest', 'bail', 'evidence', 'witness', 'victim'
    ]
    
    query_lower = query.lower()
    
    has_legal_keyword = any(keyword in query_lower for keyword in legal_keywords)
    
    help_phrases = ['what can i do', 'what should i do', 'help me', 'how to', 
                    'what are my', 'can i', 'is it possible']
    has_help_phrase = any(phrase in query_lower for phrase in help_phrases)
    
    return has_legal_keyword or has_help_phrase

def retrieve_relevant_context(query: str, k: int = 3) -> str:
    try:
        docs = vectorstore.similarity_search(query, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""

def generate_response(query: str, session_id: str) -> str:
    
    if not is_valid_legal_query(query):
        return "This is not a valid legal case or query. Please ask about legal matters related to Indian law and Constitution."
    
    context = retrieve_relevant_context(query)
    
    history = conversation_history.get(session_id, [])
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-4:]])
    
    prompt = f"""You are a legal assistant specializing in Indian Constitutional law. Your role is to help users understand their legal rights and options based on the Indian Constitution and related laws.

Relevant Constitutional Context:
{context}

Previous Conversation:
{history_text}

User Query: {query}

Instructions:
1. Analyze the user's situation carefully
2. Identify applicable articles, sections, or laws from the Indian Constitution
3. Explain the legal rights and protections available
4. Suggest concrete legal actions the user can take (like filing FIR, approaching court, etc.)
5. Mention potential punishments for the offender if applicable
6. Be empathetic, clear, and professional
7. If information is limited, suggest consulting a lawyer
8. Always base your response on Indian law

Response:"""

    try:
        response = model.generate_content(prompt)
        answer = response.text
        
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        conversation_history[session_id].append({
            'role': 'user',
            'content': query
        })
        conversation_history[session_id].append({
            'role': 'assistant',
            'content': answer
        })
        
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]
        
        return answer
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I apologize, but I encountered an error processing your request. Please try rephrasing your question or try again later."

@app.route('/')
def home():
    return render_template("dashboard.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        response = generate_response(user_message, session_id)
        
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__": 
    app.run(debug=True)