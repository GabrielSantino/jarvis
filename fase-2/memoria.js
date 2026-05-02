import Groq from "groq-sdk"
import dotenv from "dotenv"
import { fileURLToPath } from "node:url"
import { dirname, join } from "node:path"
import readline from "readline"
import { readFileSync, writeFileSync, existsSync } from "fs"
import console from "node:console"

// Aponta pro .env na raiz do projeto
const __dirname = dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: join(__dirname, "..", ".env") })

const client = new Groq ({ apiKey: process.env.GROQ_API_KEY })

// Caminho do arquivo de memória
const ARQUIVO_MEMORIA = join(__dirname, "memoria.json")


// System prompt do Jarvis
const SYSTEM_PROMPT = "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto, inteligente e levemente formal como o Jarvis do Tony Stark. Sempre chame o usuário de 'senhor Gabriel'."

// Carrega o histórico do arquivo
function carregarMemoria() {
  if(existsSync(ARQUIVO_MEMORIA)) {
    const dados = readFileSync(ARQUIVO_MEMORIA, "utf-8")
    return JSON.parse(dados)
  }
  return [{ role: "system", content: SYSTEM_PROMPT }]
}

// Salva o histórico no arquivo 
function salvarMemoria(historico) {
  writeFileSync(ARQUIVO_MEMORIA, JSON.stringify(historico,null, 2), "utf-8")
}

const historico = carregarMemoria()

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

console.log("Jaris online. Digite 'sair' para encerrar.\n")

function conversar() {
    rl.question("Você: ", async (entrada) => {
      if(entrada.toLowerCase() === "sair") {
        console.log("Jarvis: Até logo, senhor Gabriel.")
        rl.close()
        return
      }

      historico.push({ role: "user", content: entrada})

      const resposta = await client.chat.completions.create({
        model:"llama-3.1-8b-instant",
        messages: historico
      })

      const mensagem = resposta.choices[0].message.content
      historico.push({ role: "assistant", content: mensagem })

      salvarMemoria(historico)

      console.log(`Jarvis: ${mensagem}\n`)
      conversar()
    })
}

conversar()