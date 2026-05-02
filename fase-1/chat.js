import Groq from "groq-sdk"
import dotenv from "dotenv"
import { fileURLToPath } from "url"
import { dirname, join } from "path"
import readline from "readline"

// Aponta pro .env na raiz do projeto
const __dirname = dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: join(__dirname, "../.env")})

// Cria o client Groq
const client = new Groq({ apiKey: process.env.GROQ_API_KEY })

// Personalidade do Jarvis
const historico = [
    { 
        role: "system",
        content: "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto, inteligente e levemente formal como o Jarvis do Tony Stark. Sempre chame o usuário de 'senhor Gabriel'."
    }
]

// Interfacec de leitura do terminal
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

console.log("Jarvis online. Digite 'sair' para encerrar.\n")

// Função recursiva de conversa 
function conversar() {
    rl.question("Você: ", async (entrada) => {
        if (entrada.toLowerCase() === "sair") {
            console.log(" Jarvis: Até logo, senhor Gabriel.")
            rl.close()
            return
        }

        historico.push({ role: "user", content: entrada})

        const resposta = await client.chat.completions.create({
            model: "llama-3.1-8b-instant",
            messages: historico
        })

        const mensagem = resposta.choices[0].message.content
        historico.push({ role: "assistant", content: mensagem })

        console.log(`Jarvis: ${mensagem}\n`)
        conversar()
    })
}

conversar()