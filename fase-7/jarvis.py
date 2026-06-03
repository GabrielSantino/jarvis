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
    arquivos = 