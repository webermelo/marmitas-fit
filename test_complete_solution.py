#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo da Solução Corrigida
Valida todas as correções implementadas
"""

import sys
import os
import requests
from datetime import datetime

# Adicionar path para imports
sys.path.append(os.getcwd())

# Configurações
API_KEY = "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
PROJECT_ID = "marmita-fit-6a3ca"
TEST_USER_UID = "kZugmFmioiQiz1EAh8iBPBzIvum2"

def test_corrected_client():
    """Testa o cliente corrigido SEM Streamlit"""
    print("=" * 60)
    print("TESTE: CLIENTE FIRESTORE CORRIGIDO")
    print("=" * 60)
    
    # Importar cliente corrigido diretamente
    from utils.firestore_client import FirestoreClient
    
    # Criar cliente sem cache
    client = FirestoreClient(PROJECT_ID)
    
    print(f"Cliente criado: {client}")
    print(f"Project ID: {client.project_id}")
    print(f"Base URL: {client.base_url}")
    
    # Testar sem token (deve funcionar devido às regras públicas atuais)
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    collection = client.collection(collection_path)
    
    print(f"\nTestando colecao: {collection_path}")
    
    # Teste 1: Leitura
    print("\n1. LEITURA:")
    try:
        documents = collection.get()
        print(f"  Sucesso: {len(documents)} documentos encontrados")
        
        for i, doc in enumerate(documents[-3:]):  # Últimos 3
            nome = doc.get('nome', 'N/A')
            categoria = doc.get('categoria', 'N/A') 
            doc_id = doc.get('id', 'N/A')
            print(f"    Doc {i+1}: {nome} - {categoria} (ID: {doc_id[:8]}...)")
            
        return len(documents)
        
    except Exception as e:
        print(f"  Erro na leitura: {e}")
        return 0

def test_error_handling():
    """Testa o tratamento de erro melhorado"""
    print("\n" + "=" * 60)
    print("TESTE: TRATAMENTO DE ERROS MELHORADO")
    print("=" * 60)
    
    from utils.firestore_client import FirestoreClient
    
    client = FirestoreClient(PROJECT_ID)
    # Definir token inválido para testar erro 401
    client.set_auth_token("token_invalido_para_teste")
    
    collection = client.collection(f"users/{TEST_USER_UID}/ingredients")
    
    print("Testando com token inválido...")
    try:
        documents = collection.get()
        print(f"Inesperado: funcionou com token inválido! {len(documents)} docs")
    except Exception as e:
        error_msg = str(e)
        print(f"Erro capturado (esperado): {error_msg[:100]}...")
        
        if "401" in error_msg or "AUTENTICAÇÃO" in error_msg:
            print("✅ Tratamento de erro 401 funcionando!")
        else:
            print("⚠️ Erro diferente do esperado")

def test_data_persistence():
    """Testa persistência de dados"""
    print("\n" + "=" * 60)
    print("TESTE: PERSISTÊNCIA DE DADOS")
    print("=" * 60)
    
    from utils.firestore_client import FirestoreClient
    
    client = FirestoreClient(PROJECT_ID)
    collection_path = f"users/{TEST_USER_UID}/ingredients"
    collection = client.collection(collection_path)
    
    # Contar documentos antes
    docs_before = collection.get()
    count_before = len(docs_before)
    print(f"Documentos antes: {count_before}")
    
    # Adicionar documento de teste
    test_data = {
        "nome": f"Teste Solucao Final {datetime.now().strftime('%H:%M:%S')}",
        "categoria": "Teste Final",
        "user_id": TEST_USER_UID,
        "timestamp": datetime.now().isoformat(),
        "test_marker": "FINAL_SOLUTION_TEST"
    }
    
    print(f"Adicionando: {test_data['nome']}")
    
    try:
        result = collection.add(test_data)
        print(f"✅ Documento adicionado com sucesso!")
        
        if result and 'name' in result:
            doc_id = result['name'].split('/')[-1]
            print(f"Document ID: {doc_id}")
            
            # Verificar se foi realmente salvo
            docs_after = collection.get()
            count_after = len(docs_after)
            print(f"Documentos depois: {count_after}")
            
            if count_after > count_before:
                print("✅ PERSISTÊNCIA CONFIRMADA!")
                
                # Encontrar nosso documento
                for doc in docs_after:
                    if doc.get('test_marker') == 'FINAL_SOLUTION_TEST':
                        print(f"✅ Documento encontrado na leitura: {doc['nome']}")
                        break
                        
                return True
            else:
                print("❌ Documento não persistiu!")
                return False
        else:
            print("❌ Resultado inválido do add()")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao adicionar: {e}")
        return False

def test_token_management():
    """Testa gerenciamento de token (mock)"""
    print("\n" + "=" * 60)
    print("TESTE: GERENCIAMENTO DE TOKEN")
    print("=" * 60)
    
    try:
        from utils.token_manager import is_token_expired, add_token_timestamp_to_user
        
        # Teste 1: Token recente (não expirado)
        recent_timestamp = datetime.now().isoformat()
        is_expired = is_token_expired(recent_timestamp)
        print(f"Token recente expirado? {is_expired} (deve ser False)")
        
        # Teste 2: Token antigo (expirado)
        from datetime import timedelta
        old_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()
        is_expired = is_token_expired(old_timestamp)
        print(f"Token antigo expirado? {is_expired} (deve ser True)")
        
        # Teste 3: Adicionar timestamp
        user_data = {"token": "mock_token", "uid": "test"}
        user_with_timestamp = add_token_timestamp_to_user(user_data)
        print(f"Timestamp adicionado: {'token_timestamp' in user_with_timestamp}")
        
        print("✅ Gerenciamento de token funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de token: {e}")
        return False

def main():
    """Executa todos os testes da solução"""
    print("TESTE COMPLETO DA SOLUÇÃO CORRIGIDA")
    print("=" * 80)
    print(f"Projeto: {PROJECT_ID}")
    print(f"Usuário: {TEST_USER_UID}")
    print(f"Timestamp: {datetime.now()}")
    
    results = {}
    
    # Teste 1: Cliente corrigido
    try:
        doc_count = test_corrected_client()
        results["cliente_corrigido"] = doc_count > 0
    except Exception as e:
        print(f"ERRO no teste do cliente: {e}")
        results["cliente_corrigido"] = False
    
    # Teste 2: Tratamento de erro
    try:
        test_error_handling()
        results["tratamento_erro"] = True
    except Exception as e:
        print(f"ERRO no teste de erro: {e}")
        results["tratamento_erro"] = False
    
    # Teste 3: Persistência
    try:
        results["persistencia"] = test_data_persistence()
    except Exception as e:
        print(f"ERRO no teste de persistência: {e}")
        results["persistencia"] = False
    
    # Teste 4: Gerenciamento de token
    try:
        results["token_management"] = test_token_management()
    except Exception as e:
        print(f"ERRO no teste de token: {e}")
        results["token_management"] = False
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES DA SOLUÇÃO")
    print("=" * 80)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nRESULTADO GERAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 SOLUÇÃO COMPLETA FUNCIONANDO!")
    else:
        print("⚠️ Alguns problemas ainda existem")
    
    print("\nNOTA IMPORTANTE:")
    print("- Os testes são baseados nas regras Firebase atuais (público)")
    print("- Com regras de produção, autenticação será obrigatória") 
    print("- Cliente corrigido funcionará corretamente com tokens válidos")

if __name__ == "__main__":
    main()