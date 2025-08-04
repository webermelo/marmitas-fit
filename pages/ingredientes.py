# -*- coding: utf-8 -*-
"""
Página de Gestão de Ingredientes
"""

import streamlit as st
import pandas as pd
from utils.database import get_database_manager
from pages.auth import AuthManager

def show_ingredientes_page():
    """Página principal de ingredientes"""
    
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    db_manager = get_database_manager()
    
    st.title("🥕 Gestão de Ingredientes")
    
    # Carregar ingredientes do usuário
    df_ingredientes = db_manager.get_user_ingredients(user["uid"])
    
    # Tabs para diferentes operações
    tab_lista, tab_cadastro = st.tabs(["📋 Lista de Ingredientes", "➕ Cadastrar/Editar"])
    
    with tab_lista:
        show_ingredients_list(df_ingredientes, db_manager)
    
    with tab_cadastro:
        show_ingredient_form(user["uid"], db_manager)

def show_ingredients_list(df_ingredientes, db_manager):
    """Mostra lista de ingredientes"""
    
    st.subheader("📋 Seus Ingredientes")
    
    if df_ingredientes.empty:
        st.info("Nenhum ingrediente cadastrado ainda. Use a aba 'Cadastrar/Editar' para adicionar ingredientes.")
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("🔍 Pesquisar ingrediente", placeholder="Digite o nome...")
    
    with col2:
        if 'Categoria' in df_ingredientes.columns:
            categorias = ['Todos'] + sorted(df_ingredientes['Categoria'].unique().tolist())
            categoria_filter = st.selectbox("🏷️ Filtrar por categoria", categorias)
        else:
            categoria_filter = 'Todos'
    
    # Aplicar filtros
    df_filtered = df_ingredientes.copy()
    
    if search_term:
        df_filtered = df_filtered[df_filtered['Nome'].str.contains(search_term, case=False, na=False)]
    
    if categoria_filter != 'Todos':
        df_filtered = df_filtered[df_filtered['Categoria'] == categoria_filter]
    
    # Mostrar tabela
    if not df_filtered.empty:
        st.markdown(f"**{len(df_filtered)} ingrediente(s) encontrado(s)**")
        
        # Configurar colunas para exibição
        display_columns = ['Nome', 'Categoria', 'Unidade_Receita', 'Unidade_Compra', 'Preco_Padrao', 'Kcal_Por_Unidade_Receita']
        
        # Exibir dataframe editável
        edited_df = st.data_editor(
            df_filtered[display_columns],
            use_container_width=True,
            num_rows="dynamic",
            key="ingredients_editor"
        )
        
        # Botões de ação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Salvar Alterações"):
                st.success("✅ Alterações salvas! (Funcionalidade em implementação)")
        
        with col2:
            if st.button("📥 Exportar Excel"):
                # Exportar para Excel
                try:
                    df_export = df_filtered[display_columns]
                    excel_data = df_export.to_excel(index=False)
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=excel_data,
                        file_name="ingredientes_marmitas_fit.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Erro ao exportar: {e}")
        
        with col3:
            if st.button("🗑️ Limpar Filtros"):
                st.rerun()
    
    else:
        st.warning("Nenhum ingrediente encontrado com os filtros aplicados.")

def show_ingredient_form(user_id, db_manager):
    """Formulário para cadastrar/editar ingredientes"""
    
    st.subheader("➕ Cadastrar Novo Ingrediente")
    
    with st.form("ingredient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("📛 Nome do Ingrediente*", placeholder="Ex: Frango (peito)")
            categoria = st.selectbox("🏷️ Categoria*", [
                'Proteína Animal', 'Proteína Vegetal', 'Carboidrato', 
                'Leguminosa', 'Vegetal', 'Fruta', 'Laticínio', 'Tempero', 'Gordura'
            ])
            unidade_receita = st.selectbox("📏 Unidade na Receita*", ['g', 'ml', 'unidade'])
        
        with col2:
            unidade_compra = st.selectbox("🛒 Unidade de Compra*", [
                'kg', 'L', 'dúzia', 'unidade', 'pacote', 'maço', 'bandeja'
            ])
            preco_padrao = st.number_input("💰 Preço Padrão (R$)*", min_value=0.0, step=0.01, format="%.2f")
            kcal_por_unidade = st.number_input("🔥 Kcal por Unidade de Receita*", min_value=0.0, step=0.01, format="%.2f")
        
        fator_conversao = st.number_input("🔄 Fator de Conversão*", min_value=1, value=1000, help="Quantas unidades de receita cabem na unidade de compra")
        
        submit_button = st.form_submit_button("💾 Salvar Ingrediente", use_container_width=True)
        
        if submit_button:
            if nome and categoria and unidade_receita and unidade_compra and preco_padrao > 0 and kcal_por_unidade >= 0 and fator_conversao > 0:
                
                ingredient_data = {
                    "Nome": nome,
                    "Categoria": categoria,
                    "Unidade_Receita": unidade_receita,
                    "Unidade_Compra": unidade_compra,
                    "Preco_Padrao": preco_padrao,
                    "Kcal_Por_Unidade_Receita": kcal_por_unidade,
                    "Fator_Conversao": fator_conversao
                }
                
                with st.spinner("Salvando ingrediente..."):
                    if db_manager.save_ingredient(user_id, ingredient_data):
                        st.success(f"✅ Ingrediente '{nome}' salvo com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar ingrediente!")
            
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")
    
    # Upload de arquivo Excel
    st.markdown("---")
    st.subheader("📤 Importar Ingredientes do Excel")
    
    uploaded_file = st.file_uploader(
        "Faça upload de um arquivo Excel com ingredientes",
        type=['xlsx', 'xls'],
        help="O arquivo deve conter as colunas: Nome, Categoria, Unidade_Receita, Unidade_Compra, Preco_Padrao, Kcal_Por_Unidade_Receita, Fator_Conversao"
    )
    
    if uploaded_file is not None:
        try:
            df_upload = pd.read_excel(uploaded_file)
            
            st.write("**Preview dos dados:**")
            st.dataframe(df_upload.head())
            
            if st.button("📥 Importar Dados"):
                success_count = 0
                for _, row in df_upload.iterrows():
                    ingredient_data = row.to_dict()
                    if db_manager.save_ingredient(user_id, ingredient_data):
                        success_count += 1
                
                st.success(f"✅ {success_count} ingredientes importados com sucesso!")
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")

def get_user_ingredients_dict(user_id):
    """Retorna ingredientes do usuário como dicionário para uso em outras páginas"""
    db_manager = get_database_manager()
    df_ingredients = db_manager.get_user_ingredients(user_id)
    
    if df_ingredients.empty:
        return {}
    
    return df_ingredients.set_index('Nome').to_dict('index')