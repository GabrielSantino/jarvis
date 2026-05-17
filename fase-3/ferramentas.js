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

// Carrega o .env da raiz do projeto 
// ".." sobe uma pasta - de fase-3 para jarvis
dotenv.config({ path: join(__dirname, "..", ".env") })

// Cria o cliente Groq - abre a conexão com a API
// process.env.GROQ_API_KEY - pega a chave do .env carregado acima
const client = new Groq({ apiKey: process.env.GROQ_API_KEY })

// PASTA_NOTAS - caminho da pasta onde as notas serão salvas
// __dirname = fase-3
// "notas" = pasta notas dentro de fase-3
const PASTA_NOTAS = join(__dirname, "notas")

//Cria a pasta notas se ela não existir
// recursive: true - cria pastas intermediárias se necessário
if (!existsSync(PASTA_NOTAS)) {
    mkdirSync(PASTA_NOTAS, { recursive: true })
}

// - FERRAMENTA 1 - buscar na web
// Recebe uma query (texto de busca) e retorna resultados da internet
// Usa a API do DuckDuckGo via fetchc nativo do Node.js
async function buscarNaWeb(query) {
    try {
        // Monta a URL da API do DuckDuckGo com a query codificada
        const url = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1`
        const res = await fetch(url)
        const data = await res.json()

        // AbstractText - resumo principal do resultado
        if (data.AbstractText) {
            return data.AbstractText
        }

        // RelatedTopics - tópicos relacionados se não tiver resumo principal
        if (data.RelatedTopics && data.RelatedTopics.length > 0) {
            return data.RelatedTopics
                .slice(0,3) // pega só o texto 
                .map(t => t.Text) // pega só o texto
                .filter(Boolean) // remove vazios
                .join("\n\n")
        }

        return "Nenhum resultado encontrado."
    } catch (erro) {
        return `Erro na busca: ${erro.message}`
    }
}

// - FERRAMENTA 2 - cria nota 
// nome - nome do arquivo sem espaços 
// conteudo - texto que será salvo dentro do arquivo
function criarNota(nome, conteudo) {
    // Monta o caminho completo: pasta_notas/nome.txt
    const arquivo = join(PASTA_NOTAS, `${nome}.txt`)
    // Escreve o conteúdo no arquivo com encoding UTF-8 (aceita acentos)
    writeFileSync(arquivo, conteudo, "utf-8")
    return `Nota '${nome}' criada com sucesso.`
}

// - FERRAMENTA 3 - ler nota
// Lê o conteudo de um arquivo .txt pelo nome 
function lerNota(nome) {
    const arquivo = join(PASTA_NOTAS, `${nome}.txt`)
    // Verifica se o arquivo existe antes de tentar ler
    if (!existsSync(arquivo)) {
        return `Nota '${nome}' não encontrada.`
    }
    // Lê e retorna o conteúdo do arquivo
    return readFileSync(arquivo, "utf-8")
    
}

// - FERRAMENTA 4 - listar notas
// Lista todos os arquivos .txt dentro da pasta de nota
function listarNotas() {
    // readdirSync - lê todos os arquivos da pasta
    const arquivos = readdirSync(PASTA_NOTAS)
    // Filtra só os .txt e remove a extensão  do nome
    const notas = arquivos.filter(f => f.endsWith(".txt")).map(f => f.replace(".txt", ""))
    if (notas.length === 0) return "Nenhuma nota encontrada."
    // Junta os nomes com quebra de linha
    return notas.join("\n")
}

// - FERRAMENTA 5 - deletar nota
// Deleta um arquivo .txt pelo nome
function deletarNota(nome) {
    const arquivo = join(PASTA_NOTAS, `${nome}.txt`)
    if (!existsSync(arquivo)) {
        return `Nota '${nome}' não encontrada.`
    }
    // unlinkSync - deleta o arquivo permanemtemente
    unlinkSync(arquivo)
    return `Nota '${nome}' deletada com sucesso.`
}
 
// - DEFINIÇÃO DAS FERRAMENTAS PRO GROQ
// Array de objetos que descreve cada ferramenta pra IA
// A IA usa essas descrições pra decidir qual ferramenta chamar
const ferramentas = [ 
    { 
        type: "function",
        function: {
            name: "buscarNaWeb",
            description: "Busca informações atuais na internet. Use para clima, notícias, preços e dados em tempo real.",
            parameters: {
                type: "object",
                properties: {
                    query: { type: "string", description: " O que buscar na web" }
                },
                required: ["query"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "criarNota",
            description: "Cria uma nota e salva num arquivo.",
            parameters: {
                type: "object",
                properties: {
                    nome: { type: "string", description: "Nome da nota sem espaços" },
                    conteudo: { type: "string", description: "Conteúdo da nota" }
                },
                required: ["nome", "conteudo"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "lerNota",
            description: "Lê o conteúdo de uma nota salva.",
            parameters: {
                type: "object",
                properties: {
                    nome: { type: "string", description: "Nome da nota a ler" }
                },
                required: ["nome"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "deletarNota",
            description: "Deleta uma nota salva.",
            parameters: {
                type: "object",
                properties: {
                    nome: { type: "string", description: "Nome da nota a deletar" }
                },
                required: ["nome"]
            }
        }
    }
]

// - MAPA DE FUNÇÕES 
// Conecta o nome da ferramenta (string) com a função real
// Quando a IA diz "chame buscarNaWeb" - buscamos aqui a função correspondente
const mapaFerramentas= {
    buscarNaWeb,
    criarNota,
    lerNota,
    listarNotas,
    deletarNota
}

// - INTERFACE DO TERMINAL  
// readline - cria uma interface de leitura do terminal
// process.stdin - entrada padrão (teclado)
// process.stdout - saída padrão (terminal)
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

console.log("Jarvis online. Digite 'sair' para encerrar. \n" )
// - HISTÓRICO DA CONVERSA
const historico = [
    {
        role: "system",
        content: "Você é o Jarvis, assistente pessoal do Gabriel. Seja direto e inteligente. Use as ferramentas disponíveis quando necessário. Sempre chame o usuário de 'senhor Gabriel'."
    }
]
// - LOOP DE CONVERSA
// Função recursiva - chama a si mesma pra manter o loop
async function conversar() {
    rl.question("Você: ", async (entrada) => {

        //.toLowerCase() - converte pra minúsculo antes de comparar
        if (entrada.toLocaleLowerCase() === "sair") {
            console.log("Jarvis: Até logo, senhor Gabriel.")
            rl.close()
            return
        }

        // Adiciona a mensagem do usuário ao histórico
        historico.push({ role:"user",  content: entrada })

        // Primeira chamada - IA decide se usa ferramenta ou responde direto
        // tool_choice: "auto" - IA decide sozinha quando usar ferramentas
        const resposta = await client.chat.completions.create({
            model: "llama-3.3-70b-versatile",
            messages: historico,
            tools: ferramentas,
            tool_choice: "auto"
        })

        const mensagem = resposta.choices[0].message

        // tool_calls - lista de ferramentas que a IA quer usar
        if (mensagem.tool_calls) {
            // Adiciona a decisão da IA ao histórico
            historico.push(mensagem)

            // Executa cada ferramenta solicitada
            for (const toolCall of mensagem.tool_calls) {
                // nome da ferramenta que a IA quer chamar
                const nomeFuncao = toolCall.function.name

                // arguments - parâmetros que a IA passou pra ferramenta
                // JSON.parse - converte o texto JSON em objeto JS
                const args = JSON.parse(toolCall.function.arguments)

                console.log(`🔧 Usando ferramenta: ${nomeFuncao}`)

                // Busca a função no mapa a executa com os argumenetos
                const funcao = mapaFerramentas[nomeFuncao]
                const resultado = await funcao(...Object.values(args))

                // Adiciona o resultado  da ferramenta ao histórico
                historico.push({
                    role: "tool",
                    tool_call_id: toolCall.id,
                    content: String(resultado)
                })
            }

            // Segunda chamada - IA responde com base no resultado da ferramenta
            const respostaFinal = await client.chat.completions.create({
                model:"llama-3.3-70b-versatile",
                messages: historico
            })

            const respostaTexto = respostaFinal.choices[0].message.content
            historico.push({ role: "assistant", content: respostaTexto })
            console.log(`Jarvis: ${respostaTexto}\n`)
        } else {
            // IA respondeu sem precisar de ferramenta
            historico.push({ role: "assistant", content: mensagem.content })
            console.log(`Jarvis: ${mensagem.content}\n`)
        }

        // Chama a si mesma - mantém o loop de conversa
        conversar()
    })
}

// Inicia o loop de conversa
conversar()