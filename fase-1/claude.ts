import Anthropic from "@anthropic-ai/sdk"

// Sua chave de acesso
const client = new Anthropic({ apiKey: "SUA-API-KEY-AQUI" })

// Faz a pergunta pro Claude — note o tipo da resposta
const resposta: Anthropic.Message = await client.messages.create({
    model: "claude-opus-4-5",
    max_tokens: 1024,
    messages: [
        { role: "user", content: "Olá! Você é o Jarvis, meu assistente pessoal. Se apresente!" }
    ]
})

// Mostra a resposta
console.log(resposta.content[0].text)