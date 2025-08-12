#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste com autenticação real do Firebase
"""

import requests
import json
from datetime import datetime

# Configurações
API_KEY = "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
PROJECT_ID = "marmita-fit-6a3ca"
TEST_EMAIL = "weber.melo@gmail.com"

def get_valid_token():
    """
    IMPORTANTE: Este é apenas um teste para diagnóstico.
    Em produção, NUNCA coloque senhas em código!
    """
    print("TENTATIVA: Obter token válido")
    print("NOTA: Senha será solicitada via input para segurança")
    
    # Solicitar senha via input (mais seguro que hardcode)
    password = input("Digite a senha do Firebase (não será exibida): ")
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    
    payload = {
        "email": TEST_EMAIL,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            token = data["idToken"]
            uid = data["localId"]
            print(f"SUCCESS: Token obtido com sucesso!")
            print(f"UID: {uid}")
            print(f"Token (primeiros 20 chars): {token[:20]}...")
            return token, uid
        else:
            error_data = response.json()
            print(f"ERROR: {error_data}")
            return None, None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None, None

def test_with_real_token():
    """Testa com token real"""
    token, uid = get_valid_token()
    
    if not token:
        print("ERROR: Não foi possível obter token válido")
        return
    
    # Teste 1: Leitura com token válido
    print("\n" + "="*60)
    print("TESTE: LEITURA COM TOKEN VALIDO")
    print("="*60)
    
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    collection_path = f"users/{uid}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get('documents', [])
            print(f"Documentos encontrados: {len(docs)}")
            
            for i, doc in enumerate(docs[:3]):
                doc_id = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                nome = fields.get('nome', {}).get('stringValue', 'N/A')
                categoria = fields.get('categoria', {}).get('stringValue', 'N/A')
                print(f"  Doc {i+1}: {nome} - {categoria} (ID: {doc_id})")
                
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Teste 2: Escrita com token válido
    print("\n" + "="*60)
    print("TESTE: ESCRITA COM TOKEN VALIDO")
    print("="*60)
    
    test_data = {
        "fields": {
            "nome": {"stringValue": "Ingrediente Auth Real"},
            "categoria": {"stringValue": "Teste Auth"},
            "user_id": {"stringValue": uid},
            "timestamp": {"stringValue": datetime.now().isoformat()}
        }
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            doc_id = result['name'].split('/')[-1]
            print(f"SUCCESS: Documento criado! ID: {doc_id}")
            
            # Verificar se foi realmente salvo
            print("\nVERIFICACAO: Lendo novamente...")
            read_response = requests.get(url, headers=headers)
            if read_response.status_code == 200:
                read_data = read_response.json()
                docs_after = read_data.get('documents', [])
                print(f"Documentos agora: {len(docs_after)}")
                
                # Encontrar nosso documento
                for doc in docs_after:
                    if doc['name'].split('/')[-1] == doc_id:
                        fields = doc.get('fields', {})
                        nome = fields.get('nome', {}).get('stringValue', 'N/A')
                        print(f"Documento encontrado: {nome}")
                        break
                        
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_with_real_token()