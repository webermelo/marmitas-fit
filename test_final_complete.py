#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final Completo - Simula EXATAMENTE a aplicação Streamlit
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Mock Streamlit completo
class MockST:
    class SessionState:
        def __init__(self):
            self.user = {
                'uid': 'kZugmFmioiQiz1EAh8iBPBzIvum2',
                'email': 'test@test.com', 
                'token': 'mock_valid_token_123',
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

# Instalar mock ANTES de qualquer import
sys.modules['streamlit'] = MockST()
import streamlit as st

sys.path.append(os.getcwd())

def test_complete_real_scenario():
    """Teste que simula EXATAMENTE o cenário real"""
    print("=" * 70)
    print("TESTE FINAL COMPLETO - CENARIO REAL")
    print("=" * 70)
    
    # 1. Carregar CSV exatamente como aplicação
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"1. CSV carregado: {len(df)} ingredientes")
    except Exception as e:
        print(f"1. ERRO ao carregar CSV: {e}")
        return False
    
    # 2. Processar PRIMEIRA linha exatamente como admin_safe.py
    row = df.iloc[0]
    
    print(f"\n2. Processando primeira linha:")
    print(f"   Nome: {row['Nome']}")
    print(f"   Ativo original: {row['Ativo']} (tipo: {type(row['Ativo'])})")
    
    # Processamento EXATO do admin_safe.py (linhas 582-632)
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
    
    # CONVERSÃO EXATA do admin_safe.py
    ativo_converted = str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True
    
    print(f"   Ativo convertido: {ativo_converted} (tipo: {type(ativo_converted)})")
    
    # 3. Criar estrutura EXATA como admin_safe.py (linhas 611-632)
    ingredient_data = {
        # Estrutura ANTIGA (maiúscula)
        'Nome': nome,
        'Categoria': categoria,
        'Unidade_Receita': str(row['Unid_Receita']).strip(),
        'Unidade_Compra': str(row['Unid_Compra']).strip(),
        'Preco_Padrao': preco,
        'Kcal_Por_Unidade_Receita': kcal_unid,
        'Fator_Conversao': fator_conv,
        'Ativo': ativo_converted,  # Campo 7
        'Observacoes': str(row.get('Observacoes', '')),
        
        # Estrutura NOVA (minúscula)
        'nome': nome,
        'categoria': categoria,
        'unid_receita': str(row['Unid_Receita']).strip(),
        'unid_compra': str(row['Unid_Compra']).strip(),
        'preco': preco,
        'kcal_unid': kcal_unid,
        'fator_conv': fator_conv,
        'ativo': ativo_converted,  # Campo 16
        'observacoes': str(row.get('Observacoes', '')),
        'user_id': st.session_state.user['uid']
    }
    
    print(f"\n3. Estrutura criada com {len(ingredient_data)} campos:")
    for i, (key, value) in enumerate(ingredient_data.items()):
        if i in [7, 16]:  # Campos problemáticos
            print(f"   Campo {i}: '{key}' = {value} ({type(value).__name__}) <<<< PROBLEMÁTICO")
        else:
            print(f"   Campo {i}: '{key}' = {value} ({type(value).__name__})")
    
    # 4. Testar token manager
    print(f"\n4. Testando Token Manager:")
    try:
        from utils.token_manager import get_valid_token
        token = get_valid_token()
        print(f"   Token obtido: {token is not None}")
    except Exception as e:
        print(f"   Erro no token: {e}")
    
    # 5. Testar cliente Firestore
    print(f"\n5. Testando FirestoreClient:")
    try:
        from utils.firestore_client import get_firestore_client
        client = get_firestore_client()
        print(f"   Cliente obtido: {client is not None}")
        
        if client:
            # Testar conversão dos campos problemáticos
            print(f"\n6. Testando conversão dos campos problemáticos:")
            
            campo_7 = ingredient_data['Ativo']  # Campo 7
            campo_16 = ingredient_data['ativo']  # Campo 16
            
            conv_7 = client._convert_to_firestore_value(campo_7)
            conv_16 = client._convert_to_firestore_value(campo_16)
            
            print(f"   Campo 7 ('Ativo'): {campo_7} -> {conv_7}")
            print(f"   Campo 16 ('ativo'): {campo_16} -> {conv_16}")
            
            # Verificar se está correto
            if conv_7.get('booleanValue') is not None and conv_16.get('booleanValue') is not None:
                print(f"   CONVERSÃO CORRETA: Ambos campos viraram booleanValue")
            else:
                print(f"   CONVERSÃO INCORRETA:")
                if 'integerValue' in conv_7:
                    print(f"     Campo 7 virou integerValue (PROBLEMA!)")
                if 'integerValue' in conv_16:
                    print(f"     Campo 16 virou integerValue (PROBLEMA!)")
    
    except Exception as e:
        print(f"   Erro no cliente: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 7. Teste completo de salvamento
    print(f"\n7. Teste completo de salvamento:")
    try:
        collection_path = f"users/{st.session_state.user['uid']}/ingredients"
        collection = client.collection(collection_path)
        
        # Tentar salvar
        result = collection.add(ingredient_data)
        
        if result and 'name' in result:
            doc_id = result['name'].split('/')[-1]
            print(f"   SUCESSO: Documento salvo com ID {doc_id}")
            
            # Verificar se foi salvo
            docs = collection.get()
            print(f"   Verificação: {len(docs)} documentos na coleção")
            
            return True
        else:
            print(f"   FALHA: Resultado inválido - {result}")
            return False
            
    except Exception as e:
        print(f"   ERRO no salvamento: {e}")
        
        error_str = str(e)
        if "TYPE_INT64" in error_str and "True" in error_str:
            print(f"\n   *** ERRO CONFIRMADO: Boolean -> integerValue ***")
            print(f"   Isso significa que há outra versão do código sendo usada")
            print(f"   ou há cache/import que está impedindo a correção")
        
        return False
    
    print(f"\n" + "=" * 70)
    return True

if __name__ == "__main__":
    success = test_complete_real_scenario()
    
    print(f"RESULTADO FINAL:")
    if success:
        print(f"✓ TESTE PASSOU - Upload funcionando")
        print(f"✓ Correção boolean efetiva")
        print(f"✓ Aplicação pronta para uso")
    else:
        print(f"✗ TESTE FALHOU - Problema persiste")
        print(f"✗ Investigação adicional necessária")
        print(f"✗ Pode haver cache ou versão incorreta sendo usada")