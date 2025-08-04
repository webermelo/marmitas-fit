# -*- coding: utf-8 -*-
"""
Página de Planejamento de Produção
"""

import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime
from utils.database import get_database_manager
from pages.auth import AuthManager
from pages.receitas import get_user_recipes_for_production
from pages.ingredientes import get_user_ingredients_dict

def show_producao_page():
    """Página principal de produção"""
    
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    
    st.title("🏭 Planejamento de Produção")
    
    # Verificar se há receitas
    recipes_dict = get_user_recipes_for_production(user["uid"])
    ingredients_dict = get_user_ingredients_dict(user["uid"])
    
    if not recipes_dict:
        st.warning("⚠️ Você precisa cadastrar receitas primeiro!")
        if st.button("➕ Ir para Receitas"):
            st.switch_page("pages/receitas.py")
        return
    
    if not ingredients_dict:
        st.warning("⚠️ Você precisa cadastrar ingredientes primeiro!")
        if st.button("➕ Ir para Ingredientes"):
            st.switch_page("pages/ingredientes.py")
        return
    
    # Tabs para diferentes operações
    tab_planejamento, tab_lista_compras, tab_relatorio = st.tabs([
        "📋 Planejamento", "🛒 Lista de Compras", "📊 Relatório de Custos"
    ])
    
    with tab_planejamento:
        show_production_planning(recipes_dict)
    
    with tab_lista_compras:
        show_shopping_list(recipes_dict, ingredients_dict)
    
    with tab_relatorio:
        show_cost_report()

