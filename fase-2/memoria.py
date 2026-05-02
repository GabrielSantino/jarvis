import os 
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path 

# Carrega o .env
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Caminho do arquivo de memória 
ARQUIVO_MEMORIA = Path(__file__).parent / "memoria.json"

# System prompt do Jarvis
SYSTEM_PROMPT = "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto, inteligente e levemente formal como o Jarvis do Tony Stark. Sempre chame o usuário de 'senhor Gabriel'."

def carregar_memoria():
    # Se o arquivo existir, carrega o histórico
    if ARQUIVO_MEMORIA.exists():
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    # Se não existir, começa com o systemm prompt
    return [{"role": "system", "content": SYSTEM_PROMPT}]
    

def salvar_memoria(historico):
    # Salva o histórico no arquivo json
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

# Carrega a memória ao iniciar
historico = carregar_memoria()

print("Jarvis online. Digite 'sair' para encerrar.\n")

while True:
    entrada = input("Você: ")

    if entrada.lower() == "sair":
        print("Jarvis: Até logo, senhor Gabriel.")
        break

    historico.append({"role": "user", "content": entrada})

    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=historico
    )

    mensagem = resposta.choices[0].message.content
    historico.append({"role": "assistant",  "content": mensagem})

    # Salva a memória após cada mensagem
    salvar_memoria(historico)

    print(f"Jarvis: {mensagem}\n")