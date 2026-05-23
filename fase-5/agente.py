# Importa os - acessa variáveis do sistema operacional
import os

# Importa json - converte objetos Python em texto e vice-versa
import json

# Importa Groq - conecta com a API do Groq 
from groq import Groq

# Importa load_dotenv - carrega o .env
from dotenv import load_dotenv

# Importa Path - trabalha com caminhos de arquivos
from pathlib import Path

# Importa DDGS - busca na web Via DuckDuckGo
from ddgs import DDGS

# Carrega o .env da raiz do projeto
load_dotenv(dotenv_path= Path(__file__).parent.parent / ".env")

# Cria o cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Pasta onde as notas serão salvas
PASTA_NOTAS = Path(__file__).parent / "notas"
PASTA_NOTAS.mkdir(exist_ok=True)

# - FERRAMENTAS

def buscar_na_web(query: str) -> str:
    """Busca informações na web"""
    with DDGS() as ddgs:
        resultados = list(ddgs.text(query, max_results=3))
        if not resultados:
            return "Nenhum resultado encontrado."
        texto = ""
        for r in resultados:
            texto += f"Título: {r['title']}\n"
            texto += f"Resumo: {r['body']}\n\n"
        return texto
    
def criar_nota(nome: str, conteudo: str) -> str:
    """Cria uma nota e salva num arquivo"""
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Nota '{nome}' criada com sucesso."

def ler_nota(nome: str) -> str:
    """Lê o conteúdo de uma nota"""
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    if not arquivo.exists():
        return f"Nota '{nome}' não  encontrada."
    with open(arquivo, "r", encoding="utf-8") as f:
        return f.read()
    
def listar_notas() -> str:
        """Lista todas as notas salvas"""
        notas = list(PASTA_NOTAS.glob("*.txt"))
        if not notas:
            return "Nenhuma nota encontrada."
        return "\n". join([n.stem for n in notas])
    
def deletar_nota(nome: str) -> str:
        """Deleta uma nota"""
        arquivo = PASTA_NOTAS / f"{nome}.txt"
        if not arquivo.exists():
            return f"Nota '{nome}' não encontrada."
        arquivo.unlink()
        return f"Nota '{nome}' deletada com sucesso."
# - DEFINIÇÃO DAS FERRAMENTAS PRO GROQ
ferramentas = [
        {
            "type": "function",
            "function": {
                "name": "buscar_na_web",
                "description": "Busca informações atuais na internet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "O que buscar"}
                    },
                    "required":["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "criar_nota",
                "description": "Cria uma nota e salva num arquivo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome da nota"},
                        "conteudo": {"type": "string", "description": "Conteúdo da nota"}
                    },
                    "required":["nome", "conteudo"]
                }
            }
        },
        {
            "type": "function",
             "function": {
                "name": "ler_nota",
                "description": "Lê o conteúdo de uma nota salva.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome da nota"}
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
                    "nome": {"type": "string", "description": "Nome da nota"}
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

# - AGENTE  - loop de raciocínio
def executar_agente(objetivo: str) -> str:
    """..."""


    mensagens = [
        {
            "role": "system",
            "content": """Você é o Jarvis, um agente inteligente do Gabriel.
            Você tem acesso a ferramentas e deve usá-las para completar objetivos complexos.
            Planeje os passos necessários e execute um por um até completar o objetivo.
            Sempre chame o usuário de 'senhor Gabriel'."""
        },
        {
            "role": "user",
            "content":objetivo
        }
    ]


    print(f"\n🎯 Objetivo: {objetivo}")
    print("-" * 40)

    # Loop da agência - máximo 10 passos pra evitar loop infinito
    for passo in range(10):
        print(f"\n🤔 Passo {passo + 1} — raciocínando...")

        # IA decide o próximo passo
        resposta = client.chat.completions.create(
             model="llama-3.3-70b-versatile",
             messages=mensagens,
             tools=ferramentas,
             tool_choice="auto"
        )

        mensagem = resposta.choices[0].message

        # Se a IA não quer usar ferramentas - terminou!
        if not mensagem.tool_calls:
             print("\n✅ Objetivo concluído!")
             return mensagem.content
        # Adiciona a decisão da IA ao histórico
        mensagens.append(mensagem)

        # Executa cada ferramenta solicitada
        for tool_call in mensagem.tool_calls:
             nome_funcao = tool_call.function.name
             args = json.loads(tool_call.function.arguments)

             print(f"🔧 Executando: {nome_funcao}({args})")

             funcao = mapa_ferramentas[nome_funcao]
             if args:
                  resultado = funcao(**args)
             else:
                  resultado = funcao()


             print(f"📋 Resultado: {resultado[:100]}...")

             # Adiciona o resultado ao histórico
             mensagens.append({
                  "role": "tool",
                  "tool_call_id": tool_call.id,
                  "content": resultado
             })

    return  "Não consegui completar o objetivo do número máximo de passos."

# - LOOP PRINCIPAL
print("Jarvis Agente online. Digite 'sair' para encerrar.\n")

while True:
     objetivo = input("Você: ")

     if objetivo.lower() == "sair":
          print("Jarvis: Até logo, senhor Gabriel.")
          break
     
     resultado = executar_agente(objetivo)
     print(f"\nJarvis: {resultado}\n")