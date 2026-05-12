import os 
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from ddgs import DDGS 

# Carrega o .env
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Pasta onde as notas serão salvas.
PASTA_NOTAS = Path(__file__).parent / "notas"
PASTA_NOTAS.mkdir(exist_ok=True)

# FERRAMENTA 1 - busca na web
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
    
# -- FERRAMENTA 2 - criar nota
def criar_nota(nome: str, conteudo: str) -> str:
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Nota '{nome}' criada com sucesso."
    
# -- FERRAMENTA 3 - ler nota
def ler_nota(nome: str) -> str:
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    if not arquivo.exists():
        return f"Nota '{nome}' não encontrada."
    with open(arquivo, "r", encoding="utf-8") as f:
        return f.read()
        
# -- FERRAMENTAS 4 - listar notas
def listar_notas() -> str:
    notas = list (PASTA_NOTAS.glob("*.txt"))
    if not notas:
        return "Nenhuma nota encontrada."
    return "\n".join([n.stem for n in notas])
    
# -- FERRAMENTA 5 - deletar nota
def deletar_nota(nome:str) -> str:
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    if not arquivo.exists():
        return f"Nota '{nome}' não encontrada."
    arquivo.unlink()
    return f"nota '{nome}' deletada com sucesso. "
    
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
    },
    { 
        "type": "function",
        "function": {
            "name": "criar_nota",
            "description": "Cria uma nota ou anotação e salva num arquivo",
            "parameters":{
                "type": "object",
                "properties": {
                    "nome":{"type": "string", "description": "Nome da nota sem espaços"},
                    "conteudo": {"type": "string", "description": "Conteúdo da nota"}

                },
                "required": ["nome", "conteudo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ler_nota",
            "description": "Lê o conteúdo de uma nota salva.",
            "parameters": {
                "type":"object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome da nota a ler"}
                },
                "required": ["nome"]
                
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_notas",
            "description": "Lista todas as notas salvas.",
        "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deletar_nota",
            "description": "Deleta uma nota salva.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome da nota a deletar"}
                },
                "required": ["nome"]
            }
        }
    }
]

# - MAPA DE FUNÇÕES
mapa_ferramentas = {
    "buscar_na_web": buscar_na_web,
    "criar_nota": criar_nota,
    "ler_nota": ler_nota,
    "listar_notas": listar_notas,
    "deletar_nota": deletar_nota
}

# - CHAT COM FERRAMENTAS 
historico = [
    {
        "role": "system",
        "content": "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto e inteligente. Quando precisar de informações atuais, use a ferramenta de busca. Sempre chama o usuário de 'senhor Gabriel'."
    }
]

print("Jarvis online. Digite 'sair' para encerrar .\n")

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
        # Adiciciona a decisão da IA ao histórico
        historico.append(mensagem)

        # Executa cada ferramenta solicitada
        for tool_call in mensagem.tool_calls:
            nome_funcao = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"🔧 Usando ferramenta: {nome_funcao}")

            # Executa a ferramenta correta pelo mapa
            funcao = mapa_ferramentas[nome_funcao]
            resultado = funcao(**args)

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