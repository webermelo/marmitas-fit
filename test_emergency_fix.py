# -*- coding: utf-8 -*-
"""
TESTE DE EMERGÊNCIA - Problema de persistência
Teste final para identificar e corrigir o problema de conversão de booleanos
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO

def emergency_test():
    """Teste de emergência com dados mínimos"""
    
    st.title("🚨 TESTE DE EMERGÊNCIA - CONVERSÃO BOOLEANOS")
    st.error("Este teste vai identificar EXATAMENTE onde está o problema!")
    
    # Dados mínimos de teste
    csv_test = """Nome,Categoria,Preco,Unid_Receita,Unid_Compra,Kcal_Unid,Fator_Conv,Ativo,Observacoes
Teste Item,Teste Cat,1.00,g,kg,1.0,1000,TRUE,Teste observacao"""
    
    st.subheader("📋 Dados de Teste")
    df = pd.read_csv(StringIO(csv_test))
    st.dataframe(df)
    
    st.subheader("🔍 Análise dos Dados")
    for col in df.columns:
        st.write(f"**{col}**: {df[col].dtype}")
    
    if st.button("🧪 TESTE COMPLETO DE CONVERSÃO"):
        st.subheader("🧪 EXECUTANDO TESTE...")
        
        # Processar dados exatamente como admin_safe.py faz
        for idx, row in df.iterrows():
            st.write(f"**LINHA {idx + 1}:**")
            
            # Nome e categoria
            nome = str(row['Nome']).strip() if pd.notna(row['Nome']) else ''
            categoria = str(row['Categoria']).strip() if pd.notna(row['Categoria']) else ''
            
            # Conversões numéricas
            preco = float(row['Preco']) if pd.notna(row['Preco']) else 0.0
            kcal_unid = float(row['Kcal_Unid']) if pd.notna(row['Kcal_Unid']) else 0.0
            fator_conv = float(row['Fator_Conv']) if pd.notna(row['Fator_Conv']) else 1.0
            
            # CONVERSÃO CRÍTICA DO BOOLEANO
            ativo_original = row['Ativo']
            st.info(f"Ativo original: {repr(ativo_original)} ({type(ativo_original).__name__})")
            
            ativo_processed = str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True
            st.success(f"Ativo processado: {repr(ativo_processed)} ({type(ativo_processed).__name__})")
            
            # Estrutura completa como admin_safe.py cria
            ingredient_data_compatible = {
                'Nome': nome,
                'Categoria': categoria,
                'Unidade_Receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
                'Unidade_Compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
                'Preco_Padrao': preco,
                'Kcal_Por_Unidade_Receita': kcal_unid,
                'Fator_Conversao': fator_conv,
                'Ativo': ativo_processed,  # CAMPO CRÍTICO 1
                'Observacoes': str(row.get('Observacoes', '')).strip() if pd.notna(row.get('Observacoes', '')) else '',
                
                # Estrutura duplicada
                'nome': nome,
                'categoria': categoria,
                'unid_receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
                'unid_compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
                'preco': preco,
                'kcal_unid': kcal_unid,
                'fator_conv': fator_conv,
                'ativo': ativo_processed,  # CAMPO CRÍTICO 2
                'observacoes': str(row.get('Observacoes', '')).strip() if pd.notna(row.get('Observacoes', '')) else ''
            }
            
            # Adicionar metadados
            ingredient_data_compatible['user_id'] = "test_user_emergency"
            ingredient_data_compatible['created_at'] = datetime.now().isoformat()
            
            st.subheader("📦 DADOS FINAIS PARA FIREBASE")
            field_count = 0
            for key, value in ingredient_data_compatible.items():
                field_count += 1
                is_bool = isinstance(value, bool)
                type_name = type(value).__name__
                
                if is_bool:
                    st.success(f"Campo {field_count:2d}: **{key}** = `{value}` (✅ {type_name})")
                else:
                    st.info(f"Campo {field_count:2d}: **{key}** = `{value}` ({type_name})")
                
                # Marcar os campos 7 e 16 especificamente mencionados no erro
                if field_count in [7, 16]:
                    st.error(f"🎯 **CAMPO {field_count}** - MENCIONADO NO ERRO ORIGINAL!")
                    if key in ['ativo', 'Ativo']:
                        if not isinstance(value, bool):
                            st.error(f"🚨 PROBLEMA ENCONTRADO! Campo '{key}' deveria ser bool mas é {type_name}")
                        else:
                            st.success(f"✅ Campo '{key}' está correto como bool")
            
            # Teste da conversão Firestore SEM fazer requisição real
            st.subheader("🔥 TESTE DA CONVERSÃO FIRESTORE")
            
            # Simular função _convert_to_firestore_value
            for key, value in ingredient_data_compatible.items():
                if key in ['ativo', 'Ativo']:  # Focar nos campos problemáticos
                    st.write(f"**Testando campo '{key}':**")
                    if isinstance(value, str):
                        st.error(f"❌ Seria convertido para stringValue: {value}")
                    elif isinstance(value, bool):
                        st.success(f"✅ Seria convertido para booleanValue: {value}")
                    elif isinstance(value, int):
                        st.error(f"❌ Seria convertido para integerValue: {str(value)}")
                    else:
                        st.warning(f"⚠️ Tipo não reconhecido: {type(value).__name__}")
    
    if st.button("🔥 TESTE REAL COM FIREBASE"):
        st.subheader("🔥 TENTATIVA REAL DE SALVAMENTO")
        test_real_firebase_save()

def test_real_firebase_save():
    """Testa salvamento real no Firebase com dados mínimos"""
    
    if 'user' not in st.session_state:
        st.error("❌ Usuário não logado - não é possível testar Firebase")
        return
    
    try:
        from utils.token_manager import get_valid_token
        from utils.firestore_client import get_firestore_client
        
        token = get_valid_token()
        if not token:
            st.error("❌ Token inválido")
            return
        
        db = get_firestore_client()
        if not db:
            st.error("❌ Cliente Firestore não disponível")
            return
        
        # Dados mínimos para teste
        test_data = {
            'nome': 'Teste Emergency',
            'categoria': 'Teste',
            'preco': 1.0,
            'ativo': True,  # CAMPO CRÍTICO
            'user_id': st.session_state.user['uid'],
            'created_at': datetime.now().isoformat()
        }
        
        st.info("📡 Tentando salvar no Firebase...")
        st.json(test_data)
        
        user_id = st.session_state.user['uid']
        collection_path = f'users/{user_id}/test_emergency'
        
        result = db.collection(collection_path).add(test_data)
        
        if result:
            st.success(f"✅ SUCESSO! Documento salvo: {result}")
        else:
            st.error("❌ Falha no salvamento")
        
    except Exception as e:
        st.error(f"❌ ERRO: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    emergency_test()