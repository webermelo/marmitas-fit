#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final de Persistência - Versão Simples
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Mock do Streamlit
class MockStreamlit:
    class SessionState:
        def __init__(self):
            self.user = {
                'uid': 'kZugmFmioiQiz1EAh8iBPBzIvum2',
                'email': 'test@test.com',
                'token': 'mock_token_123',
                'token_timestamp': datetime.now().isoformat()
            }
            self.demo_ingredients = []
            self.database_manager = None
        
        def get(self, key, default=None):
            return getattr(self, key, default)
        
        def __contains__(self, key):
            return hasattr(self, key)
    
    def __init__(self):
        self.session_state = self.SessionState()
        self.secrets = {
            "firebase": {
                "apiKey": "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90",
                "projectId": "marmita-fit-6a3ca"
            }
        }
    
    def success(self, msg): print(f"SUCESSO: {msg}")
    def error(self, msg): print(f"ERRO: {msg}")
    def warning(self, msg): print(f"AVISO: {msg}")
    def info(self, msg): print(f"INFO: {msg}")
    def code(self, msg): print(f"CODIGO: {msg}")

# Configurar mock
import streamlit
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Adicionar path
sys.path.append(os.getcwd())

def test_persistence():
    """Teste de persistência completo"""
    print("=" * 60)
    print("TESTE FINAL DE PERSISTENCIA")
    print("=" * 60)
    
    # Passo 1: Verificar CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    print(f"1. Verificando CSV: {os.path.basename(csv_path)}")
    
    if not os.path.exists(csv_path):
        print(f"ERRO: Arquivo nao encontrado - {csv_path}")
        return False
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"CSV OK: {len(df)} linhas carregadas")
        first_row = df.iloc[0]
        print(f"Exemplo: {first_row['Nome']} - {first_row['Categoria']}")
    except Exception as e:
        print(f"ERRO CSV: {e}")
        return False
    
    # Passo 2: Testar salvamento
    print(f"\n2. Testando salvamento...")
    
    try:
        from pages.admin_safe import save_ingredient_to_firebase_direct
        
        test_row = df.iloc[0]
        ingredient_data = {
            'nome': str(test_row['Nome']).strip(),
            'categoria': str(test_row['Categoria']).strip(),
            'unid_receita': str(test_row['Unid_Receita']).strip(),
            'unid_compra': str(test_row['Unid_Compra']).strip(),
            'preco': float(test_row['Preco']),
            'kcal_unid': float(test_row['Kcal_Unid']),
            'fator_conv': float(test_row['Fator_Conv']),
            'ativo': True,
            'observacoes': str(test_row.get('Observacoes', '')),
            'test_marker': 'PERSISTENCE_TEST_FINAL'
        }
        
        print(f"Salvando: {ingredient_data['nome']}")
        save_result = save_ingredient_to_firebase_direct(ingredient_data)
        print(f"Resultado salvamento: {'OK' if save_result else 'FALHA'}")
        
    except Exception as e:
        print(f"ERRO salvamento: {e}")
        save_result = False
    
    # Passo 3: Testar carregamento
    print(f"\n3. Testando carregamento...")
    
    try:
        from app import load_ingredients_from_firebase
        
        ingredients_list = load_ingredients_from_firebase()
        print(f"Ingredientes carregados: {len(ingredients_list)}")
        
        if ingredients_list:
            # Procurar ingrediente de teste
            found = False
            for ing in ingredients_list:
                if ing.get('test_marker') == 'PERSISTENCE_TEST_FINAL':
                    print(f"Ingrediente teste encontrado: {ing.get('Nome')}")
                    found = True
                    break
            
            if not found:
                print("Ingrediente teste nao encontrado")
                print(f"Primeiros 2 ingredientes:")
                for i, ing in enumerate(ingredients_list[:2]):
                    nome = ing.get('Nome', 'N/A')
                    print(f"  {i+1}. {nome}")
            
            load_result = True
        else:
            print("ERRO: Lista vazia")
            load_result = False
            
    except Exception as e:
        print(f"ERRO carregamento: {e}")
        load_result = False
    
    # Resultado
    print(f"\n" + "=" * 60)
    print(f"RESULTADO FINAL:")
    print(f"  Salvamento: {'OK' if save_result else 'FALHA'}")
    print(f"  Carregamento: {'OK' if load_result else 'FALHA'}")
    
    success = save_result and load_result
    print(f"\nPERSISTENCIA: {'FUNCIONANDO' if success else 'COM PROBLEMAS'}")
    
    return success

if __name__ == "__main__":
    test_persistence()