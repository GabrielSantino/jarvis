# Importa os — acessa variáveis do sistema operacional
import os

# Importa sounddevice — captura áudio do microfone
import sounddevice as sd

# Importa write — salva o áudio capturado em arquivo WAV
from scipy.io.wavfile import write

# Importa numpy — operações matemáticas em arrays de áudio
import numpy as np

# Importa pyttsx3 — converte texto em fala (TTS) offline
import pyttsx3

# Importa Groq — conecta com a API do Groq
from groq import Groq

# Importa load_dotenv — carrega o .env
from dotenv import load_dotenv

# Importa Path — trabalha com caminhos de arquivos
from pathlib import Path

# Carrega o .env da raiz do projeto
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Cria o cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Histórico da conversa
historico = [
    {
        "role": "system",
        "content": "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto e inteligente. Responda de forma curta e objetiva pois sua resposta será lida em voz alta. Sempre chame o usuário de 'senhor Gabriel'."
    }
]

def transcrever_groq(caminho_audio):
    """Envia o áudio pro Groq e retorna o texto transcrito"""
    with open(caminho_audio, "rb") as f:
        resposta = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3",
            response_format="json"
        )
    return resposta.text

def falar(texto):
    """Converte texto em fala — TTS"""
    print(f"Jarvis: {texto}")
    try:
         # Reinicia o motor a cada fala — resolve o travamento no Windows
        motor = pyttsx3.init()
        motor.setProperty("rate", 150)
        motor.say(texto)
        motor.runAndWait()
        motor.stop()
    except Exception as e:
        print(f"Erro no TTS: {e}")

def ouvir():
    """Captura áudio do microfone com detecção de silêncio"""
    fs = 16000           # frequência de amostragem
    chunk = 1024         # pedaços de áudio analisados por vez
    silencio_limite = 0.05  # volume mínimo pra considerar voz
    silencio_max = 2     # segundos de silêncio pra parar de gravar

    print("🎤 Ouvindo... (fale agora)")

    gravando = []        # acumula os pedaços de áudio
    silencio = 0         # contador de silêncio
    falando = False      # flag — detectou voz?

    with sd.InputStream(samplerate=fs, channels=1, dtype='float32') as stream:
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

    # Junta os pedaços e salva o arquivo WAV
    audio = np.concatenate(gravando, axis=0)
    write("audio.wav", fs, audio)

    texto = transcrever_groq("audio.wav")
    texto = texto.strip()
    print(f"Você disse: {texto}")
    return texto if texto else None

def perguntar_jarvis(texto):
    """Envia o texto pro Groq e retorna a resposta"""
    historico.append({"role": "user", "content": texto})

    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=historico
    )

    mensagem = resposta.choices[0].message.content
    historico.append({"role": "assistant", "content": mensagem})
    return mensagem

# ── LOOP PRINCIPAL ─────────────────────────────────────
print("Jarvis online! Fale algo ou diga 'sair' para encerrar.\n")
falar("Olá senhor Gabriel, estou online e pronto para ajudá-lo.")

while True:
    entrada = ouvir()

    if entrada is None:
        falar("Não entendi, pode repetir?")
        continue

    if "sair" in entrada.lower():
        falar("Até logo, senhor Gabriel.")
        break

    resposta = perguntar_jarvis(entrada)
    falar(resposta)