# Função que apresentat o Jarvis 
def apresentar(nome):
    if nome == "Jarvis":
        print("Olá! Eu sou o " + nome + ", seu assistente pessoal.")
    else:
        print("Olá, " + nome + "!")

#Repetição - cumprimenta 3 vezes
for i in range(3):
    print("Rodada " + str(i + 1))

# Chama a função
apresentar("Jarvis")
apresentar("Tony")