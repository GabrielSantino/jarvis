# Importa os - acessa variáveis do sistema operacional 
import os 

# Importa json - comverte objetos Python em texto e vice-versa
import json

# Importa asyncio - permite rodar tarefas em paralelo (wake word + servidor)
import asyncio

# Importa threading - roda a detecção de voz numa thread separada
import threading

# Importa FastAPI - Framework web para criar o servidor
from fastapi import FastAPI, WebSocket

# Importa CORSMiddleware - permite o React se comunicar com o servidor
from fastapi.middleware.cors import CORSMiddleware

# Importa Groq - conecta com a API do Groq
from groq import Groq

# Importa load_dotenv - carrega o .env
from dotenv import load_dotenv

# Importa Path - trabalha com caminhos de arquivos
from pathlib import Path

# Importa sounddevice - captura áudio do microfone
import sounddevice as sd

# Importa numpy - operações matemáticas em arrays de áudio
import numpy as np

# Importa scipy - salva o áudio em formato WAV
from scipy.io.wavfile import write

# Importa pyttsx3 - converte texto em fala (TTS)
import pyttsx3

# Importa spotipy - controla o Spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Importa DDGS - busca na web
from ddgs import DDGS

# Carrega o .env da raiz do projeto
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# - CLIENTES
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
))

# - MEMÓRIA 
ARQUIVO_MEMORIA = Path(__file__).parent / "memoria.json"
PASTA_NOTAS = Path(__file__).parent / "notas"
PASTA_NOTAS.mkdir(exist_ok=True)

SYSTEM_PROMPT = """Você é o Jarvis, assistente pessoal do Gabriel.
Seja direto, inteligente e levemente formal como o Jarvis do Tony Stark.
Sempre chame o usuário de 'sonhor Gabriel'.
Responda de forma curta e objetiva pois sua resposta será lida em voz alta.
Use as ferramentas disponíveis quando necessário."""

def carregar_memoria():
    if ARQUIVO_MEMORIA.exists():
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def salvar_memoria(historico):
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

historico = carregar_memoria()

# - FERRAMENTAS
def buscar_na_web(query:str) -> str:
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
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Nota '{nome}' criada com sucesso."

def ler_nota(nome: str) -> str:
    arquivos = PASTA_NOTAS / f"{nome}.txt"
    if not arquivo.exists():
        return f"Nota '{nome}' não encontrada."
    with open(arquivo, "r", encoding="utf-8") as f:
        return f.read()
    
def listar_notas() -> str:
    notas = list(PASTA_NOTAS.glob("*.txt"))
    if not notas:
        return "Nenhuma nota encontrada."
    return "\n".join([n.stem for n in notas])

def deletar_nota(nome: str) -> str:
    arquivo = PASTA_NOTAS / f"{nome}.txt"
    if not arquivo.exists():
        return f"Nota '{nome}' não encontrada."
    arquivo.unlink()
    return f"Nota '{nome}' deletada com sucesso."

def tocar_musica(nome: str) -> str:
    resultado = sp.search(q=nome, limit=1, type="track")
    tracks = resultado["tracks"]["items"]
    if not tracks:
        return f"Música '{nome}' não encontrada."
    track = track[0]
    sp.start_playback(uris=[track["uri"]])
    return f"Tocando: {track['name']} - {track['artists'][0]['name']}"

def pausar_musica() -> str:
    sp.pause_playback()
    return "Música pausada."

def proxima_musica() -> str:
    sp.next_track()
    return "Próxima música."

