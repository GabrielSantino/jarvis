function apresentar(nome) {
     if (nome === "Jarvis") {
        console.log("Olá! Eu sou o " + nome + ", seu assistente pessoal.")
     } else {
        console.log("Olá, " + nome + "!")
     }
}

// Repetição - cumprimenta 3 vezes 
for (let i = 0; i < 3; i++) {
    console.log("Rodada " + (i + 1))
}

//Chama a função 
apresentar("Jarvis")
apresentar("Gabriel")