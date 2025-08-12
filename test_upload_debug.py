#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Específico para Debug do Upload de Ingredientes
Simula o processo completo sem Streamlit
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar path para imports
sys.path.append(os.getcwd())

# Configurações
PROJECT_ID = "marmita-fit-6a3ca"
TEST_USER_UID = "kZugmFmioiQiz1EAh8iBPBzIvum2"

def test_upload_flow():
    """Testa o fluxo completo de upload e leitura"""
    print("=" * 60)
    print("TESTE DE UPLOAD E LEITURA - FLUXO COMPLETO")
    print("=" * 60)
    
    # Passo 1: Ler o arquivo CSV
    csv_file = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    print(f"1. Lendo arquivo: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"   CSV carregado: {len(df)} linhas")
        print(f"   Colunas: {list(df.columns)}")
        print(f"   Primeira linha: {df.iloc[0].to_dict()}")
    except Exception as e:
        print(f"   ERRO ao ler CSV: {e}")
        return False
    
    # Passo 2: Simular processo de upload (salvar direto via FirestoreClient)
    print("\n2. Testando salvamento via FirestoreClient...")
    
    try:
        from utils.firestore_client import FirestoreClient
        
        client = FirestoreClient(PROJECT_ID)
        collection_path = f"users/{TEST_USER_UID}/ingredients"
        collection = client.collection(collection_path)
        
        # Pegar primeira linha para teste
        first_row = df.iloc[0]
        
        # Estrutura que o admin_safe.py cria
        test_ingredient = {
            "nome": str(first_row['Nome']).strip(),
            "categoria": str(first_row['Categoria']).strip(),
            "unid_receita": str(first_row['Unid_Receita']).strip(),
            "unid_compra": str(first_row['Unid_Compra']).strip(),
            "preco": float(first_row['Preco']),
            "kcal_unid": float(first_row['Kcal_Unid']),
            "fator_conv": float(first_row['Fator_Conv']),
            "ativo": True,
            "observacoes": str(first_row.get('Observacoes', '')),
            "user_id": TEST_USER_UID,
            "timestamp": datetime.now().isoformat(),
            "test_marker": "UPLOAD_DEBUG_TEST"
        }
        
        print(f"   Dados a salvar: {test_ingredient['nome']} - {test_ingredient['categoria']}")
        
        # Salvar
        result = collection.add(test_ingredient)
        print(f"   Resultado do salvamento: {result is not None}")
        
        if result and 'name' in result:
            doc_id = result['name'].split('/')[-1]
            print(f"   Document ID: {doc_id}")
            save_success = True
        else:
            print("   FALHA no salvamento")
            save_success = False
            
    except Exception as e:
        print(f"   ERRO no salvamento: {e}")
        save_success = False
    
    # Passo 3: Testar leitura via DatabaseManager
    print("\n3. Testando leitura via DatabaseManager...")
    
    try:
        from utils.database import DatabaseManager
        
        # Simular session state mínimo necessário
        class MockSessionState:
            def __init__(self):
                self.data = {}
                self.user = {
                    'uid': TEST_USER_UID,
                    'email': 'test@test.com'
                }
            
            def get(self, key, default=None):
                return self.data.get(key, default)
            
            def __contains__(self, key):
                return key in self.data or key == 'user'
        
        # Mock streamlit
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = MockSessionState()
        
        db_manager = DatabaseManager()
        ingredients_df = db_manager.get_user_ingredients(TEST_USER_UID)
        
        print(f"   DatabaseManager retornou: {len(ingredients_df) if not ingredients_df.empty else 0} ingredientes")
        
        if not ingredients_df.empty:
            # Procurar nosso ingrediente de teste
            test_found = False
            for _, ingredient in ingredients_df.iterrows():
                if ingredient.get('test_marker') == 'UPLOAD_DEBUG_TEST' or 'test' in str(ingredient.get('Nome', '')).lower():
                    print(f"   ✅ Ingrediente encontrado: {ingredient.get('Nome')} - {ingredient.get('Categoria')}")
                    test_found = True
                    break
            
            if not test_found:
                print("   ⚠️ Ingrediente de teste não encontrado na lista")
                print("   Primeiros 3 ingredientes encontrados:")
                for i, (_, ingredient) in enumerate(ingredients_df.head(3).iterrows()):
                    print(f"     {i+1}. {ingredient.get('Nome')} - {ingredient.get('Categoria')}")
            
            read_success = True
        else:
            print("   ❌ Nenhum ingrediente encontrado")
            read_success = False
            
    except Exception as e:
        print(f"   ERRO na leitura: {e}")
        read_success = False
    
    # Passo 4: Teste direto da conversão de estrutura
    print("\n4. Testando conversão de estruturas...")
    
    try:
        # Estrutura Firebase (como salva o admin)
        firebase_structure = {
            "nome": "Frango peito",
            "categoria": "Proteina Animal",
            "preco": 32.90,
            "kcal_unid": 1.65
        }
        
        # Testar conversão Firebase -> App
        converted = db_manager._convert_firebase_to_app_structure(firebase_structure)
        print(f"   Firebase -> App: {converted.get('Nome')} - OK: {converted.get('Nome') == 'Frango peito'}")
        
        # Estrutura App (como espera a interface)
        app_structure = {
            "Nome": "Frango peito",
            "Categoria": "Proteina Animal", 
            "Preco_Padrao": 32.90,
            "Kcal_Por_Unidade_Receita": 1.65
        }
        
        # Testar conversão App -> Firebase
        converted_back = db_manager._convert_app_to_firebase_structure(app_structure)
        print(f"   App -> Firebase: {converted_back.get('nome')} - OK: {converted_back.get('nome') == 'Frango peito'}")
        
        conversion_success = True
        
    except Exception as e:
        print(f"   ERRO na conversão: {e}")
        conversion_success = False
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print(f"  ✅ Salvamento: {'OK' if save_success else 'FALHA'}")
    print(f"  ✅ Leitura: {'OK' if read_success else 'FALHA'}")
    print(f"  ✅ Conversão: {'OK' if conversion_success else 'FALHA'}")
    
    overall_success = save_success and read_success and conversion_success
    print(f"\n🎯 PERSISTÊNCIA: {'FUNCIONANDO' if overall_success else 'COM PROBLEMAS'}")
    
    if not overall_success:
        print("\nDIAGNÓSTICO:")
        if not save_success:
            print("  - Problema no salvamento via FirestoreClient")
        if not read_success:
            print("  - Problema na leitura via DatabaseManager")
        if not conversion_success:
            print("  - Problema na conversão de estruturas")
    
    return overall_success

if __name__ == "__main__":
    test_upload_flow()