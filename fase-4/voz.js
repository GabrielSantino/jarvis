// Importa Groq — SDK oficial para conectar com a API do Groq
import Groq from "groq-sdk"

// Importa dotenv — carrega as variáveis do .env
import dotenv from "dotenv"

// Importa fileURLToPath, dirname, join — reconstrói o __dirname no ES Module
import { fileURLToPath } from "url"
import { dirname, join } from "path"

// Importa fs — lê e escreve arquivos no sistema
import { createReadStream, createWriteStream } from "fs"

// Importa say — converte texto em fala (TTS)
import say from "say"

// Importa Microphone — captura áudio do microfone no Windows
import Microphone from "node-microphone"

// Reconstrói o __dirname
const __dirname = dirname(fileURLToPath(import.meta.url))

// Carrega o .env
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
function falar(texto) {
    return new Promise((resolve) => {
        console.log(`Jarvis: ${texto}`)
        say.speak(texto, null, 1.0, () => resolve())
    })
}

// ── FUNÇÃO STT ─────────────────────────────────────────
function ouvir() {
    return new Promise((resolve) => {
        const arquivoAudio = join(__dirname, "audio.wav")
        const mic = new Microphone()
        const stream = mic.startRecording()
        const writer = createWriteStream(arquivoAudio)

        console.log("🎤 Ouvindo... (aguarde 5 segundos)")

        // Escreve o áudio no arquivo
        stream.pipe(writer)

        // Para após 5 segundos
        setTimeout(async () => {
            mic.stopRecording()
            writer.end()

            // Aguarda o arquivo ser salvo
            writer.on("finish", async () => {
                try {
                    const audioStream = createReadStream(arquivoAudio)
                    const resposta = await client.audio.transcriptions.create({
                        file: audioStream,
                        model: "whisper-large-v3",
                        response_format: "json",
                        language: "pt"
                    })
                    const texto = resposta.text.trim()
                    console.log(`Você disse: ${texto}`)
                    resolve(texto || null)
                } catch (erro) {
                    console.log(`Erro na transcrição: ${erro.message}`)
                    resolve(null)
                }
            })
        }, 5000)
    })
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

main()