"use strict";
// Função que apresenta o Jarvis
// Note o ": string" - TypeScript exige saber o tipo do dado
function apresentarts(nome) {
    if (nome === "Jarvis") {
        console.log("Olá! Eu sou o " + nome + ", seu assistente pessoal.");
    }
    else {
        console.log("Olá, " + nome + "!");
    }
}
// Repetição - cumprimenta 3 vezes
for (let i = 0; i < 3; i++) {
    console.log("Rodada" + (i + 1));
}
// chama a função 
apresentarts("Jarvis");
apresentarts("Gabriel");
