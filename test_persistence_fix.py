# -*- coding: utf-8 -*-
"""
TESTE DE PERSISTÊNCIA - SOLUÇÃO UNIFICADA
Verifica se ingredientes uploadados via admin são visíveis na lista
"""

import streamlit as st
from utils.database import get_database_manager

def test_persistence():
    st.title("🧪 TESTE DE PERSISTÊNCIA - SOLUÇÃO UNIFICADA")
    
    st.markdown("---")
    st.subheader("📋 Objetivo do Teste")
    st.write("""
    **Testar se:**
    1. Ingredientes salvos no Admin (admin_safe.py) aparecem na Lista (app.py)
    2. Sistema unificado DatabaseManager funciona
    3. Conversão de estruturas está correta
    """)
    
    # Simular usuário logado
    if 'user' not in st.session_state:
        st.session_state.user = {
            'email': 'teste@persistencia.com',
            'uid': 'test_user_123',
            'display_name': 'Teste Persistência',
            'token': 'fake_token_for_testing',
            'token_timestamp': '2025-01-11T10:00:00'
        }
        st.info("🔧 Usuário de teste simulado criado")
    
    st.markdown("---")
    st.subheader("🔍 TESTE 1: Inicialização do DatabaseManager")
    
    try:
        db_manager = get_database_manager()
        st.success("✅ DatabaseManager inicializado com sucesso")
        
        # Debug do cliente
        if db_manager.db:
            st.success("✅ Cliente Firestore conectado")
        else:
            st.warning("⚠️ Cliente Firestore não conectado (modo demo)")
        
    except Exception as e:
        st.error(f"❌ Erro ao inicializar DatabaseManager: {e}")
        return
    
    st.markdown("---")
    st.subheader("🔍 TESTE 2: Salvar Ingrediente de Teste")
    
    if st.button("💾 Salvar Ingrediente de Teste"):
        test_ingredient = {
            'Nome': 'TESTE PERSISTÊNCIA',
            'Categoria': 'Teste',
            'Unidade_Receita': 'g',
            'Unidade_Compra': 'kg',
            'Preco_Padrao': 99.99,
            'Kcal_Por_Unidade_Receita': 1.0,
            'Fator_Conversao': 1000.0,
            'Ativo': True,
            'Observacoes': 'Ingrediente criado pelo teste de persistência'
        }
        
        st.info("📤 Tentando salvar ingrediente...")
        
        try:
            user_id = st.session_state.user['uid']
            result = db_manager.save_ingredient(user_id, test_ingredient)
            
            if result:
                st.success("✅ TESTE 2 PASSOU: Ingrediente salvo com sucesso!")
            else:
                st.error("❌ TESTE 2 FALHOU: Erro ao salvar ingrediente")
                
        except Exception as e:
            st.error(f"❌ TESTE 2 FALHOU: Exceção ao salvar - {e}")
            import traceback
            st.code(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("🔍 TESTE 3: Carregar Ingredientes")
    
    if st.button("📥 Carregar Ingredientes"):
        st.info("📤 Tentando carregar ingredientes...")
        
        try:
            user_id = st.session_state.user['uid']
            df_ingredients = db_manager.get_user_ingredients(user_id)
            
            st.write(f"**Resultado:** {type(df_ingredients)}")
            st.write(f"**Shape:** {df_ingredients.shape if hasattr(df_ingredients, 'shape') else 'N/A'}")
            st.write(f"**Empty?** {df_ingredients.empty if hasattr(df_ingredients, 'empty') else 'N/A'}")
            
            if not df_ingredients.empty:
                st.success(f"✅ TESTE 3 PASSOU: {len(df_ingredients)} ingredientes carregados!")
                
                # Mostrar dados
                st.dataframe(df_ingredients)
                
                # Verificar se ingrediente de teste está presente
                if 'Nome' in df_ingredients.columns:
                    teste_presente = df_ingredients['Nome'].str.contains('TESTE PERSISTÊNCIA').any()
                    if teste_presente:
                        st.success("🎯 INGREDIENTE DE TESTE ENCONTRADO!")
                    else:
                        st.warning("⚠️ Ingrediente de teste não encontrado na lista")
                        
            else:
                st.error("❌ TESTE 3 FALHOU: DataFrame vazio")
                
        except Exception as e:
            st.error(f"❌ TESTE 3 FALHOU: Exceção ao carregar - {e}")
            import traceback
            st.code(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("🔍 TESTE 4: Teste de Conversão de Estruturas")
    
    with st.expander("🧪 Testar Conversões"):
        # Teste Firebase → App
        firebase_data = {
            'nome': 'Teste Firebase',
            'categoria': 'Teste',
            'unid_receita': 'g',
            'unid_compra': 'kg',
            'preco': 10.5,
            'kcal_unid': 2.0,
            'fator_conv': 1000,
            'ativo': True,
            'observacoes': 'teste'
        }
        
        st.write("**Firebase → App:**")
        converted_app = db_manager._convert_firebase_to_app_structure(firebase_data)
        st.json(converted_app)
        
        # Teste App → Firebase  
        app_data = {
            'Nome': 'Teste App',
            'Categoria': 'Teste',
            'Unidade_Receita': 'g',
            'Unidade_Compra': 'kg',
            'Preco_Padrao': 15.5,
            'Kcal_Por_Unidade_Receita': 3.0,
            'Fator_Conversao': 1000,
            'Ativo': True,
            'Observacoes': 'teste app'
        }
        
        st.write("**App → Firebase:**")
        converted_firebase = db_manager._convert_app_to_firebase_structure(app_data)
        st.json(converted_firebase)
    
    st.markdown("---")
    st.subheader("📊 RESUMO DOS TESTES")
    
    st.info("""
    **Se todos os testes passaram:**
    - ✅ DatabaseManager está funcionando
    - ✅ Conversões de estrutura estão corretas
    - ✅ Firebase está conectado ou modo demo ativo
    - ✅ Sistema unificado foi implementado com sucesso
    
    **Para testar persistência real:**
    1. Faça upload via Admin (Administração → Upload Ingredientes)
    2. Navegue para Ingredientes → Lista
    3. Ingredientes devem aparecer!
    """)

if __name__ == "__main__":
    test_persistence()