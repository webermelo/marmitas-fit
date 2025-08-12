#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Direto - Bypass admin_safe para testar correção
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.getcwd())

def test_direct_fix():
    """Teste direto da correção boolean"""
    print("=" * 50)
    print("TESTE DIRETO - BYPASS admin_safe")
    print("=" * 50)
    
    # Mock mínimo
    class MockST:
        def error(self, msg): print(f"ERROR: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        
        class SessionState:
            def __init__(self):
                self.user = {
                    'uid': 'kZugmFmioiQiz1EAh8iBPBzIvum2',
                    'email': 'test@test.com',
                    'token': 'mock_token',
                    'token_timestamp': datetime.now().isoformat()
                }
            
            def __contains__(self, key):
                return key == 'user'
        
        def __init__(self):
            self.session_state = self.SessionState()
            self.secrets = {"firebase": {"projectId": "marmita-fit-6a3ca"}}
    
    # Instalar mock
    sys.modules['streamlit'] = MockST()
    import streamlit as st
    
    # Carregar dados CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    first_row = df.iloc[0]
    
    print(f"1. Dados CSV:")
    print(f"   Nome: {first_row['Nome']}")
    print(f"   Ativo: {first_row['Ativo']} (tipo: {type(first_row['Ativo'])})")
    
    # Processar como admin_safe faz
    ativo_converted = str(first_row['Ativo']).upper() == 'TRUE'
    
    # Criar estrutura MÍNIMA sem campos duplicados
    ingredient_data = {
        'nome': str(first_row['Nome']).strip(),
        'categoria': str(first_row['Categoria']).strip(),
        'preco': float(first_row['Preco']),
        'kcal_unid': float(first_row['Kcal_Unid']),
        'ativo': ativo_converted,  # Boolean que está causando problema
        'user_id': 'kZugmFmioiQiz1EAh8iBPBzIvum2',
        'created_at': datetime.now().isoformat()
    }
    
    print(f"\n2. Estrutura simplificada:")
    for key, value in ingredient_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    # Testar DIRETAMENTE com FirestoreClient (bypass admin_safe)
    print(f"\n3. Teste direto FirestoreClient:")
    
    try:
        from utils.firestore_client import FirestoreClient
        
        client = FirestoreClient("marmita-fit-6a3ca")
        collection = client.collection("users/kZugmFmioiQiz1EAh8iBPBzIvum2/ingredients")
        
        print(f"   Cliente criado: {client}")
        
        # Testar add diretamente
        result = collection.add(ingredient_data)
        
        if result and 'name' in result:
            doc_id = result['name'].split('/')[-1]
            print(f"   SUCESSO: Salvo com ID {doc_id}")
            
            # Verificar se foi salvo
            docs = collection.get()
            print(f"   Verificacao: {len(docs)} docs na colecao")
            
            # Procurar nosso documento
            found = False
            for doc in docs:
                if doc.get('user_id') == ingredient_data['user_id'] and doc.get('created_at') == ingredient_data['created_at']:
                    print(f"   Documento encontrado: {doc.get('nome')}")
                    found = True
                    break
            
            if not found:
                print(f"   Documento NAO encontrado na verificacao")
            
            return True
        else:
            print(f"   FALHA: Resultado invalido - {result}")
            return False
            
    except Exception as e:
        print(f"   ERRO: {e}")
        
        # Analisar se é o erro de boolean
        error_str = str(e)
        if "TYPE_INT64" in error_str and "True" in error_str:
            print(f"\n   *** ERRO BOOLEAN CONFIRMADO ***")
            print(f"   - Ainda há codigo convertendo boolean para integerValue")
            print(f"   - Nossa correcao no FirestoreClient nao foi aplicada completamente")
        
        return False

if __name__ == "__main__":
    success = test_direct_fix()
    print(f"\n" + "=" * 50)
    if success:
        print("RESULTADO: CORRECAO FUNCIONANDO")
    else:
        print("RESULTADO: PROBLEMA AINDA EXISTE")