#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simula o comportamento exato da aplicação Streamlit
"""

import sys
import os
sys.path.append(os.getcwd())

from utils.firestore_client import get_firestore_client
from datetime import datetime

# Simular session_state do Streamlit
class MockSessionState:
    def __init__(self):
        self.user = {
            'uid': 'kZugmFmioiQiz1EAh8iBPBzIvum2',
            'email': 'weber.melo@gmail.com',
            'token': 'mock_token_123'  # Token mock para teste
        }

# Mock do Streamlit para não dar erro
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
        self.secrets = {
            'firebase': {
                'projectId': 'marmita-fit-6a3ca'
            }
        }
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def success(self, msg):
        print(f"SUCCESS: {msg}")
    
    def cache_resource(self, func):
        return func

# Substituir o módulo streamlit
sys.modules['streamlit'] = MockStreamlit()
st = MockStreamlit()

def test_load_ingredients_simulation():
    """Simula a função load_ingredients_from_firebase() exatamente"""
    print("SIMULACAO: load_ingredients_from_firebase()")
    print("=" * 60)
    
    try:
        # Obter cliente Firestore (mesma lógica da app)
        db = get_firestore_client()
        if not db:
            print("ERROR: Cliente Firestore é None")
            return []
        
        # Verificar token (simular)
        token = st.session_state.user['token']
        db.set_auth_token(token)
        print(f"INFO: Token configurado: {token[:10]}...")
        
        # Carregar ingredientes do usuário (mesma lógica)
        user_id = st.session_state.user['uid']
        collection_path = f'users/{user_id}/ingredients'
        
        print(f"INFO: Tentando carregar de: {collection_path}")
        
        # CHAMADA CRÍTICA (mesmo código da app)
        raw_ingredients = db.collection(collection_path).get()
        
        print(f"INFO: Raw ingredients type: {type(raw_ingredients)}")
        print(f"INFO: Raw ingredients length: {len(raw_ingredients) if raw_ingredients else 'None'}")
        
        if raw_ingredients:
            print(f"SUCCESS: {len(raw_ingredients)} ingredientes encontrados!")
            for i, ingredient in enumerate(raw_ingredients[:3]):
                print(f"  Item {i+1}: {ingredient.get('nome', 'N/A')} - {ingredient.get('categoria', 'N/A')}")
            return raw_ingredients
        else:
            print(f"ERROR: NENHUM ingrediente encontrado na coleção: {collection_path}")
            return []
            
    except Exception as e:
        print(f"ERROR: ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_save_ingredient_simulation():
    """Simula save_ingredient_to_firebase_direct()"""
    print("\nSIMULACAO: save_ingredient_to_firebase_direct()")
    print("=" * 60)
    
    # Dados de teste (mesmo formato da app)
    ingredient = {
        'nome': 'Ingrediente Teste Simulacao',
        'categoria': 'Simulacao',
        'calorias': 100,
        'proteinas': 10,
        'carboidratos': 5,
        'gorduras': 2
    }
    
    try:
        # Obter cliente Firestore
        db = get_firestore_client()
        if not db:
            print("ERROR: Cliente Firestore não inicializado")
            return False
        
        # Verificar e configurar token
        token = st.session_state.user['token']
        db.set_auth_token(token)
        print(f"INFO: Token configurado: {token[:10]}...")
        
        # Preparar dados (mesma lógica)
        user_id = st.session_state.user['uid']
        collection_path = f'users/{user_id}/ingredients'
        
        # Dados completos para Firebase
        ingredient_data = ingredient.copy()
        ingredient_data['user_id'] = user_id
        ingredient_data['created_at'] = datetime.now().isoformat()
        
        print(f"INFO: Salvando em: {collection_path}")
        print(f"INFO: Item: {ingredient_data.get('nome', 'N/A')} - {ingredient_data.get('categoria', 'N/A')}")
        
        # Salvar no Firebase via REST API (mesma chamada)
        result = db.collection(collection_path).add(ingredient_data)
        
        print(f"INFO: Result type: {type(result)}")
        print(f"INFO: Result value: {result}")
        
        if result:
            print(f"SUCCESS: '{ingredient_data.get('nome', 'N/A')}' salvo com sucesso!")
            if 'name' in result:
                doc_id = result['name'].split('/')[-1]
                print(f"INFO: Document ID: {doc_id}")
            return True
        else:
            print("ERROR: Falha na resposta (resultado vazio)")
            return False
            
    except Exception as e:
        print(f"ERROR: EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa simulação completa"""
    print("SIMULACAO COMPLETA DO COMPORTAMENTO DA APP")
    print("=" * 80)
    
    # Teste 1: Carregar ingredientes (deve encontrar os que salvamos nos testes anteriores)
    ingredients_before = test_load_ingredients_simulation()
    
    # Teste 2: Salvar novo ingrediente
    save_success = test_save_ingredient_simulation()
    
    # Teste 3: Carregar novamente para verificar persistência
    if save_success:
        print("\n" + "="*60)
        print("VERIFICACAO: Carregando novamente após salvamento")
        print("=" * 60)
        ingredients_after = test_load_ingredients_simulation()
        
        # Comparar resultados
        print("\nRESULTADOS:")
        print(f"Antes do save: {len(ingredients_before)} ingredientes")
        print(f"Após o save: {len(ingredients_after)} ingredientes")
        
        if len(ingredients_after) > len(ingredients_before):
            print("SUCCESS: Ingrediente foi persistido com sucesso!")
        else:
            print("ERROR: Ingrediente NÃO foi persistido!")

if __name__ == "__main__":
    main()