# - DEFINIÇÃO DAS FERRAMENTAS
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
                "required": ["query"]
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
                "required": ["nome", "conteudo"]
            }
        }
    },
     {
        "type": "function",
        "function": {
            "name": "ler_nota",
            "description": "Lê o conteúdo de uma nota.",
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
            "description": "Deleta uma nota.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome da nota"}
                },
                "required": ["nome"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "deletar_nota",
            "description": "Deleta uma nota.",
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
            "name": "tocar_musica",
            "description": "Toca uma música no Spotify.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome da música"}
                },
                "required": ["nome"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pausar_musica",
            "description": "Pausa a música no Spotify.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proxima_musica",
            "description": "Pula pra próxima música no Spotify.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

mapa_ferramentas = {
    "buscar_na_web": buscar_na_web,
    "criar_nota": criar_nota,
    "ler_nota": ler_nota,
    "listar_notas": listar_notas,
    "deletar_nota": deletar_nota,
    "tocar_musica": tocar_musica,
    "pausar_musica": pausar_musica,
    "proxima_musica": proxima_musica
}

# - TTS
def falar(texto: str):
    motor = pyttsx3.init()
    motor.setProperty("rate", 150)
    motor.say(texto)
    motor.runAndWait()
    motor.stop()

# - STT
def ouvir() -> str  | None:
    fs = 16000
    chunk = 1024
    silencio_limite = 0.05
    silencio_max = 2

    print("🎤 Ouvindo...")
    gravando = []
    silencio = 0
    falando = False

    with sd.InputStream(samplarate=fs, channels=1, dtype='float32') as stream:
        while True:
            pedaco, _ = stream.read(chunk)
            volume = np.abs(pedaco).mean()

            if volume > silencio_limite:
                falando = True
                silencio = 0
                gravando.append(pedaco)
            elif falando:
                silencio += chunk / fs
                gravando.append(pedaco)
                if silencio >= silencio_max:
                    break

    audio = np.concatenate(gravando, axis=0)
    write("audio.wav", fs, audio)

    with open("audio.wav", "rb") as f:
        resposta = client.audio.transcriptions.create(
            file=r,
            model="whisper-large-v3",
            response_format="json"
        )
    return resposta.text.strip() or None

# - AGENTE
def processar(entrada:str, ws_callback=None) -> str:
    historico.append({"role": "user", "content": entrada})

    mensagens = historico.copy()

    for passo in range(10):
        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens,
            tools=ferramentas,
            tool_choice="auto"
        )

        mensagem = resposta.choices[0].message

        if not mensagem.tool_calls:
            texto = mensagem.content
            historico.append({"role": "assistant", "content": texto})
            salvar_memoria(historico)
            return texto
        
        mensagens.append(mensagem)

        for tool_call in mensagem.tool_calls:
            nome = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if ws_callback:
                ws_callback(f"🔧 {nome}")
            
            funcao = mapa_ferramentas[nome]
            resultado = funcao(**args) if args else funcao()

            mensagens.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado
            })
    
    return "Não consegui completar a tarefa."

# - WAKE WORD
def detectar_wake_word(texto: str) -> bool:
    """Verifica se o texto contém a wake word"""
    wake_words = ["olá jarvis", "ola jarvis", "hey jarvis", "jarvis"]
    return any(w in texto.lower() for w in wake_words)

# - SERVIDOR FASTAPI
app = FastAPI()

# Permite o React se comunicar com o servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# WebSocket - canal de comunicação em tempo real com o React
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"tipo": "status", "dados": "conectado"})

    while True:
        dados = await websocke.receive_json()
        tipo = dados.get("tipo")

        if tipo == "texto":
            entrada = dados.get("entrada")
            await websocket.send_json({"tipo": "resposta", "dados": "pensando"})

            def callback(msg):
                asyncio.run(websocket.send_json({"tipo": "ferramenta", "dados": msg}))

            resposta = processar(entrada, callback)
            await websocket.send_json({"tipo": "resposta", "dados": resposta})

        elif tipo == "voz":
            await websocket.send_json({"tipo": "status", "dados": "ouvindo"})
            texto = await asyncio.to_thread(ouvir)

            if texto:
                await websocket.send_json({"tipo": "transcricao", "dados": texto})

                if detectar_wake_word(texto):
                    texto = texto.lower()
                    for w in ["olá jarvis", "ola jarvis", "hey jarvis", "jarvis"]:
                        texto = texto.replace(w, "").strip()
                
                await websocket.send_json({"tipo": "status", "dados": "pensando"})
                resposta = processar(texto)
                await websocket.send_json({"tipo": "resposta", "dados": resposta})

                threading.Thread(target=falar, args=(resposta,)).start()
            else:
                await websocket.send_json({"tipo": "status", "dados": "nao_entendi"})

# - ROTA DE STATUS
@app.get("/")
def status():
    return {"status": "Jarvis online"}

# - INICIA O SERVIDOR
if __name__ == "__main__":
    import uvicorn
    print("🚀 Jarvis iniciando...")
    uvicorn.run(app,host="0.0.0.0", port = 8000)