import os 
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Carrega o .env
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Personalidade do Jarvis - system prompt
historico = [
    {
        "role" :"system",
         "content": "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto, inteligente e levemente formal como o Jarvis do Tony Stark. Sempre chame o usuário de 'senhor Gabriel'."""
    }
]

print("Jarvis online. Digite 'sair' para encerrar.\n")

# Loop infinito de conversa
while True:
    entrada = input("Você: ")

    if entrada.lower() == "sair":
        print("Jarvis: Até logo, senhor Gabriel.")
        break

    #Adiciona a mensagem do usuário ao históriico
    historico.append({ "role": "user", "content": entrada })

    # Envia o histórico inteiro pra IA
    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=historico
    )

    # Pega a resposta
    mensagem = resposta.choices[0].message.content

    # Adiciona a resposta ao histórico
    historico.append({ "role": "assistant", "content": mensagem})

    print(f"Jarvis: {mensagem}\n")