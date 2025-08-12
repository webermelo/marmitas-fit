#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Direto das Classes Firebase - Sem Streamlit
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar path
sys.path.append(os.getcwd())

def test_direct_firebase():
    """Teste direto das classes Firebase"""
    print("=" * 50)
    print("TESTE DIRETO FIREBASE (SEM STREAMLIT)")
    print("=" * 50)
    
    # Configurações
    PROJECT_ID = "marmita-fit-6a3ca"
    USER_ID = "kZugmFmioiQiz1EAh8iBPBzIvum2"
    
    # Passo 1: Testar FirestoreClient diretamente
    print("1. Testando FirestoreClient...")
    
    try:
        from utils.firestore_client import FirestoreClient
        
        client = FirestoreClient(PROJECT_ID)
        collection_path = f"users/{USER_ID}/ingredients"
        collection = client.collection(collection_path)
        
        print(f"Cliente criado: {client}")
        print(f"Colecao: {collection_path}")
        
        # Testar leitura
        docs = collection.get()
        print(f"Documentos encontrados: {len(docs) if docs else 0}")
        
        if docs:
            print("Primeiros 3 documentos:")
            for i, doc in enumerate(docs[:3]):
                nome = doc.get('nome', doc.get('Nome', 'N/A'))
                categoria = doc.get('categoria', doc.get('Categoria', 'N/A'))
                print(f"  {i+1}. {nome} - {categoria}")
        
        read_success = True
        
    except Exception as e:
        print(f"ERRO na leitura: {e}")
        read_success = False
    
    # Passo 2: Testar salvamento
    print(f"\n2. Testando salvamento...")
    
    try:
        # Dados de teste
        test_ingredient = {
            "nome": f"Teste Direto {datetime.now().strftime('%H%M%S')}",
            "categoria": "Teste",
            "preco": 10.0,
            "kcal_unid": 1.0,
            "fator_conv": 1000.0,
            "ativo": True,
            "test_marker": "DIRECT_TEST"
        }
        
        print(f"Salvando: {test_ingredient['nome']}")
        
        result = collection.add(test_ingredient)
        
        if result and 'name' in result:
            doc_id = result['name'].split('/')[-1]
            print(f"Salvo com ID: {doc_id}")
            save_success = True
        else:
            print("Falha no salvamento")
            save_success = False
            
    except Exception as e:
        print(f"ERRO no salvamento: {e}")
        save_success = False
    
    # Passo 3: Verificar se foi salvo
    if save_success:
        print(f"\n3. Verificando se foi salvo...")
        
        try:
            docs_after = collection.get()
            print(f"Documentos após salvamento: {len(docs_after) if docs_after else 0}")
            
            found = False
            for doc in docs_after:
                if doc.get('test_marker') == 'DIRECT_TEST':
                    print(f"Ingrediente teste encontrado: {doc.get('nome')}")
                    found = True
                    break
            
            if not found:
                print("Ingrediente teste NAO encontrado")
            
            verify_success = found
            
        except Exception as e:
            print(f"ERRO na verificacao: {e}")
            verify_success = False
    else:
        verify_success = False
    
    # Resultado
    print(f"\n" + "=" * 50)
    print(f"RESULTADO:")
    print(f"  Leitura: {'OK' if read_success else 'FALHA'}")
    print(f"  Salvamento: {'OK' if save_success else 'FALHA'}")
    print(f"  Verificacao: {'OK' if verify_success else 'FALHA'}")
    
    overall = read_success and save_success and verify_success
    print(f"\nFIREBASE DIRETO: {'FUNCIONANDO' if overall else 'COM PROBLEMAS'}")
    
    # Diagnostico se há problemas
    if not overall:
        print(f"\nDIAGNOSTICO:")
        if not read_success:
            print(f"  - Problema na leitura (token/auth)")
        if not save_success:
            print(f"  - Problema no salvamento")
        if not verify_success and save_success:
            print(f"  - Dados nao persistem")
    
    return overall

if __name__ == "__main__":
    test_direct_firebase()