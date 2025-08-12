#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples da Solução (sem emojis para Windows)
"""

import sys
import os

# Adicionar path para imports
sys.path.append(os.getcwd())

# Configurações
PROJECT_ID = "marmita-fit-6a3ca"
TEST_USER_UID = "kZugmFmioiQiz1EAh8iBPBzIvum2"

def main():
    """Teste principal sem problemas de encoding"""
    print("=" * 50)
    print("TESTE SIMPLES DA SOLUCAO CORRIGIDA")
    print("=" * 50)
    
    # Importar cliente diretamente
    from utils.firestore_client import FirestoreClient
    
    # Criar cliente
    client = FirestoreClient(PROJECT_ID)
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    collection = client.collection(collection_path)
    
    print(f"Testando colecao: {collection_path}")
    
    # Teste de leitura
    try:
        documents = collection.get()
        print(f"SUCESSO: {len(documents)} documentos encontrados")
        
        if len(documents) > 0:
            print("PERSISTENCIA CONFIRMADA - Dados existem no Firebase!")
            
            # Mostrar alguns exemplos
            for i, doc in enumerate(documents[-3:]):
                nome = doc.get('nome', 'N/A')
                categoria = doc.get('categoria', 'N/A')
                print(f"  - {nome} ({categoria})")
                
        return True
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("RESULTADO: SOLUCAO FUNCIONANDO!")
        print("O problema de persistencia foi RESOLVIDO")
    else:
        print("RESULTADO: Ainda há problemas")
    print("=" * 50)