# -*- coding: utf-8 -*-
"""
Página de Limpeza - Marmitas Fit
Ferramenta de limpeza para duplicatas de ingredientes
"""

import streamlit as st
import pandas as pd

def show_cleanup_page():
    """Página dedicada à limpeza de duplicatas"""
    
    st.title("🧹 Limpeza de Dados")
    st.warning("⚠️ ATENÇÃO: Ferramenta para limpeza de dados duplicados")
    
    # Verificar se há ingredientes
    total_ingredients = len(st.session_state.get('demo_ingredients', []))
    
    if total_ingredients == 0:
        st.info("Nenhum ingrediente encontrado para limpeza.")
        return
    
    # Mostrar status atual
    st.error(f"🚨 DETECTADO: {total_ingredients} ingredientes no banco de dados")
    
    if total_ingredients > 50:
        st.error("⚠️ POSSÍVEL PROBLEMA: Muitos ingredientes duplicados detectados!")
    
    # Debug: Mostrar alguns ingredientes
    with st.expander("🔍 Ver primeiros ingredientes"):
        for i, ing in enumerate(st.session_state.demo_ingredients[:5]):
            st.write(f"**Ingrediente {i+1}:**")
            if isinstance(ing, dict):
                cols = st.columns(4)
                with cols[0]:
                    st.write(f"Nome: {ing.get('nome', 'N/A')}")
                with cols[1]:
                    st.write(f"Categoria: {ing.get('categoria', 'N/A')}")
                with cols[2]:
                    st.write(f"Preço: {ing.get('preco', 'N/A')}")
                with cols[3]:
                    st.write(f"Status: {'OK' if ing.get('nome') else '❌ ERRO'}")
            else:
                st.write(f"Tipo inválido: {type(ing)}")
    
    st.markdown("---")
    
    # Opções de limpeza
    st.subheader("🛠️ Opções de Limpeza")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ LIMPAR TUDO", type="primary", key="clear_all"):
            st.session_state.demo_ingredients = []
            st.success(f"✅ Todos os {total_ingredients} ingredientes foram removidos!")
            st.balloons()
            st.rerun()
    
    with col2:
        if st.button("🔧 RESETAR COM BASE", key="reset_base"):
            # Carregar ingredientes base
            try:
                df = pd.read_csv("ingredientes_completos_200.csv")
                
                ingredientes_base = []
                for _, row in df.iterrows():
                    ingrediente = {
                        'nome': str(row['Nome']),
                        'categoria': str(row['Categoria']),
                        'preco': float(row['Preco']) if pd.notna(row['Preco']) else 0.0,
                        'unid_receita': str(row['Unid_Receita']),
                        'unid_compra': str(row['Unid_Compra']),
                        'kcal_unid': float(row['Kcal_Unid']) if pd.notna(row['Kcal_Unid']) else 0.0,
                        'fator_conv': float(row['Fator_Conv']) if pd.notna(row['Fator_Conv']) else 1.0,
                        'ativo': str(row['Ativo']).upper() == 'TRUE',
                        'observacoes': str(row['Observacoes']) if pd.notna(row['Observacoes']) else ''
                    }
                    ingredientes_base.append(ingrediente)
                
                st.session_state.demo_ingredients = ingredientes_base
                st.success(f"✅ Base de {len(ingredientes_base)} ingredientes carregada!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao carregar base: {e}")
    
    with col3:
        if st.button("📊 REMOVER DUPLICATAS", key="remove_dupes"):
            if 'demo_ingredients' in st.session_state:
                # Remover duplicatas por nome
                ingredientes_unicos = []
                nomes_vistos = set()
                
                for ing in st.session_state.demo_ingredients:
                    if isinstance(ing, dict):
                        nome = ing.get('nome', '').strip().lower()
                        if nome and nome not in nomes_vistos:
                            nomes_vistos.add(nome)
                            ingredientes_unicos.append(ing)
                
                duplicatas_removidas = len(st.session_state.demo_ingredients) - len(ingredientes_unicos)
                st.session_state.demo_ingredients = ingredientes_unicos
                
                st.success(f"✅ {duplicatas_removidas} duplicatas removidas!")
                st.info(f"Restam {len(ingredientes_unicos)} ingredientes únicos")
                st.rerun()
    
    st.markdown("---")
    
    # Informações adicionais
    with st.expander("ℹ️ Sobre este problema"):
        st.write("""
        **O que aconteceu:**
        - Múltiplos uploads criaram ingredientes duplicados
        - Alguns ingredientes podem ter dados corrompidos (mostram 'None')
        - Total de ingredientes muito alto indica problema
        
        **Soluções:**
        1. **LIMPAR TUDO**: Remove todos os ingredientes atuais
        2. **RESETAR COM BASE**: Substitui por base de 200 ingredientes limpa
        3. **REMOVER DUPLICATAS**: Mantém apenas um ingrediente por nome
        
        **Recomendação:** Use "RESETAR COM BASE" para voltar ao estado original.
        """)

if __name__ == "__main__":
    show_cleanup_page()