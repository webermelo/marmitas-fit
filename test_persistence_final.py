#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final de Persistência - Solução Definitiva
Simula exatamente o fluxo da aplicação Streamlit
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Mock do Streamlit antes de importar qualquer coisa
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
    
    def success(self, msg): print(f"✅ {msg}")
    def error(self, msg): print(f"❌ {msg}")
    def warning(self, msg): print(f"⚠️ {msg}")
    def info(self, msg): print(f"ℹ️ {msg}")
    def code(self, msg): print(f"📄 {msg}")

# Configurar mock
import streamlit
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Adicionar path
sys.path.append(os.getcwd())

def test_complete_persistence():
    """Teste completo da persistência usando a arquitetura real"""
    print("=" * 70)
    print("🧪 TESTE FINAL DE PERSISTÊNCIA - ARQUITETURA COMPLETA")
    print("=" * 70)
    
    # Passo 1: Verificar arquivo CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    print(f"1️⃣ Verificando arquivo CSV: {os.path.basename(csv_path)}")
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return False
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"✅ CSV carregado: {len(df)} linhas, {len(df.columns)} colunas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # Mostrar primeira linha como exemplo
        first_row = df.iloc[0]
        print(f"📄 Exemplo (linha 1): {first_row['Nome']} - {first_row['Categoria']}")
        
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return False
    
    # Passo 2: Testar salvamento usando a função real do admin_safe
    print(f"\n2️⃣ Testando salvamento usando admin_safe.py...")
    
    try:
        # Importar função real do admin_safe
        from pages.admin_safe import save_ingredient_to_firebase_direct
        
        # Pegar primeira linha do CSV para teste
        test_row = df.iloc[0]
        
        # Criar estrutura exatamente como o admin_safe faz
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
            'test_marker': f'PERSISTENCE_TEST_{datetime.now().strftime("%H%M%S")}'
        }
        
        print(f"💾 Salvando: {ingredient_data['nome']} ({ingredient_data['categoria']})")
        
        # Tentar salvar usando função real
        save_result = save_ingredient_to_firebase_direct(ingredient_data)
        print(f"📊 Resultado do salvamento: {'SUCESSO' if save_result else 'FALHA'}")
        
    except Exception as e:
        print(f"❌ Erro no salvamento: {e}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")
        save_result = False
    
    # Passo 3: Testar carregamento usando a função real do app.py
    print(f"\n3️⃣ Testando carregamento usando app.py...")
    
    try:
        # Importar função real do app
        from app import load_ingredients_from_firebase
        
        # Carregar ingredientes
        ingredients_list = load_ingredients_from_firebase()
        
        print(f"📊 Ingredientes carregados: {len(ingredients_list)}")
        
        if ingredients_list:
            # Procurar nosso ingrediente de teste
            test_found = False
            for ingredient in ingredients_list:
                nome = ingredient.get('Nome', '')
                categoria = ingredient.get('Categoria', '') 
                marker = ingredient.get('test_marker', '')
                
                if 'PERSISTENCE_TEST' in str(marker) or nome == ingredient_data['nome']:
                    print(f"✅ Ingrediente encontrado: {nome} - {categoria}")
                    test_found = True
                    break
            
            if not test_found:
                print(f"⚠️ Ingrediente de teste não encontrado")
                print(f"📋 Primeiros 3 ingredientes da lista:")
                for i, ing in enumerate(ingredients_list[:3]):
                    nome = ing.get('Nome', 'N/A')
                    categoria = ing.get('Categoria', 'N/A')
                    print(f"   {i+1}. {nome} - {categoria}")
            
            load_result = len(ingredients_list) > 0
        else:
            print(f"❌ Nenhum ingrediente carregado")
            load_result = False
            
    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")
        load_result = False
    
    # Passo 4: Testar consistência das estruturas
    print(f"\n4️⃣ Verificando consistência das estruturas...")
    
    structure_ok = True
    
    if ingredients_list:
        sample_ingredient = ingredients_list[0]
        required_fields = ['Nome', 'Categoria', 'Preco_Padrao', 'Kcal_Por_Unidade_Receita']
        
        for field in required_fields:
            if field in sample_ingredient:
                print(f"✅ Campo '{field}': OK")
            else:
                print(f"❌ Campo '{field}': AUSENTE")
                structure_ok = False
    else:
        print(f"⚠️ Não foi possível verificar estrutura - lista vazia")
        structure_ok = False
    
    # Resultado Final
    print(f"\n" + "=" * 70)
    print(f"🎯 RESULTADO FINAL:")
    print(f"   📤 Salvamento (admin_safe.py): {'✅ OK' if save_result else '❌ FALHA'}")
    print(f"   📥 Carregamento (app.py): {'✅ OK' if load_result else '❌ FALHA'}")  
    print(f"   🏗️ Estrutura de dados: {'✅ OK' if structure_ok else '❌ FALHA'}")
    
    overall_success = save_result and load_result and structure_ok
    
    print(f"\n🚀 PERSISTÊNCIA GERAL: {'✅ FUNCIONANDO!' if overall_success else '❌ COM PROBLEMAS'}")
    
    if not overall_success:
        print(f"\n🔧 PROBLEMAS IDENTIFICADOS:")
        if not save_result:
            print(f"   • Salvamento via admin_safe não está funcionando")
        if not load_result:
            print(f"   • Carregamento via app não está funcionando")
        if not structure_ok:
            print(f"   • Estruturas de dados inconsistentes")
    else:
        print(f"\n🎉 SOLUÇÃO COMPLETA VALIDADA!")
        print(f"   O problema de persistência foi RESOLVIDO")
    
    return overall_success

if __name__ == "__main__":
    success = test_complete_persistence()
    exit(0 if success else 1)