import anthropic 

# Sua chave de acesso
client = anthropic.Anthropic(api_key="SUA-API-KEY-AQUI")

# Faz a pergunta pro Claude
resposta = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Olá! Você é o Jarvis, meu assistente pessoal. Se apresente!"}
    ]
)

# Mostra a resposta
print(resposta.content[0].text)