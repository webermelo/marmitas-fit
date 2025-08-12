#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug simples para testar operações Firestore
"""

import requests
import json
from datetime import datetime

# Configurações
API_KEY = "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
PROJECT_ID = "marmita-fit-6a3ca"
TEST_USER_UID = "kZugmFmioiQiz1EAh8iBPBzIvum2"

def test_firestore_access():
    """Testa acesso básico ao Firestore"""
    print("=" * 60)
    print("TESTE: ACESSO FIRESTORE SEM AUTENTICACAO")
    print("=" * 60)
    
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get('documents', [])
            print(f"Documentos encontrados: {len(docs)}")
            
            for i, doc in enumerate(docs[:2]):
                doc_id = doc['name'].split('/')[-1]
                print(f"  Doc {i+1}: {doc_id}")
                
        return response.status_code
        
    except Exception as e:
        print(f"ERRO: {e}")
        return None

def test_firestore_write_no_auth():
    """Testa escrita sem autenticação"""
    print("\n" + "=" * 60)
    print("TESTE: ESCRITA SEM AUTENTICACAO")
    print("=" * 60)
    
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    test_data = {
        "fields": {
            "nome": {"stringValue": "Teste Debug"},
            "categoria": {"stringValue": "Debug"},
            "timestamp": {"stringValue": datetime.now().isoformat()}
        }
    }
    
    try:
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        return response.status_code
        
    except Exception as e:
        print(f"ERRO: {e}")
        return None

def test_firebase_rules():
    """Verifica regras do Firebase"""
    print("\n" + "=" * 60)
    print("TESTE: VERIFICACAO REGRAS FIREBASE")
    print("=" * 60)
    
    read_status = test_firestore_access()
    write_status = test_firestore_write_no_auth()
    
    print(f"\nResultados:")
    print(f"Leitura sem auth: {read_status}")
    print(f"Escrita sem auth: {write_status}")
    
    if read_status == 403 or write_status == 403:
        print("REGRAS: Requerem autenticacao (normal)")
    elif read_status == 200 or write_status == 200:
        print("REGRAS: Permitem acesso publico (ATENCAO!)")
    else:
        print("REGRAS: Status desconhecido")

if __name__ == "__main__":
    test_firebase_rules()