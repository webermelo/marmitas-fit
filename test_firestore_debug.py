#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para testar operações Firestore
Identifica onde está o problema na persistência de dados
"""

import requests
import json
from datetime import datetime

# Configurações do Firebase (copiadas do secrets.toml)
API_KEY = "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
PROJECT_ID = "marmita-fit-6a3ca"
AUTH_DOMAIN = "marmita-fit-6a3ca.firebaseapp.com"

# Dados de teste do usuário conhecido
TEST_USER_EMAIL = "weber.melo@gmail.com"
TEST_USER_UID = "kZugmFmioiQiz1EAh8iBPBzIvum2"

def test_authentication():
    """Testa autenticação básica do Firebase"""
    print("=" * 60)
    print("TESTE 1: AUTENTICAÇÃO FIREBASE")
    print("=" * 60)
    
    # Simular login (sem senha real por segurança)
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}"
    
    # Primeiro vamos verificar se conseguimos acessar a API
    try:
        response = requests.get(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}")
        print(f"OK API Firebase acessivel: {response.status_code}")
        
        if response.status_code == 400:  # Esperado sem dados
            error_data = response.json()
            print(f"Resposta API: {error_data}")
            
    except Exception as e:
        print(f"ERRO ao acessar API Firebase: {e}")
        return None
    
    return "mock_token_for_testing"

def test_firestore_permissions(token):
    """Testa permissões do Firestore"""
    print("\n" + "=" * 60)
    print("TESTE 2: PERMISSÕES FIRESTORE")
    print("=" * 60)
    
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Teste 1: Tentar listar documentos na coleção do usuário
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    print(f"🔍 Testando acesso à coleção: {collection_path}")
    print(f"🌐 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Conteúdo: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Documentos encontrados: {len(data.get('documents', []))}")
            return True
        elif response.status_code == 404:
            print("⚠️  Coleção não existe (isso é normal se nunca foi criada)")
            return True
        elif response.status_code == 401:
            print("❌ Erro de autenticação - token inválido")
            return False
        elif response.status_code == 403:
            print("❌ Erro de permissão - usuário não tem acesso")
            return False
        else:
            print(f"❌ Erro desconhecido: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção ao testar Firestore: {e}")
        return False

def test_firestore_write(token):
    """Testa escrita no Firestore"""
    print("\n" + "=" * 60)
    print("TESTE 3: ESCRITA NO FIRESTORE")
    print("=" * 60)
    
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Dados de teste
    test_ingredient = {
        "fields": {
            "nome": {"stringValue": "Teste Debug Ingrediente"},
            "categoria": {"stringValue": "Teste"},
            "user_id": {"stringValue": TEST_USER_UID},
            "created_at": {"stringValue": datetime.now().isoformat()},
            "test_timestamp": {"integerValue": str(int(datetime.now().timestamp()))}
        }
    }
    
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    print(f"🔍 Testando escrita na coleção: {collection_path}")
    print(f"🌐 URL: {url}")
    print(f"📋 Dados: {json.dumps(test_ingredient, indent=2)}")
    
    try:
        response = requests.post(url, json=test_ingredient, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Documento criado com sucesso!")
            print(f"📄 Document ID: {result.get('name', 'N/A').split('/')[-1]}")
            return result
        else:
            print(f"❌ Falha na escrita: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exceção ao escrever no Firestore: {e}")
        return None

def test_firestore_read_after_write(token):
    """Testa leitura após escrita"""
    print("\n" + "=" * 60)
    print("TESTE 4: LEITURA APÓS ESCRITA")
    print("=" * 60)
    
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"📄 Documentos encontrados: {len(documents)}")
            
            for i, doc in enumerate(documents[:3]):  # Mostrar apenas primeiros 3
                doc_id = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                nome = fields.get('nome', {}).get('stringValue', 'N/A')
                created_at = fields.get('created_at', {}).get('stringValue', 'N/A')
                
                print(f"  📋 Doc {i+1}: ID={doc_id}, Nome={nome}, Created={created_at}")
                
            return len(documents) > 0
        else:
            print(f"❌ Falha na leitura: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção ao ler do Firestore: {e}")
        return False

def test_firebase_rules():
    """Testa as regras de segurança do Firebase"""
    print("\n" + "=" * 60)
    print("TESTE 5: REGRAS DE SEGURANÇA")
    print("=" * 60)
    
    # Tentar acessar sem autenticação
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    headers = {'Content-Type': 'application/json'}  # Sem Authorization
    
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    url = f"{base_url}/{collection_path}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Acesso sem auth - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Regras funcionando: acesso negado sem autenticação")
        elif response.status_code == 403:
            print("✅ Regras funcionando: acesso proibido sem autenticação")
        elif response.status_code == 200:
            print("⚠️  ATENÇÃO: Dados acessíveis sem autenticação!")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exceção ao testar regras: {e}")

def main():
    """Executa todos os testes"""
    print("FIREBASE/FIRESTORE DEBUG TOOL")
    print("Projeto:", PROJECT_ID)
    print("Usuario:", TEST_USER_EMAIL)
    print("UID:", TEST_USER_UID)
    
    # Teste 1: Autenticação
    token = test_authentication()
    if not token:
        print("❌ FALHA CRÍTICA: Não foi possível obter token")
        return
    
    # Teste 2: Permissões
    has_permissions = test_firestore_permissions(token)
    
    # Teste 3: Escrita
    write_result = test_firestore_write(token)
    
    # Teste 4: Leitura após escrita
    read_success = test_firestore_read_after_write(token)
    
    # Teste 5: Regras de segurança
    test_firebase_rules()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"🔐 Autenticação: {'✅ OK' if token else '❌ FALHA'}")
    print(f"🔑 Permissões: {'✅ OK' if has_permissions else '❌ FALHA'}")
    print(f"✏️  Escrita: {'✅ OK' if write_result else '❌ FALHA'}")
    print(f"📖 Leitura: {'✅ OK' if read_success else '❌ FALHA'}")
    
    if write_result and not read_success:
        print("\n🚨 PROBLEMA IDENTIFICADO:")
        print("   - Escrita parece funcionar")
        print("   - Mas leitura não encontra dados")
        print("   - Possível problema de cache ou timing")

if __name__ == "__main__":
    main()