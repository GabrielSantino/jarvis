// Importa o Groq — SDK oficial para conectar com a API do Groq
import Groq from "groq-sdk"

// Importa o dotenv — lê o arquivo .env e carrega as variáveis de ambiente
import dotenv from "dotenv"

// Importa fileURLToPath — converte URL do arquivo para caminho de pasta
// dirname — pega o nome da pasta a partir de um caminho
// join — junta partes de um caminho de forma segura
import { fileURLToPath } from "url"
import { dirname, join } from "path"

// Importa readline — permite ler o que o usuário digita no terminal
import readline from "readline"


// Importa fs — File System, módulo nativo para trabalhar com arquivos
// readFileSync — lê um arquivo de forma síncrona (espera terminar)
// writeFileSync — escreve num arquivo de forma síncrona
// existsSync — verifica se um arquivo ou pasta existe
// mkdirSync — cria uma pasta
// readdirSync — lista arquivos dentro de uma pasta
// unlinkSync — deleta um arquivo
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, unlinkSync } from "fs"

// Importa json — para converter objetos em texto e vice-versa
import { createRequire } from "module"

// __dirname — caminho da pasta atual (fase-3)
// Em ES Modules o __dirname não existe por padrão — precisamos reconstruir
const __dirname = dirname(fileURLToPath(import.meta.url))