def show_production_planning(recipes_dict):
    """Planejamento da produção"""
    
    st.subheader("📋 Planejamento de Produção")
    
    # Inicializar lista de produção na sessão
    if 'production_plan' not in st.session_state:
        st.session_state.production_plan = []
    
    # Formulário para adicionar receita à produção
    with st.form("add_to_production", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            receita_selecionada = st.selectbox(
                "Selecione a Receita", 
                options=list(recipes_dict.keys()),
                key="recipe_select"
            )
        
        with col2:
            quantidade_producao = st.number_input("Quantidade", min_value=1, value=1, key="production_quantity")
        
        with col3:
            st.write("")  # Espaço
            add_to_production_btn = st.form_submit_button("➕ Adicionar à Produção")
        
        if add_to_production_btn and receita_selecionada and quantidade_producao > 0:
            # Verificar se receita já foi adicionada
            existing_recipe_index = None
            for i, item in enumerate(st.session_state.production_plan):
                if item['receita'] == receita_selecionada:
                    existing_recipe_index = i
                    break
            
            if existing_recipe_index is not None:
                # Atualizar quantidade
                st.session_state.production_plan[existing_recipe_index]['quantidade'] += quantidade_producao
            else:
                # Adicionar nova receita
                recipe_data = recipes_dict[receita_selecionada]
                st.session_state.production_plan.append({
                    'receita': receita_selecionada,
                    'quantidade': quantidade_producao,
                    'custo_unitario': recipe_data['custo_total'],
                    'calorias_unitario': recipe_data['calorias_total']
                })
            
            st.rerun()
    
    # Mostrar plano de produção
    if st.session_state.production_plan:
        st.markdown("**Plano de Produção Atual:**")
        
        total_custo = 0
        total_marmitas = 0
        
        for i, item in enumerate(st.session_state.production_plan):
            with st.expander(f"🍽️ {item['receita']} - {item['quantidade']} unidades", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                custo_total_item = item['quantidade'] * item['custo_unitario']
                total_custo += custo_total_item
                total_marmitas += item['quantidade']
                
                with col1:
                    st.metric("Quantidade", f"{item['quantidade']} un.")
                
                with col2:
                    st.metric("Custo Unitário", f"R$ {item['custo_unitario']:.2f}")
                
                with col3:
                    st.metric("Custo Total", f"R$ {custo_total_item:.2f}")
                
                with col4:
                    if st.button("🗑️ Remover", key=f"remove_production_{i}"):
                        st.session_state.production_plan.pop(i)
                        st.rerun()
        
        # Resumo da produção
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📦 Total de Marmitas", f"{total_marmitas} unidades")
        
        with col2:
            st.metric("💰 Custo Total", f"R$ {total_custo:.2f}")
        
        with col3:
            custo_medio = total_custo / total_marmitas if total_marmitas > 0 else 0
            st.metric("💵 Custo Médio por Marmita", f"R$ {custo_medio:.2f}")
        
        # Botão para limpar produção
        if st.button("🗑️ Limpar Produção"):
            st.session_state.production_plan = []
            st.rerun()

def show_shopping_list(recipes_dict, ingredients_dict):
    """Gera lista de compras consolidada"""
    
    st.subheader("🛒 Lista de Compras Consolidada")
    
    if not st.session_state.get('production_plan', []):
        st.info("Adicione receitas ao planejamento na aba 'Planejamento' para gerar a lista de compras.")
        return
    
    # Consolidar ingredientes
    ingredientes_consolidados = defaultdict(float)
    
    try:
        for item_producao in st.session_state.production_plan:
            receita_nome = item_producao['receita']
            quantidade_producao = item_producao['quantidade']
            
            if receita_nome in recipes_dict:
                receita_data = recipes_dict[receita_nome]
                
                for ingrediente_info in receita_data['ingredientes']:
                    ingrediente_nome = ingrediente_info['ingrediente']
                    quantidade_ingrediente = ingrediente_info['quantidade']
                    
                    ingredientes_consolidados[ingrediente_nome] += quantidade_ingrediente * quantidade_producao
        
        if not ingredientes_consolidados:
            st.warning("Nenhum ingrediente encontrado para consolidar.")
            return
        
        # Gerar tabela de lista de compras
        st.markdown(f"**Lista de compras para {len(ingredientes_consolidados)} ingredientes únicos:**")
        
        lista_compras = []
        custo_total_compras = 0
        ingredientes_nao_encontrados = []
        
        for ingrediente, qtd_total in sorted(ingredientes_consolidados.items()):
            if ingrediente in ingredients_dict:
                ing_data = ingredients_dict[ingrediente]
                
                # Calcular quantidade a comprar
                fator_conversao = ing_data.get('Fator_Conversao', 1)
                qtd_comprar = np.ceil(qtd_total / fator_conversao) if fator_conversao > 0 else 1
                custo_item = qtd_comprar * ing_data.get('Preco_Padrao', 0)
                custo_total_compras += custo_item
                
                lista_compras.append({
                    'Ingrediente': ingrediente,
                    'Qtd. Total Necessária': f"{qtd_total:.1f} {ing_data.get('Unidade_Receita', '')}",
                    'Unidade de Compra': ing_data.get('Unidade_Compra', ''),
                    'Qtd. a Comprar': f"{qtd_comprar:.0f} un.",
                    'Custo Estimado': f"R$ {custo_item:.2f}"
                })
            else:
                ingredientes_nao_encontrados.append(ingrediente)
                lista_compras.append({
                    'Ingrediente': ingrediente,
                    'Qtd. Total Necessária': f"{qtd_total:.1f}",
                    'Unidade de Compra': '❌ NÃO ENCONTRADO',
                    'Qtd. a Comprar': '-',
                    'Custo Estimado': '-'
                })
        
        # Mostrar tabela
        if lista_compras:
            df_lista_compras = pd.DataFrame(lista_compras)
            st.dataframe(df_lista_compras, use_container_width=True)
            
            # Resumo de custos
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("💰 Custo Total Estimado das Compras", f"R$ {custo_total_compras:.2f}")
            
            with col2:
                st.metric("✅ Ingredientes Encontrados", f"{len(lista_compras) - len(ingredientes_nao_encontrados)}")
            
            # Ingredientes não encontrados
            if ingredientes_nao_encontrados:
                st.warning(f"⚠️ **{len(ingredientes_nao_encontrados)} ingrediente(s) não encontrado(s) na sua base:**")
                for ing in ingredientes_nao_encontrados:
                    st.write(f"• {ing}")
                st.info("💡 Cadastre esses ingredientes na aba 'Ingredientes' para calcular os custos corretamente.")
            
            # Botão para exportar
            if st.button("📥 Exportar Lista de Compras"):
                csv_data = df_lista_compras.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"lista_compras_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    except Exception as e:
        st.error(f"❌ Erro ao gerar lista de compras: {e}")
        st.write("Dados de debug:")
        st.write(f"Produção: {st.session_state.production_plan}")
        st.write(f"Receitas: {list(recipes_dict.keys())}")

def show_cost_report():
    """Relatório de custos detalhado"""
    
    st.subheader("📊 Relatório de Custos")
    
    if not st.session_state.get('production_plan', []):
        st.info("Adicione receitas ao planejamento para ver o relatório de custos.")
        return
    
    # Calcular métricas detalhadas
    production_data = []
    
    for item in st.session_state.production_plan:
        custo_total_item = item['quantidade'] * item['custo_unitario']
        calorias_total_item = item['quantidade'] * item['calorias_unitario']
        
        production_data.append({
            'Receita': item['receita'],
            'Quantidade': item['quantidade'],
            'Custo Unitário': item['custo_unitario'],
            'Custo Total': custo_total_item,
            'Calorias por Unidade': item['calorias_unitario'],
            'Calorias Totais': calorias_total_item
        })
    
    if production_data:
        df_production = pd.DataFrame(production_data)
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Total de Marmitas", f"{df_production['Quantidade'].sum()}")
        
        with col2:
            st.metric("💰 Custo Total", f"R$ {df_production['Custo Total'].sum():.2f}")
        
        with col3:
            custo_medio = df_production['Custo Total'].sum() / df_production['Quantidade'].sum()
            st.metric("💵 Custo Médio", f"R$ {custo_medio:.2f}")
        
        with col4:
            calorias_media = df_production['Calorias Totais'].sum() / df_production['Quantidade'].sum()
            st.metric("🔥 Calorias Médias", f"{calorias_media:.0f} kcal")
        
        # Tabela detalhada
        st.markdown("**Detalhamento por Receita:**")
        st.dataframe(df_production, use_container_width=True)
        
        # Gráfico de custos por receita
        try:
            import plotly.express as px
            
            fig = px.pie(
                df_production, 
                values='Custo Total', 
                names='Receita',
                title="Distribuição de Custos por Receita"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except ImportError:
            st.info("📈 Instale plotly para visualizar gráficos: pip install plotly")
        
        # Exportar relatório
        if st.button("📄 Exportar Relatório"):
            excel_data = df_production.to_excel(index=False)
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"relatorio_producao_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )