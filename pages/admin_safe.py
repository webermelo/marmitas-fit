# -*- coding: utf-8 -*-
"""
Página de Administração - Versão Segura (Sem openpyxl)
Painel para gerenciar ingredientes, embalagens e usuários
"""

import streamlit as st
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

def show_admin_page():
    """Página principal de administração - Versão Segura"""
    
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
    tab1, tab2 = st.tabs(["📥 Templates", "📊 Estatísticas"])
    
    with tab1:
        show_templates_safe()
    
    with tab2:
        show_stats_safe()

def show_templates_safe():
    """Seção de templates - versão segura"""
    
    st.header("📥 Templates CSV")
    st.info("💡 Baixe os templates para facilitar o preenchimento de dados")
    
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
        
        csv_ingredientes = """Nome,Categoria,Preco,Unid_Receita,Unid_Compra,Kcal_Unid,Fator_Conv,Ativo,Observacoes
Frango peito,Proteina Animal,18.90,g,kg,1.65,1000,TRUE,Sem pele congelado
Arroz integral,Carboidrato,8.90,g,kg,1.11,1000,TRUE,Grao longo tipo 1
Brocolis,Vegetal,6.50,g,kg,0.34,1000,TRUE,Fresco preco medio
Azeite extra virgem,Gordura,12.00,ml,L,8.84,1000,TRUE,Primeira prensagem
Sal refinado,Tempero,1.20,g,kg,0.00,1000,TRUE,Iodado"""
        
        st.download_button(
            label="📥 Download Ingredientes (CSV)",
            data=csv_ingredientes.encode('utf-8-sig'),
            file_name=f"ingredientes_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
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
        
        csv_embalagens = """Nome,Tipo,Preco,Capacidade_ml,Categoria,Ativo,Descricao
Marmita 500ml,descartavel,0.50,500,principal,TRUE,PP transparente com tampa
Marmita 750ml,descartavel,0.65,750,principal,TRUE,PP transparente com tampa
Marmita 1000ml,descartavel,0.80,1000,principal,TRUE,PP transparente com tampa
Pote sobremesa 150ml,descartavel,0.25,150,complemento,TRUE,Para doces e frutas
Talher plastico,utensilio,0.08,0,utensilio,TRUE,Garfo + faca + colher
Guardanapo,higiene,0.05,0,higiene,TRUE,Papel 20x20cm
Sacola plastica,transporte,0.12,0,transporte,TRUE,30x40cm alca camiseta"""
        
        st.download_button(
            label="📥 Download Embalagens (CSV)",
            data=csv_embalagens.encode('utf-8-sig'),
            file_name=f"embalagens_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
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
        
        csv_custos = """Categoria,Item,Custo_Mensal,Rateio_por_Marmita,Descricao
Energia,Conta de luz,150.00,0.30,Fogao geladeira freezer
Gas,Botijao 13kg,80.00,0.16,Consumo medio mensal
Agua,Conta de agua,60.00,0.12,Limpeza e preparo
Aluguel,Espaco cozinha,800.00,1.60,Proporcional ao uso
Mao de obra,Salario proprio,2000.00,4.00,Base 500 marmitas por mes
TOTAL,,3090.00,6.18,Base 500 marmitas por mes"""
        
        st.download_button(
            label="📥 Download Custos (CSV)",
            data=csv_custos.encode('utf-8-sig'),
            file_name=f"custos_fixos_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Instruções de uso
    st.markdown("---")
    st.subheader("📋 Como usar os templates:")
    
    with st.expander("📖 Instruções detalhadas"):
        st.markdown("""
        ### 🎯 Passo a passo:
        
        1. **📥 Baixe** o template desejado (formato CSV)
        2. **📝 Abra** no Excel ou Google Sheets
        3. **✏️ Preencha** os dados nas colunas
        4. **💾 Salve** como CSV
        5. **📤 Contate** o administrador para fazer upload
        6. **✅ Confirme** a importação
        
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

def show_stats_safe():
    """Seção de estatísticas - versão segura"""
    
    st.header("📊 Estatísticas do Sistema")
    
    # Mock data para demonstração
    st.subheader("📈 Métricas de Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("👥 Total Usuários", "1.247", "12 novos")
        st.metric("💎 Assinantes Ativos", "1.189", "4.2%")
        st.metric("🍽️ Receitas Criadas", "15.632")
        st.metric("🏭 Produções Planejadas", "8.947")
    
    with col2:
        st.metric("💰 Receita Mensal", "R$ 2.958", "4.2%")
        st.metric("📈 Taxa Conversão", "95.3%", "2.1%")
        st.metric("🛒 Listas Geradas", "12.458")
        st.metric("📄 PDFs Baixados", "9.234")
    
    # Resumo do modelo de negócio
    st.markdown("---")
    st.subheader("💼 Modelo de Negócio")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **💰 Preço:**
        R$ 29,90/ano
        
        **🎯 Meta:**
        200k usuários
        
        **📈 Margem:**
        40% nos preços
        """)
    
    with col2:
        st.success("""
        **💵 Projeção:**
        R$ 5.98M/ano
        
        **👥 Conversão:**
        95% dos usuários
        
        **🔄 Renovação:**
        Anual automática
        """)
    
    with col3:
        st.warning("""
        **📊 Atualizações:**
        Preços mensais
        
        **🎁 Diferencial:**
        Sem versão gratuita
        
        **⚡ Foco:**
        Empreendedores sérios
        """)

# Função para incluir no menu principal
def show_admin_menu_item():
    """Mostra item de menu admin se usuário for administrador"""
    
    if 'user' in st.session_state:
        user_email = st.session_state.user.get('email', '')
        
        if is_admin(user_email):
            return True
    
    return False