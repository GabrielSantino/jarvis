import os 
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from ddgs import DDGS 

# Carrega o .env
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# FERRAMENTA - busca na web
def buscar_na_web(query: str) -> str:
    """Busca informações na web e retorna os resultados"""
    with DDGS() as ddgs:
        resultados = list(ddgs.text(query, max_results=3))
        if not resultados:
            return "Nenhum resultado encontrado."
        # Formata os resultados
        texto = " "
        for r in resultados:
            texto += f"Título: {r['title']}\n"
            texto += f"Resumo: {r['body']}\n\n"
        return texto
    
# - DEFINIÇÃO DAS FERRAMENTAS PRO GROQ
ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "buscar_na_web",
            "description": "Busca iniformações atuais na internet. Use quando precisar de dados em tempo real com clima, notícias, preços ou qualquer informação recente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "O que buscar na web"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# - CHAT COM FERRAMENTAS 
historico = [
    {
        "role": "system",
        "content": "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto e inteligente. Quando precisar de informações atuais, use a ferramenta de busca. Sempre chama o usuário de 'senhor Gabriel'."
    }
]

print("Jarvis online com busca na web. Digite 'sair' para encerrar .\n")

while True:
    entrada = input("Você: ")

    if entrada.lower() == "sair":
        print("Jarvis: Até logo, senhor Gabriel.")
        break

    historico.append({"role": "user", "content": entrada})

    # Primeira chamada - IA decide se usa ferramenta
    resposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=historico,
        tools=ferramentas,
        tool_choice="auto"
    )

    mensagem = resposta.choices[0].message

    #Verifica se a IA quer usar uma ferramenta
    if mensagem.tool_calls:
        print("🔍 Buscando na web...\n")

        # Adiciciona a decisão da IA ao histórico
        historico.append(mensagem)

        # Executa cada ferramenta solicitada
        for tool_call in mensagem.tool_calls:
            args = json.loads(tool_call.function.arguments)
            resultado = buscar_na_web(args["query"])

            # Adiciona o resultado ao históricoc
            historico.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado
            })

        # Segunda chamada - IA responde com base no resultado
        resposta_final = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico
        )


        resposta_texto = resposta_final.choices[0].message.content
        historico.append({ "role": "assistant", "content": resposta_texto})
        print(f"Jarvis: {resposta_texto}\n")

    else:
        # IA respondeu sem precisar de ferramenta
        historico.append({"role": "assistant", "content": mensagem.content})
        print(f"Jarvis: {mensagem.content}\n")