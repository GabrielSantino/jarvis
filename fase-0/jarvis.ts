// Função que apresenta o Jarvis
// Note o ": string" - TypeScript exige saber o tipo do dado

function apresentarts(nome: string): void {
    if (nome === "Jarvis") {
        console.log("Olá! Eu sou o " + nome + ", seu assistente pessoal.")
    } else {
        console.log("Olá, " + nome + "!")
    }
}

// Repetição - cumprimenta 3 vezes
for (let i: number = 0; i < 3; i++) {
    console.log("Rodada" + (i + 1))
}

// chama a função 
apresentarts("Jarvis")
apresentarts("Gabriel")