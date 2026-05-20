// Importa Groq — SDK oficial para conectar com a API do Groq
import Groq from "groq-sdk"

// Importa dotenv — carrega as variáveis do .env
import dotenv from "dotenv"

// Importa fileURLToPath, dirname, join — reconstrói o __dirname no ES Module
import { fileURLToPath } from "url"
import { dirname, join } from "path"

// Importa fs — lê e escreve arquivos no sistema
import { writeFileSync, createReadStream } from "fs"

// Importa readline — lê input do terminal
import readline from "readline"

// Importa say — converte texto em fala (TTS) usando a voz do sistema
import say from "say"

// Importa child_process — executa comandos do sistema operacional
// execSync — executa um comando e espera terminar
import { execSync } from "child_process"

// Reconstrói o __dirname — necessário em ES Modules
const __dirname = dirname(fileURLToPath(import.meta.url))

// Carrega o .env da raiz do projeto
dotenv.config({ path: join(__dirname, "..", ".env") })

// Cria o cliente Groq
const client = new Groq({ apiKey: process.env.GROQ_API_KEY })

// Histórico da conversa
const historico = [
    {
        role: "system",
        content: "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto e inteligente. Responda de forma curta e objetiva pois sua resposta será lida em voz alta. Sempre chame o usuário de 'senhor Gabriel'."
    }
]

// ── FUNÇÃO TTS ─────────────────────────────────────────
// say.speak() — usa a voz nativa do sistema operacional
// Retorna uma Promise — aguarda terminar de falar
function falar(texto) {
    return new Promise((resolve) => {
        console.log(`Jarvis: ${texto}`)
        // say.speak(texto, voz, velocidade, callback)
        // null = voz padrão do sistema
        // 1.0 = velocidade normal
        say.speak(texto, null, 1.0, () => resolve())
    })
}

// ── FUNÇÃO STT ─────────────────────────────────────────
// Grava áudio pelo microfone usando sox (gravador de linha de comando)
// Envia pro Groq Whisper e retorna o texto transcrito
async function ouvir() {
    const arquivoAudio = join(__dirname, "audio.wav")

    console.log("🎤 Ouvindo... (fale agora, pressione Ctrl+C pra parar)")

    try {
        // sox — programa de linha de comando para gravar áudio
        // rec = grava do microfone
        // -r 16000 = frequência 16000Hz
        // -c 1 = mono (1 canal)
        // silence = para quando detectar silêncio
        // 1 0.1 3% = espera 0.1s com volume abaixo de 3% pra começar
        // 1 2.0 3% = para após 2s de silêncio abaixo de 3%
        execSync(
            `sox -d -r 16000 -c 1 ${arquivoAudio} silence 1 0.1 3% 1 2.0 3%`,
            { stdio: "inherit" }
        )
    } catch {
        return null
    }

    // Envia o áudio pro Groq Whisper
    const stream = createReadStream(arquivoAudio)
    const resposta = await client.audio.transcriptions.create({
        file: stream,
        model: "whisper-large-v3",
        response_format: "json",
        language: "pt"
    })

    const texto = resposta.text.trim()
    console.log(`Você disse: ${texto}`)
    return texto || null
}

// ── FUNÇÃO JARVIS ──────────────────────────────────────
async function perguntarJarvis(texto) {
    historico.push({ role: "user", content: texto })

    const resposta = await client.chat.completions.create({
        model: "llama-3.1-8b-instant",
        messages: historico
    })

    const mensagem = resposta.choices[0].message.content
    historico.push({ role: "assistant", content: mensagem })
    return mensagem
}

// ── LOOP PRINCIPAL ─────────────────────────────────────
async function main() {
    console.log("Jarvis online! Fale algo ou diga 'sair' para encerrar.\n")
    await falar("Olá senhor Gabriel, estou online e pronto para ajudá-lo.")

    while (true) {
        const entrada = await ouvir()

        if (!entrada) {
            await falar("Não entendi, pode repetir?")
            continue
        }

        if (entrada.toLowerCase().includes("sair")) {
            await falar("Até logo, senhor Gabriel.")
            break
        }

        const resposta = await perguntarJarvis(entrada)
        await falar(resposta)
    }
}

main