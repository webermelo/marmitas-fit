#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do cliente Firestore customizado
"""

import sys
import os
sys.path.append(os.getcwd())

from utils.firestore_client import FirestoreClient
from datetime import datetime

def test_custom_client():
    """Testa o cliente customizado"""
    print("TESTE: CLIENTE FIRESTORE CUSTOMIZADO")
    print("=" * 60)
    
    # Criar cliente
    client = FirestoreClient("marmita-fit-6a3ca")
    
    # Testar sem token primeiro
    collection_path = "users/kZugmFmioiQiz1EAh8iBPBzIvum2/ingredients"
    collection = client.collection(collection_path)
    
    print(f"Testando colecao: {collection_path}")
    
    # Teste 1: Leitura
    print("\n1. TESTE LEITURA:")
    try:
        documents = collection.get()
        print(f"Documentos retornados: {len(documents)}")
        print(f"Tipo: {type(documents)}")
        
        if documents:
            print(f"Primeiro doc: {documents[0]}")
        
    except Exception as e:
        print(f"ERRO na leitura: {e}")
    
    # Teste 2: Escrita
    print("\n2. TESTE ESCRITA:")
    test_data = {
        "nome": "Teste Cliente Custom",
        "categoria": "Debug Custom",
        "timestamp": datetime.now().isoformat(),
        "user_id": "kZugmFmioiQiz1EAh8iBPBzIvum2"
    }
    
    try:
        result = collection.add(test_data)
        print(f"Resultado escrita: {result}")
        print(f"Tipo resultado: {type(result)}")
        
        if result and 'name' in result:
            doc_id = result['name'].split('/')[-1]
            print(f"Document ID: {doc_id}")
        
    except Exception as e:
        print(f"ERRO na escrita: {e}")
    
    # Teste 3: Leitura após escrita
    print("\n3. TESTE LEITURA APOS ESCRITA:")
    try:
        documents = collection.get()
        print(f"Documentos agora: {len(documents)}")
        
        if documents:
            for i, doc in enumerate(documents[-2:]):  # Ultimos 2
                print(f"Doc {i+1}: {doc.get('nome', 'N/A')} - {doc.get('categoria', 'N/A')}")
        
    except Exception as e:
        print(f"ERRO na leitura pos-escrita: {e}")

if __name__ == "__main__":
    test_custom_client()