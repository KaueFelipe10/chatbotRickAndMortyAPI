import requests
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

class CharacterState(TypedDict):
    search_query: str
    category: str  # 'character', 'location' ou 'episode'
    results: Optional[dict]
    error: Optional[str]

def fetch_api_data(state: CharacterState):
    """Faz a chamada para a API baseada na categoria e query."""
    base_url = "https://rickandmortyapi.com/api"
    category = state['category']
    query = state['search_query']
    param = "name" if not query.isdigit() else ""
    url = f"{base_url}/{category}/{query}" if not param else f"{base_url}/{category}/?{param}={query}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            result = data['results'][0] if 'results' in data else data
            return {"results": result, "error": None}
        return {"error": "Nada encontrado! Tente outro nome ou ID.", "results": None}
    except Exception as e:
        return {"error": str(e)}

def presenter(state: CharacterState):
    """Formata a saída para o usuário."""
    if state['error']:
        print(f"\n❌ Erro: {state['error']}")
    else:
        res = state['results']
        print("\n" + "="*30)
        print(f"✨ RESULTADO ENCONTRADO:")
        print(f"Nome: {res.get('name')}")
        
        if state['category'] == 'character':
            print(f"Espécie: {res.get('species')}")
            print(f"Status: {res.get('status')}")
        elif state['category'] == 'episode':
            print(f"Lançamento: {res.get('air_date')}")
            print(f"Episódio: {res.get('episode')}")
            
        print("="*30 + "\n")


workflow = StateGraph(CharacterState)
workflow.add_node("call_api", fetch_api_data)
workflow.add_node("display", presenter)
workflow.set_entry_point("call_api")
workflow.add_edge("call_api", "display")
workflow.add_edge("display", END)

app = workflow.compile()

def main():
    print("Rick and Morty Bot")
    while True:
        print("O que deseja buscar?")
        print("1. Personagem | 2. Episódio | 3. Sair")
        choice = input("> ")
        
        if choice == '3': break
        
        cat_map = {'1': 'character', '2': 'episode'}
        category = cat_map.get(choice)
        
        if not category:
            print("Opção inválida!")
            continue
            
        query = input(f"Digite o nome ou ID do {category}: ")

        app.invoke({
            "search_query": query,
            "category": category
        })

if __name__ == "__main__":
    main()