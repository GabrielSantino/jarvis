# Importa os - acessa variáveis do sistema operacional
import os

# Importa spotipy - biblioteca oficial para a API do Spotify
import spotipy

# Importa SpotifyOAuth - gerencia a autentificação OAuth do Spotify
from spotipy.oauth2 import SpotifyOAuth

# Importa load_dotenv - carrega o .env
from dotenv import load_dotenv

# Importa Path - trabalha com caminhos de arquivos
from pathlib import Path

# Carrega o .env da raiz do projeto 
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Permissões que o Jarvis precisa no Spotify
# user - read-playback-state - ver o que está tocando
# user - modify-playback -state - play, pause, volume, próxima
# user - read- currently-playing - ver música atual
SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

 # Cria o cliente Spotify com autenticação OAutht
 # Na primeira vez abre o navegador pra você autorizar
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
     client_id=os.getenv("SPOTIFY_CLIENT_ID"),
     client_secret=os.getenv("SPOTIFY_CLIENT_ID"),
     redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
     scope=SCOPES
))

def tocar_musica(nome: str) -> str:
    """Buscar e toca uma música pelo nome"""
    # Busca a música no Spotify
    resultado = sp.search(q=nome, limit=1, type="track")
    tracks = resultado["tracks"]["items"]

    if not tracks:
        return f"Música '{nome}' não encontrada."
    
    # Pega a primeira música encontrada
    track = tracks[0]
    uri = tracks["uri"]
    artista = tracks["artists"][0]["name"]
    titulo = track["name"]

    # Toca a música 
    sp.start_playback(uris=[uri])
    return f"Tocando: {titulo} - {artista}"

def pausar () -> str:
    """Pausa a música atual"""
    sp.pause_playback()
    return "Música pausada."

def continuar() -> str:
    """Continua a música pausada"""
    sp.start_playback()
    return "Música continuada."

def proxima() -> str:
    """Pula pra próxima música pausada"""
    sp.start_playback()
    return "Música continuada."

def proxima() -> str:
    """Pula pra próxima música"""
    sp.next_track()
    return "Próxima música."