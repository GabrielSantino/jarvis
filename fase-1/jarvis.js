import Groq from "groq-sdk";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
// Aponta pro .env na raiz do projeto
const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, "../.env") });
// Conecta ao Groq
const client = new Groq({ apiKey: process.env.GROQ_API_KEY });
// Faz a pergunta
const resposta = await client.chat.completions.create({
    model: "llama-3.1-8b-instant",
    messages: [
        { role: "user", content: "Olá! Você é o Jarvis, meu assistente pessoal. Se apresente!" }
    ]
});
console.log(resposta.choices[0].message.content);
