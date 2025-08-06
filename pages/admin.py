# -*- coding: utf-8 -*-
"""
Página de Administração - Marmitas Fit
Painel para gerenciar ingredientes, embalagens e usuários
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Lista de administradores autorizados
ADMINS = [
    "weber.melo@gmail.com",    # Super Admin Principal
    "weber@marmitasfit.com",   # Backup
    "admin@marmitasfit.com",   # Admin secundário
    "demo@marmitasfit.com"     # Para testes
]

def is_admin(user_email):
    """Verifica se o usuário é administrador"""
    return user_email.lower() in [admin.lower() for admin in ADMINS]

# Funções para gerar templates Excel diretamente
def generate_ingredientes_template():
    """Gera template de ingredientes"""
    data = [
        {
            'Nome': 'Frango (peito)',
            'Categoria': 'Proteína Animal',
            'Preço (R$)': 18.90,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 1.65,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Sem pele, congelado'
        },
        {
            'Nome': 'Arroz integral',
            'Categoria': 'Carboidrato',
            'Preço (R$)': 8.90,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 1.11,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Grão longo, tipo 1'
        },
        {
            'Nome': 'Brócolis',
            'Categoria': 'Vegetal',
            'Preço (R$)': 6.50,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 0.34,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Fresco, preço médio'
        },
        {
            'Nome': 'Azeite extra virgem',
            'Categoria': 'Gordura',
            'Preço (R$)': 12.00,
            'Unid.Receita': 'ml',
            'Unid.Compra': 'L',
            'Kcal/Unid': 8.84,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Primeira prensagem'
        },
        {
            'Nome': 'Sal refinado',
            'Categoria': 'Tempero',
            'Preço (R$)': 1.20,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 0.00,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Iodado'
        }
    ]
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, sheet_name='Ingredientes', index=False)
    buffer.seek(0)
    return buffer.getvalue()

def generate_embalagens_template():
    """Gera template de embalagens"""
    data = [
        {
            'Nome': 'Marmita 500ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.50,
            'Capacidade (ml)': 500,
            'Categoria': 'principal',
            'Ativo': True,
            'Descrição': 'PP transparente com tampa'
        },
        {
            'Nome': 'Marmita 750ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.65,
            'Capacidade (ml)': 750,
            'Categoria': 'principal',
            'Ativo': True,
            'Descrição': 'PP transparente com tampa'
        },
        {
            'Nome': 'Marmita 1000ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.80,
            'Capacidade (ml)': 1000,
            'Categoria': 'principal',
            'Ativo': True,
            'Descrição': 'PP transparente com tampa'
        },
        {
            'Nome': 'Pote sobremesa 150ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.25,
            'Capacidade (ml)': 150,
            'Categoria': 'complemento',
            'Ativo': True,
            'Descrição': 'Para doces e frutas'
        },
        {
            'Nome': 'Talher plástico',
            'Tipo': 'utensilio',
            'Preço (R$)': 0.08,
            'Capacidade (ml)': 0,
            'Categoria': 'utensilio',
            'Ativo': True,
            'Descrição': 'Garfo + faca + colher'
        },
        {
            'Nome': 'Guardanapo',
            'Tipo': 'higiene',
            'Preço (R$)': 0.05,
            'Capacidade (ml)': 0,
            'Categoria': 'higiene',
            'Ativo': True,
            'Descrição': 'Papel 20x20cm'
        },
        {
            'Nome': 'Sacola plástica',
            'Tipo': 'transporte',
            'Preço (R$)': 0.12,
            'Capacidade (ml)': 0,
            'Categoria': 'transporte',
            'Ativo': True,
            'Descrição': '30x40cm alça camiseta'
        }
    ]
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, sheet_name='Embalagens', index=False)
    buffer.seek(0)
    return buffer.getvalue()

def generate_custos_fixos_template():
    """Gera template de custos fixos"""
    data = [
        {
            'Categoria': 'Energia',
            'Item': 'Conta de luz',
            'Custo Mensal (R$)': 150.00,
            'Rateio por Marmita': 0.30,
            'Descrição': 'Fogão, geladeira, freezer'
        },
        {
            'Categoria': 'Gás',
            'Item': 'Botijão 13kg',
            'Custo Mensal (R$)': 80.00,
            'Rateio por Marmita': 0.16,
            'Descrição': 'Consumo médio mensal'
        },
        {
            'Categoria': 'Água',
            'Item': 'Conta de água',
            'Custo Mensal (R$)': 60.00,
            'Rateio por Marmita': 0.12,
            'Descrição': 'Limpeza e preparo'
        },
        {
            'Categoria': 'Aluguel',
            'Item': 'Espaço cozinha',
            'Custo Mensal (R$)': 800.00,
            'Rateio por Marmita': 1.60,
            'Descrição': 'Proporcional ao uso'
        },
        {
            'Categoria': 'Mão de obra',
            'Item': 'Salário próprio',
            'Custo Mensal (R$)': 2000.00,
            'Rateio por Marmita': 4.00,
            'Descrição': 'Base: 500 marmitas/mês'
        },
        {
            'Categoria': 'TOTAL',
            'Item': '',
            'Custo Mensal (R$)': 3090.00,
            'Rateio por Marmita': 6.18,
            'Descrição': 'Base: 500 marmitas/mês'
        }
    ]
    
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, sheet_name='Custos_Fixos', index=False)
    buffer.seek(0)
    return buffer.getvalue()

def show_admin_page():
    """Página principal de administração"""
    
    # Verificar autenticação
    if 'user' not in st.session_state:
        st.error("🔐 Acesso restrito. Faça login primeiro.")
        return
    
    user_email = st.session_state.user.get('email', '')
    
    # Verificar permissões de admin
    if not is_admin(user_email):
        st.error("🚫 Acesso negado. Você não tem permissões de administrador.")
        st.info(f"👤 Usuário atual: {user_email}")
        return
    
    # Interface de administração
    st.title("👑 Painel de Administração")
    st.success(f"🔓 Acesso autorizado: {user_email}")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Templates", 
        "📤 Upload Dados", 
        "👥 Usuários", 
        "📊 Estatísticas"
    ])
    
    with tab1:
        show_templates_section()
    
    with tab2:
        show_upload_section()
    
    with tab3:
        show_users_section()
    
    with tab4:
        show_stats_section()

def show_templates_section():
    """Seção de download de templates"""
    
    st.header("📥 Templates Excel")
    st.info("💡 Baixe os templates para facilitar o upload de dados em lote")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🥕 Ingredientes")
        st.markdown("""
        **Template para:**
        - Nome e categoria
        - Preços atualizados
        - Informações nutricionais
        - Unidades de medida
        """)
        
        # Botão de download
        ingredientes_data = generate_ingredientes_template()
        st.download_button(
            label="📥 Download Template Ingredientes",
            data=ingredientes_data,
            file_name=f"ingredientes_template_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.subheader("📦 Embalagens")
        st.markdown("""
        **Template para:**
        - Tipos de embalagens
        - Preços unitários
        - Capacidades
        - Categorias
        """)
        
        # Botão de download
        embalagens_data = generate_embalagens_template()
        st.download_button(
            label="📥 Download Template Embalagens",
            data=embalagens_data,
            file_name=f"embalagens_template_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        st.subheader("🏠 Custos Fixos")
        st.markdown("""
        **Template para:**
        - Energia, gás, água
        - Aluguel e mão de obra
        - Rateio por marmita
        - Cálculo automático
        """)
        
        # Botão de download
        custos_data = generate_custos_fixos_template()
        st.download_button(
            label="📥 Download Template Custos",
            data=custos_data,
            file_name=f"custos_fixos_template_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # Instruções de uso
    st.markdown("---")
    st.subheader("📋 Como usar os templates:")
    
    with st.expander("📖 Instruções detalhadas"):
        st.markdown("""
        ### 🎯 Passo a passo:
        
        1. **📥 Baixe** o template desejado
        2. **✏️ Preencha** os dados no Excel
        3. **💾 Salve** o arquivo
        4. **📤 Upload** na aba "Upload Dados"
        5. **✅ Confirme** a importação
        
        ### ⚠️ Regras importantes:
        
        - **Não altere** os nomes das colunas
        - **Mantenha** os tipos de dados (texto, número, verdadeiro/falso)
        - **Use pontos** para decimais (ex: 18.90)
        - **Ative/Desative** com TRUE/FALSE
        - **Teste primeiro** com poucos registros
        
        ### 🔄 Frequência de atualização:
        
        - **Ingredientes:** Mensal (preços de mercado)
        - **Embalagens:** Trimestral (novos fornecedores)
        - **Custos Fixos:** Conforme necessário
        """)

def show_upload_section():
    """Seção de upload de dados"""
    
    st.header("📤 Upload de Dados")
    st.warning("🚧 Funcionalidade em desenvolvimento")
    
    # Placeholder para futura implementação
    st.info("""
    **Próximas funcionalidades:**
    - Upload de planilhas Excel
    - Validação automática de dados
    - Preview antes da importação
    - Log de alterações
    """)

def show_users_section():
    """Seção de gerenciamento de usuários"""
    
    st.header("👥 Gerenciamento de Usuários")
    st.warning("🚧 Funcionalidade em desenvolvimento")
    
    # Mock data para demonstração
    st.subheader("📊 Resumo de Usuários")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Usuários", "1.247")
    
    with col2:
        st.metric("💎 Assinantes Ativos", "1.189", "12 novos")
    
    with col3:
        st.metric("💰 Receita Mensal", "R$ 2.958", "4.2%")
    
    with col4:
        st.metric("📈 Taxa Conversão", "95.3%", "2.1%")

def show_stats_section():
    """Seção de estatísticas do sistema"""
    
    st.header("📊 Estatísticas do Sistema")
    st.warning("🚧 Funcionalidade em desenvolvimento")
    
    # Mock data para demonstração
    st.subheader("📈 Métricas de Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🍽️ Receitas Criadas", "15.632")
        st.metric("🏭 Produções Planejadas", "8.947")
        st.metric("🛒 Listas Geradas", "12.458")
    
    with col2:
        st.metric("📄 PDFs Baixados", "9.234")
        st.metric("💡 Sugestões de Preço", "24.789")
        st.metric("⚡ Uptime Sistema", "99.7%")

# Função para incluir no menu principal
def show_admin_menu_item():
    """Mostra item de menu admin se usuário for administrador"""
    
    if 'user' in st.session_state:
        user_email = st.session_state.user.get('email', '')
        
        if is_admin(user_email):
            return True
    
    return False