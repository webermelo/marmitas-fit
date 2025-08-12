#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DEFINITIVO PRODUÇÃO - Modelo Opus 4.0
Validação completa do sistema após todas as correções
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import traceback

def main():
    st.set_page_config(
        page_title="Teste Final Produção - Marmitas Fit",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 TESTE FINAL PRODUÇÃO - Opus 4.0")
    st.markdown("---")
    
    # Verificar estado do usuário
    if 'user' not in st.session_state:
        st.error("❌ ERRO: Usuário não logado")
        st.info("👉 Faça login primeiro em app.py")
        return
    
    user_id = st.session_state.user['uid']
    st.success(f"✅ Usuário logado: {user_id}")
    
    # Teste 1: Token Manager
    st.header("🔧 TESTE 1: Token Manager")
    try:
        from utils.token_manager import get_valid_token, ensure_token_timestamp
        
        # Garantir timestamp
        ensure_token_timestamp()
        
        # Obter token válido
        token = get_valid_token()
        
        if token:
            st.success(f"✅ Token válido obtido: {token[:20]}...")
        else:
            st.error("❌ FALHA: Não foi possível obter token válido")
            return
            
    except Exception as e:
        st.error(f"❌ ERRO Token Manager: {e}")
        st.code(traceback.format_exc())
        return
    
    # Teste 2: Firestore Client
    st.header("🔥 TESTE 2: Firestore Client")
    try:
        from utils.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        
        if client:
            st.success("✅ Cliente Firestore criado com sucesso")
            st.info(f"📍 Project ID: {client.project_id}")
            st.info(f"🔑 Token definido: {'SIM' if client.auth_token else 'NÃO'}")
        else:
            st.error("❌ FALHA: Cliente Firestore não criado")
            return
            
    except Exception as e:
        st.error(f"❌ ERRO Firestore Client: {e}")
        st.code(traceback.format_exc())
        return
    
    # Teste 3: Conversão de Tipos
    st.header("🔢 TESTE 3: Conversão de Tipos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧪 Teste Boolean")
        
        test_values = {
            "boolean_true": True,
            "boolean_false": False,
            "string_test": "Frango peito",
            "int_test": 100,
            "float_test": 32.90
        }
        
        st.json(test_values)
        
        # Testar conversões
        for key, value in test_values.items():
            converted = client._convert_to_firestore_value(value)
            
            if key.startswith("boolean"):
                if "booleanValue" in converted:
                    st.success(f"✅ {key}: {value} → {converted}")
                else:
                    st.error(f"❌ {key}: {value} → {converted} (ERRO: deveria ser booleanValue)")
            else:
                st.info(f"ℹ️ {key}: {value} → {converted}")
    
    with col2:
        st.subheader("📊 Teste isinstance()")
        
        test_bool = True
        
        st.code(f"""
test_bool = {test_bool}
isinstance(test_bool, bool) = {isinstance(test_bool, bool)}
isinstance(test_bool, int) = {isinstance(test_bool, int)}

ORDEM CRÍTICA:
1. Check bool PRIMEIRO ✅
2. Check int DEPOIS ✅
""")
    
    # Teste 4: Database Manager
    st.header("💾 TESTE 4: Database Manager")
    try:
        from utils.database import get_database_manager
        
        db_manager = get_database_manager()
        st.success("✅ Database Manager inicializado")
        
        # Testar caminho da coleção
        collection_path = db_manager.get_user_data_path(user_id, "ingredients")
        st.info(f"📍 Caminho coleção: {collection_path}")
        
    except Exception as e:
        st.error(f"❌ ERRO Database Manager: {e}")
        st.code(traceback.format_exc())
        return
    
    # Teste 5: Ingrediente de Teste
    st.header("🧅 TESTE 5: Salvar Ingrediente")
    
    if st.button("🚀 EXECUTAR TESTE DE SALVAMENTO"):
        test_ingredient = {
            "Nome": "TESTE_FINAL_PRODUCAO",
            "Categoria": "Teste",
            "Unidade_Receita": "g",
            "Unidade_Compra": "kg", 
            "Preco_Padrao": 99.99,
            "Kcal_Por_Unidade_Receita": 1.50,
            "Fator_Conversao": 1000.0,
            "Ativo": True,  # CRÍTICO: Este boolean deve virar booleanValue
            "Observacoes": f"Teste produção {datetime.now().isoformat()}"
        }
        
        st.json(test_ingredient)
        
        try:
            # Converter para estrutura Firebase
            firebase_data = db_manager._convert_app_to_firebase_structure(test_ingredient)
            st.subheader("🔄 Dados Convertidos")
            st.json(firebase_data)
            
            # Verificar se boolean foi preservado
            if isinstance(firebase_data.get('ativo'), bool):
                st.success("✅ Campo 'ativo' mantido como boolean")
            else:
                st.error(f"❌ Campo 'ativo' virou: {type(firebase_data.get('ativo'))}")
            
            # Salvar no Firebase
            st.subheader("💾 Salvando no Firebase...")
            result = db_manager.save_ingredient(user_id, test_ingredient)
            
            if result:
                st.success("✅ INGREDIENTE SALVO COM SUCESSO!")
            else:
                st.error("❌ FALHA AO SALVAR INGREDIENTE")
                
        except Exception as e:
            st.error(f"❌ ERRO ao salvar: {e}")
            st.code(traceback.format_exc())
    
    # Teste 6: Verificar Dados Salvos
    st.header("📋 TESTE 6: Verificar Dados Salvos")
    
    if st.button("🔍 CARREGAR INGREDIENTES"):
        try:
            st.info("🔄 Carregando ingredientes...")
            
            # Usar Database Manager unificado
            ingredients_df = db_manager.get_user_ingredients(user_id)
            
            if ingredients_df.empty:
                st.warning("⚠️ Nenhum ingrediente encontrado")
            else:
                st.success(f"✅ {len(ingredients_df)} ingredientes encontrados")
                
                # Mostrar ingredientes
                st.dataframe(ingredients_df)
                
                # Verificar se tem o ingrediente de teste
                if "TESTE_FINAL_PRODUCAO" in ingredients_df['Nome'].values:
                    st.success("✅ INGREDIENTE DE TESTE ENCONTRADO!")
                    
                    # Verificar campo boolean
                    test_row = ingredients_df[ingredients_df['Nome'] == "TESTE_FINAL_PRODUCAO"].iloc[0]
                    ativo_value = test_row['Ativo']
                    
                    if isinstance(ativo_value, bool):
                        st.success(f"✅ Campo 'Ativo' é boolean: {ativo_value}")
                    else:
                        st.error(f"❌ Campo 'Ativo' não é boolean: {ativo_value} ({type(ativo_value)})")
                
        except Exception as e:
            st.error(f"❌ ERRO ao carregar: {e}")
            st.code(traceback.format_exc())
    
    # Teste 7: Verificação Final
    st.header("🎯 TESTE 7: Verificação Final do Sistema")
    
    if st.button("🏁 EXECUTAR TESTE COMPLETO"):
        st.info("🔄 Executando bateria completa de testes...")
        
        test_results = {
            "token_manager": False,
            "firestore_client": False,
            "boolean_conversion": False,
            "database_manager": False,
            "save_ingredient": False,
            "load_ingredient": False
        }
        
        # Teste Token Manager
        try:
            token = get_valid_token()
            test_results["token_manager"] = token is not None
        except:
            pass
        
        # Teste Firestore Client
        try:
            client = get_firestore_client()
            test_results["firestore_client"] = client is not None
        except:
            pass
        
        # Teste Boolean Conversion
        try:
            converted = client._convert_to_firestore_value(True)
            test_results["boolean_conversion"] = "booleanValue" in converted
        except:
            pass
        
        # Teste Database Manager
        try:
            db_manager = get_database_manager()
            test_results["database_manager"] = db_manager is not None
        except:
            pass
        
        # Mostrar resultados
        st.subheader("📊 RESULTADOS DOS TESTES")
        
        all_passed = True
        for test_name, passed in test_results.items():
            if passed:
                st.success(f"✅ {test_name.upper().replace('_', ' ')}")
            else:
                st.error(f"❌ {test_name.upper().replace('_', ' ')}")
                all_passed = False
        
        st.markdown("---")
        
        if all_passed:
            st.balloons()
            st.success("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
        else:
            st.error("❌ ALGUNS TESTES FALHARAM. Verifique os logs acima.")
        
        # Informações de sistema
        st.subheader("🔧 Informações do Sistema")
        st.json({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "streamlit_version": st.__version__,
            "session_keys": list(st.session_state.keys()),
            "token_exists": 'token' in st.session_state.user if 'user' in st.session_state else False
        })

if __name__ == "__main__":
    main()