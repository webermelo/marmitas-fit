# -*- coding: utf-8 -*-
"""
Página de Gestão de Receitas
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import get_database_manager
from pages.auth import AuthManager
from pages.ingredientes import get_user_ingredients_dict

def show_receitas_page():
    """Página principal de receitas"""
    
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    db_manager = get_database_manager()
    
    st.title("📝 Gestão de Receitas")
    
    # Verificar se há ingredientes
    ingredients_dict = get_user_ingredients_dict(user["uid"])
    
    if not ingredients_dict:
        st.warning("⚠️ Você precisa cadastrar ingredientes primeiro!")
        if st.button("➕ Ir para Ingredientes"):
            st.switch_page("pages/ingredientes.py")
        return
    
    # Carregar receitas do usuário
    df_receitas = db_manager.get_user_recipes(user["uid"])
    
    # Tabs para diferentes operações
    tab_lista, tab_cadastro = st.tabs(["📋 Minhas Receitas", "👨‍🍳 Criar Receita"])
    
    with tab_lista:
        show_recipes_list(df_receitas, db_manager)
    
    with tab_cadastro:
        show_recipe_form(user["uid"], db_manager, ingredients_dict)

def show_recipes_list(df_receitas, db_manager):
    """Mostra lista de receitas"""
    
    st.subheader("📋 Suas Receitas")
    
    if df_receitas.empty:
        st.info("Nenhuma receita cadastrada ainda. Use a aba 'Criar Receita' para adicionar receitas.")
        return
    
    # Agrupar receitas por nome (uma receita pode ter vários ingredientes)
    if not df_receitas.empty and 'nome_receita' in df_receitas.columns:
        receitas_agrupadas = df_receitas.groupby('nome_receita').agg({
            'custo_total': 'first',
            'calorias_total': 'first',
            'created_at': 'first'
        }).reset_index()
        
        print(f"DEBUG: Receitas agrupadas: {len(receitas_agrupadas)}")
        for _, receita in receitas_agrupadas.iterrows():
            print(f"DEBUG: - {receita['nome_receita']}: R$ {receita['custo_total']:.2f}")
    else:
        receitas_agrupadas = pd.DataFrame()
    
    # Filtro de busca
    search_term = st.text_input("🔍 Pesquisar receita", placeholder="Digite o nome da receita...")
    
    if search_term and not receitas_agrupadas.empty:
        receitas_agrupadas = receitas_agrupadas[receitas_agrupadas['nome_receita'].str.contains(search_term, case=False, na=False)]
    
    # Mostrar receitas em cards
    if not receitas_agrupadas.empty:
        for _, receita in receitas_agrupadas.iterrows():
            with st.expander(f"🍽️ {receita['nome_receita']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💰 Custo", f"R$ {receita['custo_total']:.2f}")
                
                with col2:
                    st.metric("🔥 Calorias", f"{receita['calorias_total']:.0f} kcal")
                
                with col3:
                    st.metric("📅 Criada em", receita['created_at'].strftime('%d/%m/%Y') if receita['created_at'] else 'N/A')
                
                # Mostrar ingredientes da receita
                ingredientes_receita = df_receitas[df_receitas['nome_receita'] == receita['nome_receita']]
                
                st.markdown("**Ingredientes:**")
                for _, ing in ingredientes_receita.iterrows():
                    st.write(f"• {ing['ingrediente']}: {ing['quantidade']} {ing['unidade']}")
                
                # Botões de ação
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Editar", key=f"edit_{receita['nome_receita']}"):
                        st.info("Funcionalidade de edição em implementação")
                
                with col2:
                    if st.button(f"🗑️ Excluir", key=f"delete_{receita['nome_receita']}"):
                        st.error("Funcionalidade de exclusão em implementação")
    else:
        st.warning("Nenhuma receita encontrada. Tente ajustar os filtros ou criar uma nova receita.")

def show_recipe_form(user_id, db_manager, ingredients_dict):
    """Formulário para criar receitas"""
    
    st.subheader("👨‍🍳 Criar Nova Receita")
    
    # Nome da receita
    nome_receita = st.text_input("📛 Nome da Receita*", placeholder="Ex: Frango Grelhado com Batata Doce")
    
    # Ingredientes da receita
    st.markdown("**Ingredientes da Receita:**")
    
    # Inicializar lista de ingredientes na sessão
    if 'recipe_ingredients' not in st.session_state:
        st.session_state.recipe_ingredients = []
    
    # Formulário para adicionar ingrediente
    with st.form("add_ingredient", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            ingrediente_selecionado = st.selectbox(
                "Ingrediente", 
                options=list(ingredients_dict.keys()),
                key="ingredient_select"
            )
        
        with col2:
            quantidade = st.number_input("Quantidade", min_value=0.1, step=0.1, format="%.1f", key="quantity_input")
        
        with col3:
            unidade = ingredients_dict.get(ingrediente_selecionado, {}).get('Unidade_Receita', 'g')
            st.text_input("Unidade", value=unidade, disabled=True)
        
        add_ingredient_btn = st.form_submit_button("➕ Adicionar Ingrediente")
        
        if add_ingredient_btn and ingrediente_selecionado and quantidade > 0:
            # Verificar se ingrediente já foi adicionado
            if not any(ing['nome'] == ingrediente_selecionado for ing in st.session_state.recipe_ingredients):
                ingredient_info = ingredients_dict[ingrediente_selecionado]
                
                st.session_state.recipe_ingredients.append({
                    'nome': ingrediente_selecionado,
                    'quantidade': quantidade,
                    'unidade': ingredient_info['Unidade_Receita'],
                    'preco_unitario': ingredient_info['Preco_Padrao'] / ingredient_info['Fator_Conversao'],
                    'kcal_unitario': ingredient_info['Kcal_Por_Unidade_Receita']
                })
                st.rerun()
            else:
                st.error("❌ Ingrediente já adicionado à receita!")
    
    # Mostrar ingredientes adicionados
    if st.session_state.recipe_ingredients:
        st.markdown("**Ingredientes Adicionados:**")
        
        custo_total = 0
        calorias_total = 0
        
        for i, ing in enumerate(st.session_state.recipe_ingredients):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            custo_ingrediente = ing['quantidade'] * ing['preco_unitario']
            calorias_ingrediente = ing['quantidade'] * ing['kcal_unitario']
            
            custo_total += custo_ingrediente
            calorias_total += calorias_ingrediente
            
            with col1:
                st.write(f"• {ing['nome']}")
            
            with col2:
                st.write(f"{ing['quantidade']} {ing['unidade']}")
            
            with col3:
                st.write(f"R$ {custo_ingrediente:.2f}")
            
            with col4:
                if st.button("🗑️", key=f"remove_{i}"):
                    st.session_state.recipe_ingredients.pop(i)
                    st.rerun()
        
        # Mostrar totais
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("💰 Custo Total da Receita", f"R$ {custo_total:.2f}")
        
        with col2:
            st.metric("🔥 Calorias Totais", f"{calorias_total:.0f} kcal")
        
        # Botão para salvar receita
        if st.button("💾 Salvar Receita", use_container_width=True):
            if nome_receita and st.session_state.recipe_ingredients:
                
                # Preparar dados da receita
                for ingrediente in st.session_state.recipe_ingredients:
                    recipe_data = {
                        "nome_receita": nome_receita,
                        "ingrediente": ingrediente['nome'],
                        "quantidade": ingrediente['quantidade'],
                        "unidade": ingrediente['unidade'],
                        "custo_unitario": ingrediente['preco_unitario'],
                        "custo_total": custo_total,
                        "calorias_unitario": ingrediente['kcal_unitario'],
                        "calorias_total": calorias_total
                    }
                    
                    db_manager.save_recipe(user_id, recipe_data)
                
                st.success(f"✅ Receita '{nome_receita}' salva com sucesso!")
                st.session_state.recipe_ingredients = []  # Limpar lista
                st.rerun()
            
            else:
                st.error("❌ Preencha o nome da receita e adicione pelo menos um ingrediente!")
    
    # Botão para limpar ingredientes
    if st.session_state.recipe_ingredients:
        if st.button("🗑️ Limpar Todos os Ingredientes"):
            st.session_state.recipe_ingredients = []
            st.rerun()

def get_user_recipes_for_production(user_id):
    """Retorna receitas do usuário para usar na produção"""
    db_manager = get_database_manager()
    df_recipes = db_manager.get_user_recipes(user_id)
    
    if df_recipes.empty:
        return {}
    
    # Agrupar por nome da receita
    recipes_dict = {}
    for nome_receita in df_recipes['nome_receita'].unique():
        recipe_data = df_recipes[df_recipes['nome_receita'] == nome_receita]
        
        recipes_dict[nome_receita] = {
            'ingredientes': recipe_data[['ingrediente', 'quantidade', 'unidade']].to_dict('records'),
            'custo_total': recipe_data['custo_total'].iloc[0],
            'calorias_total': recipe_data['calorias_total'].iloc[0]
        }
    
    return recipes_dict