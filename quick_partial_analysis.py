#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE RÁPIDA - Upload Parcial
Diagnóstico rápido do problema de upload parcial
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Análise Rápida - Upload Parcial",
        page_icon="⚡",
        layout="wide"
    )
    
    st.title("⚡ ANÁLISE RÁPIDA - UPLOAD PARCIAL")
    st.markdown("---")
    
    if 'user' not in st.session_state:
        st.error("❌ Faça login primeiro em app.py")
        return
    
    user_id = st.session_state.user['uid']
    st.success(f"✅ Usuário: {user_id}")
    
    # Análise rápida - botão único
    if st.button("🔍 EXECUTAR ANÁLISE RÁPIDA", type="primary"):
        
        st.header("📊 1. CONTAGEM ATUAL DE INGREDIENTES")
        
        try:
            from utils.database import get_database_manager
            
            db_manager = get_database_manager()
            current_df = db_manager.get_user_ingredients(user_id)
            
            if current_df.empty:
                st.error("❌ NENHUM ingrediente encontrado no Firebase")
                st.error("🚨 FALHA TOTAL DO UPLOAD")
            else:
                count = len(current_df)
                st.success(f"✅ {count} ingredientes encontrados no Firebase")
                
                if count < 198:
                    missing = 198 - count
                    st.warning(f"⚠️ UPLOAD PARCIAL: {missing} ingredientes ausentes")
                    
                    # Calcular percentual
                    percentage = (count / 198) * 100
                    st.metric("Taxa de Sucesso", f"{percentage:.1f}%")
                    
                    if count > 0:
                        st.info("✅ PROGRESSO: Erro boolean foi corrigido (alguns salvos)")
                        st.warning("❌ PROBLEMA ATUAL: Upload incompleto")
                    
                elif count == 198:
                    st.success("🎉 TODOS OS 198 INGREDIENTES PRESENTES!")
                    st.balloons()
                else:
                    st.info(f"ℹ️ {count} ingredientes (mais que o esperado)")
        
        except Exception as e:
            st.error(f"❌ Erro ao verificar Firebase: {e}")
        
        st.header("🔍 2. POSSÍVEIS CAUSAS DO UPLOAD PARCIAL")
        
        causes = [
            {
                "causa": "Rate Limiting Firebase",
                "probabilidade": "ALTA",
                "descricao": "Firebase limitou operações por excesso de requests simultâneos",
                "solucao": "Upload em lotes menores com delays"
            },
            {
                "causa": "Timeout da Aplicação",
                "probabilidade": "ALTA", 
                "descricao": "Streamlit ou browser interrompeu por tempo limite",
                "solucao": "Upload em chunks com progress feedback"
            },
            {
                "causa": "Falhas Silenciosas",
                "probabilidade": "MÉDIA",
                "descricao": "Alguns registros falharam sem gerar erro visível",
                "solucao": "Validação individual de cada item"
            },
            {
                "causa": "Limite de Memória",
                "probabilidade": "BAIXA",
                "descricao": "Falta de memória durante processamento de 198 items",
                "solucao": "Processamento em lotes menores"
            },
            {
                "causa": "Dados Inválidos",
                "probabilidade": "MÉDIA",
                "descricao": "Alguns ingredientes têm dados que causam falha",
                "solucao": "Validação prévia dos dados do CSV"
            }
        ]
        
        for i, cause in enumerate(causes):
            with st.expander(f"{i+1}. {cause['causa']} ({cause['probabilidade']} probabilidade)"):
                st.write(f"**Descrição**: {cause['descricao']}")
                st.write(f"**Solução**: {cause['solucao']}")
        
        st.header("🚀 3. PRÓXIMAS AÇÕES RECOMENDADAS")
        
        actions = [
            "🔬 **Executar debug_partial_upload.py** para análise detalhada",
            "📊 **Usar batch_upload_optimizer.py** para reprocessar com otimizações",
            "🧪 **Testar upload de 10-20 ingredientes** primeiro para validar",
            "📋 **Comparar arquivo CSV** com o que está no Firebase",
            "🔄 **Fazer upload incremental** dos ingredientes faltantes"
        ]
        
        for action in actions:
            st.markdown(action)
        
        # Sugestão de arquivo de teste
        st.header("🧪 4. TESTE IMEDIATO SUGERIDO")
        
        test_ingredients = [
            {"Nome": "Teste Frango", "Categoria": "Proteina", "Preco": 25.90, "Ativo": True},
            {"Nome": "Teste Arroz", "Categoria": "Carboidrato", "Preco": 8.50, "Ativo": True},
            {"Nome": "Teste Brocolis", "Categoria": "Vegetal", "Preco": 12.30, "Ativo": False}
        ]
        
        st.info("💡 **Sugestão**: Teste primeiro com estes 3 ingredientes:")
        st.json(test_ingredients)
        
        if st.button("🧪 TESTAR 3 INGREDIENTES AGORA"):
            try:
                from utils.firestore_client import get_firestore_client
                
                client = get_firestore_client()
                if not client:
                    st.error("❌ Erro Firebase client")
                    return
                
                collection_path = f"users/{user_id}/ingredients"
                
                success_count = 0
                for ingredient in test_ingredients:
                    try:
                        ingredient_data = {
                            "nome": ingredient["Nome"],
                            "categoria": ingredient["Categoria"], 
                            "preco": ingredient["Preco"],
                            "ativo": ingredient["Ativo"],
                            "unid_receita": "g",
                            "unid_compra": "kg",
                            "kcal_unid": 1.0,
                            "fator_conv": 1000.0,
                            "observacoes": f"Teste rápido {datetime.now().isoformat()}",
                            "user_id": user_id,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        result = client.collection(collection_path).add(ingredient_data)
                        
                        if result:
                            success_count += 1
                            st.success(f"✅ {ingredient['Nome']} salvo com sucesso")
                        else:
                            st.error(f"❌ Falha ao salvar {ingredient['Nome']}")
                    
                    except Exception as item_error:
                        st.error(f"🚨 Erro em {ingredient['Nome']}: {item_error}")
                
                if success_count == 3:
                    st.success("🎉 TESTE PASSOU! Sistema funcionando - problema é com volume")
                    st.info("👉 **Próximo passo**: Usar batch_upload_optimizer.py")
                elif success_count > 0:
                    st.warning(f"⚠️ Parcial: {success_count}/3 funcionaram")
                else:
                    st.error("❌ TESTE FALHOU: Problema sistêmico")
            
            except Exception as e:
                st.error(f"🚨 Erro no teste: {e}")

if __name__ == "__main__":
    main()