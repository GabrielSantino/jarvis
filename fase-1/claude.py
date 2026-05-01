import os 
from groq import Groq
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

# Conecta ao Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Faz a pergunta
resposta = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Olá! Você é o Jarvis, meu assistente pessoal. Se apresente!"}
    ]
)

# Mostra a resposta
print(resposta.choices[0].message.content)