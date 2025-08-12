#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Específico do Erro Real - Simula Exatamente o Streamlit
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Mock mais completo do Streamlit
class StreamlitMock:
    class SessionState:
        def __init__(self):
            self.user = {
                'uid': 'kZugmFmioiQiz1EAh8iBPBzIvum2',
                'email': 'test@test.com',
                'token': 'mock_token',
                'token_timestamp': datetime.now().isoformat()
            }
            self.demo_ingredients = []
        
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
    
    def success(self, msg): print(f"SUCCESS: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")
    def code(self, msg): print(f"CODE: {msg}")
    def subheader(self, msg): print(f"SUBHEADER: {msg}")
    def write(self, msg): print(f"WRITE: {msg}")

# Instalar mock
sys.modules['streamlit'] = StreamlitMock()
import streamlit as st
sys.path.append(os.getcwd())

def debug_real_upload():
    """Debug do erro real simulando o admin_safe"""
    print("=" * 60)
    print("DEBUG REAL ERROR - SIMULA admin_safe.py")
    print("=" * 60)
    
    # Carregar CSV exatamente como admin_safe faz
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print(f"1. CSV carregado: {len(df)} linhas")
    
    # Processar EXATAMENTE como admin_safe.py linha 582-632
    print(f"\n2. Processando primeira linha...")
    
    row = df.iloc[0]  # Primeira linha
    
    # Exatamente como admin_safe.py
    nome = str(row['Nome']).strip() if pd.notna(row['Nome']) else ''
    categoria = str(row['Categoria']).strip() if pd.notna(row['Categoria']) else ''
    
    try:
        preco = float(row['Preco']) if pd.notna(row['Preco']) else 0.0
    except:
        preco = 0.0
    
    try:
        kcal_unid = float(row['Kcal_Unid']) if pd.notna(row['Kcal_Unid']) else 0.0
    except:
        kcal_unid = 0.0
    
    try:
        fator_conv = float(row['Fator_Conv']) if pd.notna(row['Fator_Conv']) else 1.0
    except:
        fator_conv = 1.0
    
    # ESTRUTURA EXATA como admin_safe cria (linhas 611-632)
    ingredient_data_compatible = {
        # Estrutura ANTIGA que o app espera
        'Nome': nome,
        'Categoria': categoria,
        'Unidade_Receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
        'Unidade_Compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
        'Preco_Padrao': preco,
        'Kcal_Por_Unidade_Receita': kcal_unid,
        'Fator_Conversao': fator_conv,
        'Ativo': str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True,
        'Observacoes': str(row.get('Observacoes', '')),
        
        # Estrutura NOVA para Firebase (minúscula)
        'nome': nome,
        'categoria': categoria,
        'unid_receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
        'unid_compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
        'preco': preco,
        'kcal_unid': kcal_unid,
        'fator_conv': fator_conv,
        'ativo': str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True,
        'observacoes': str(row.get('Observacoes', '')),
        'user_id': 'test_user'
    }
    
    print(f"   Estrutura criada com {len(ingredient_data_compatible)} campos")
    
    # Debug detalhado dos campos booleanos
    boolean_fields = ['Ativo', 'ativo']
    print(f"\n3. Debug campos booleanos:")
    
    for field in boolean_fields:
        if field in ingredient_data_compatible:
            value = ingredient_data_compatible[field]
            print(f"   {field}: {value} (tipo: {type(value).__name__})")
            print(f"   isinstance(bool): {isinstance(value, bool)}")
            print(f"   isinstance(int): {isinstance(value, int)}")
    
    # Chamar save_ingredient_to_firebase_direct REAL
    print(f"\n4. Chamando save_ingredient_to_firebase_direct...")
    
    try:
        from pages.admin_safe import save_ingredient_to_firebase_direct
        
        print(f"   Função importada com sucesso")
        
        # CHAMAR A FUNÇÃO REAL
        result = save_ingredient_to_firebase_direct(ingredient_data_compatible)
        
        print(f"   Resultado: {result}")
        
    except Exception as e:
        print(f"   ERRO: {e}")
        
        # Capturar detalhes do erro
        error_str = str(e)
        if "TYPE_INT64" in error_str and "True" in error_str:
            print(f"\n   *** ERRO CONFIRMADO: Boolean sendo convertido para integerValue ***")
            print(f"   O erro menciona TYPE_INT64 e 'True'")
            
            # Analisar quais campos
            if "fields[7]" in error_str:
                print(f"   Campo 7 problemático (possivelmente 'ativo')")
            if "fields[16]" in error_str:
                print(f"   Campo 16 problemático (possivelmente 'Ativo')")
        
        import traceback
        print(f"\n   Traceback completo:")
        print(traceback.format_exc())
    
    print(f"\n" + "=" * 60)
    print(f"ANÁLISE:")
    print(f"- admin_safe.py cria estrutura com 2 campos boolean: 'Ativo' e 'ativo'")
    print(f"- Ambos são resultado de: str(row['Ativo']).upper() == 'TRUE'")  
    print(f"- Ambos são tipo <bool> correto")
    print(f"- FirestoreClient foi corrigido para bool antes de int")
    print(f"- MAS erro ainda acontece: campos 7 e 16 viram integerValue")
    
    print(f"\nHIPÓTESE:")
    print(f"- Pode haver cache ou import antigo sendo usado")
    print(f"- Pode haver múltiplas versões do código")
    print(f"- Pode haver problema na ordem dos campos no dicionário")

if __name__ == "__main__":
    debug_real_upload()