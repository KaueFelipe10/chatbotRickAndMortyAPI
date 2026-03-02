import requests
import random
import re
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END

SAUDACOES = [
    "Wubba Lubba Dub Dub! Sou o Bot-Rick. Qual o seu nome, viajante interdimensional?",
    "Ei, você! É... você mesmo. Diz aí seu nome antes que eu mude de dimensão.",
    "Olha só, mais um humano querendo saber segredos do multiverso. Como se chama?"
]

ERROS_NOME = [
    "Opa, esse nome tá mais perdido que o Jerry numa sala de conferências. Sem números ou desenhos, use letras!",
    "Nome estranho... Você é um parasita alienígena ou o quê? Tenta de novo só com letras.",
    "Esse nome não consta no Conselho de Ricks. Digite um nome humano real (só letras)!"
]

class CharacterState(TypedDict):
    user_name: str
    search_query: str
    results: List[dict]
    error: Optional[str]

def multi_search_api(state: CharacterState):
    base_url = "https://rickandmortyapi.com/api"
    query = state['search_query']
    found_results = []
    
    for category in ['character', 'episode']:
        param = "name" if not query.isdigit() else ""
        url = f"{base_url}/{category}/{query}" if not param else f"{base_url}/{category}/?{param}={query}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                items = data.get('results', [data]) if isinstance(data, dict) else [data]
                for item in items:
                    item['origin_type'] = category
                    found_results.append(item)
        except:
            continue

    if found_results:
        return {"results": found_results, "error": None}
    return {"error": f"Não achei nada sobre '{query}', {state['user_name']}. Até o Morty faria melhor.", "results": []}

def presenter(state: CharacterState):
    if state['error']:
        print(f"\n🛸 {state['error']}")
    else:
        print(f"\n✨ {state['user_name']}, olha o que eu desenterrei do multiverso:")
        for res in state['results'][:3]:
            tipo = "👤 PERSONAGEM" if res['origin_type'] == 'character' else "🎬 EPISÓDIO"
            print(f"--- {tipo} ---")
            print(f"Nome: {res.get('name')}")
            if res['origin_type'] == 'character':
                print(f"Status: {res.get('status')} | Espécie: {res.get('species')}")
            else:
                print(f"Lançamento: {res.get('air_date')} | Cod: {res.get('episode')}")
        print("="*30)

workflow = StateGraph(CharacterState)
workflow.add_node("search", multi_search_api)
workflow.add_node("display", presenter)
workflow.set_entry_point("search")
workflow.add_edge("search", "display")
workflow.add_edge("display", END)
app = workflow.compile()

def main():
    print("--- RICK & MORTY MULTIVERSE SEARCH ---")
    
    user_name = ""
    while True:
        print(f"\n🤖 {random.choice(SAUDACOES)}")
        entrada = input("> ").strip()
        
        if re.fullmatch(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", entrada) and len(entrada) >= 2:
            user_name = entrada.title()
            break
        else:
            print(f"\n❌ {random.choice(ERROS_NOME)}")

    print(f"\nBeleza, {user_name}! Eu sou especialista em tudo dessa série.")
    print("Mande um nome ou ID e eu vou vasculhar personagens e episódios ao mesmo tempo.")

    while True:
        query = input(f"\nO que quer buscar agora, {user_name}? (ou digite 'sair' para finalizarmos): ").strip()
        
        if query.lower() in ['sair', 'exit', 'quit']:
            print(f"Vou nessa. Não se esqueça: a existência é uma dor, {user_name}!")
            break
            
        if not query:
            continue

        app.invoke({
            "user_name": user_name,
            "search_query": query,
            "results": []
        })

if __name__ == "__main__":
    main()