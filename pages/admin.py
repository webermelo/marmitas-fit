# -*- coding: utf-8 -*-
"""
Página de Administração - Marmitas Fit
Painel para gerenciar ingredientes, embalagens e usuários
"""

import streamlit as st
import pandas as pd
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

# Funções para gerar templates CSV (mais compatível)
def generate_ingredientes_template():
    """Gera template CSV de ingredientes"""
    csv_content = """Nome,Categoria,Preco,Unid_Receita,Unid_Compra,Kcal_Unid,Fator_Conv,Ativo,Observacoes
Frango peito,Proteina Animal,18.90,g,kg,1.65,1000,TRUE,Sem pele congelado
Arroz integral,Carboidrato,8.90,g,kg,1.11,1000,TRUE,Grao longo tipo 1
Brocolis,Vegetal,6.50,g,kg,0.34,1000,TRUE,Fresco preco medio
Azeite extra virgem,Gordura,12.00,ml,L,8.84,1000,TRUE,Primeira prensagem
Sal refinado,Tempero,1.20,g,kg,0.00,1000,TRUE,Iodado"""
    
    return csv_content.encode('utf-8-sig')

def generate_embalagens_template():
    """Gera template CSV de embalagens"""
    csv_content = """Nome,Tipo,Preco,Capacidade_ml,Categoria,Ativo,Descricao
Marmita 500ml,descartavel,0.50,500,principal,TRUE,PP transparente com tampa
Marmita 750ml,descartavel,0.65,750,principal,TRUE,PP transparente com tampa
Marmita 1000ml,descartavel,0.80,1000,principal,TRUE,PP transparente com tampa
Pote sobremesa 150ml,descartavel,0.25,150,complemento,TRUE,Para doces e frutas
Talher plastico,utensilio,0.08,0,utensilio,TRUE,Garfo + faca + colher
Guardanapo,higiene,0.05,0,higiene,TRUE,Papel 20x20cm
Sacola plastica,transporte,0.12,0,transporte,TRUE,30x40cm alca camiseta"""
    
    return csv_content.encode('utf-8-sig')

def generate_custos_fixos_template():
    """Gera template CSV de custos fixos"""
    csv_content = """Categoria,Item,Custo_Mensal,Rateio_por_Marmita,Descricao
Energia,Conta de luz,150.00,0.30,Fogao geladeira freezer
Gas,Botijao 13kg,80.00,0.16,Consumo medio mensal
Agua,Conta de agua,60.00,0.12,Limpeza e preparo
Aluguel,Espaco cozinha,800.00,1.60,Proporcional ao uso
Mao de obra,Salario proprio,2000.00,4.00,Base 500 marmitas por mes
TOTAL,,3090.00,6.18,Base 500 marmitas por mes"""
    
    return csv_content.encode('utf-8-sig')

def show_admin_page():
    """Página principal de administração"""
    
    try:
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
    
    except Exception as e:
        st.error(f"🚫 Erro no painel admin: {str(e)}")
        st.info("📋 **Versão simplificada ativada**")
        
        # Interface simples de fallback
        st.title("👑 Admin - Modo Básico")
        
        # Templates básicos
        st.subheader("📥 Downloads")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_ing = """Nome,Categoria,Preco,Unid_Receita,Unid_Compra,Kcal_Unid,Fator_Conv,Ativo,Observacoes
Frango peito,Proteina Animal,18.90,g,kg,1.65,1000,TRUE,Sem pele congelado"""
            
            st.download_button(
                "📥 Template Ingredientes",
                csv_ing.encode('utf-8-sig'),
                f"ingredientes_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        with col2:
            csv_emb = """Nome,Tipo,Preco,Capacidade_ml,Categoria,Ativo,Descricao
Marmita 500ml,descartavel,0.50,500,principal,TRUE,PP transparente com tampa"""
            
            st.download_button(
                "📥 Template Embalagens",
                csv_emb.encode('utf-8-sig'),
                f"embalagens_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

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
            label="📥 Download Template Ingredientes (CSV)",
            data=ingredientes_data,
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
        
        # Botão de download
        embalagens_data = generate_embalagens_template()
        st.download_button(
            label="📥 Download Template Embalagens (CSV)",
            data=embalagens_data,
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
        
        # Botão de download
        custos_data = generate_custos_fixos_template()
        st.download_button(
            label="📥 Download Template Custos (CSV)",
            data=custos_data,
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
        4. **💾 Salve** como CSV ou Excel
        5. **📤 Upload** na aba "Upload Dados"
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

def show_upload_section():
    """Seção de upload de dados"""
    
    st.header("📤 Upload de Dados")
    st.info("📋 Faça upload dos templates CSV preenchidos para popular o banco de dados")
    
    # Tabs para diferentes tipos de upload
    tab1, tab2, tab3 = st.tabs(["🥕 Ingredientes", "📦 Embalagens", "🏠 Custos Fixos"])
    
    with tab1:
        upload_ingredientes()
    
    with tab2:
        upload_embalagens()
    
    with tab3:
        upload_custos_fixos()

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

def upload_ingredientes():
    """Upload de ingredientes CSV"""
    
    st.subheader("🥕 Upload Ingredientes")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de ingredientes",
        type=['csv'],
        key="ingredientes_upload"
    )
    
    if uploaded_file is not None:
        try:
            # Ler CSV com encoding correto (forçar engine CSV puro)
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Validar colunas obrigatórias
            required_columns = ['Nome', 'Categoria', 'Preco', 'Unid_Receita', 'Unid_Compra', 'Kcal_Unid', 'Fator_Conv', 'Ativo']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                return
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Ingredientes", key="confirm_ingredientes"):
                success_count = upload_to_firebase_ingredientes(df)
                if success_count > 0:
                    st.success(f"🎉 {success_count} ingredientes salvos com sucesso!")
                else:
                    st.error("❌ Erro ao salvar ingredientes")
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def upload_embalagens():
    """Upload de embalagens CSV"""
    
    st.subheader("📦 Upload Embalagens")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de embalagens",
        type=['csv'],
        key="embalagens_upload"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Validar colunas obrigatórias
            required_columns = ['Nome', 'Tipo', 'Preco', 'Capacidade_ml', 'Categoria', 'Ativo']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                return
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Embalagens", key="confirm_embalagens"):
                success_count = upload_to_firebase_embalagens(df)
                if success_count > 0:
                    st.success(f"🎉 {success_count} embalagens salvas com sucesso!")
                else:
                    st.error("❌ Erro ao salvar embalagens")
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def upload_custos_fixos():
    """Upload de custos fixos CSV"""
    
    st.subheader("🏠 Upload Custos Fixos")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de custos fixos",
        type=['csv'],
        key="custos_upload"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Validar colunas obrigatórias
            required_columns = ['Categoria', 'Item', 'Custo_Mensal', 'Rateio_por_Marmita']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                return
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Custos Fixos", key="confirm_custos"):
                success_count = upload_to_firebase_custos(df)
                if success_count > 0:
                    st.success(f"🎉 {success_count} custos fixos salvos com sucesso!")
                else:
                    st.error("❌ Erro ao salvar custos fixos")
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def upload_to_firebase_ingredientes(df):
    """Salva ingredientes no Firestore"""
    try:
        from utils.firestore_client import get_firestore_client
        
        db = get_firestore_client()
        if not db:
            st.error("Erro ao conectar com o banco de dados")
            return 0
        
        success_count = 0
        
        for _, row in df.iterrows():
            # Converter para dict e limpar valores NaN
            ingredient_data = {
                'nome': str(row['Nome']).strip(),
                'categoria': str(row['Categoria']).strip(),
                'preco': float(row['Preco']),
                'unid_receita': str(row['Unid_Receita']).strip(),
                'unid_compra': str(row['Unid_Compra']).strip(),
                'kcal_unid': float(row['Kcal_Unid']),
                'fator_conv': float(row['Fator_Conv']),
                'ativo': str(row['Ativo']).upper() == 'TRUE',
                'observacoes': str(row.get('Observacoes', '')).strip(),
                'updated_at': pd.Timestamp.now().isoformat()
            }
            
            # Salvar no Firestore (coleção global de ingredientes)
            try:
                db.collection('ingredientes_master').add(ingredient_data)
                success_count += 1
            except Exception as e:
                st.warning(f"Erro ao salvar {ingredient_data['nome']}: {str(e)}")
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro geral no upload: {str(e)}")
        return 0

def upload_to_firebase_embalagens(df):
    """Salva embalagens no Firestore"""
    try:
        from utils.firestore_client import get_firestore_client
        
        db = get_firestore_client()
        if not db:
            return 0
        
        success_count = 0
        
        for _, row in df.iterrows():
            embalagem_data = {
                'nome': str(row['Nome']).strip(),
                'tipo': str(row['Tipo']).strip(),
                'preco': float(row['Preco']),
                'capacidade_ml': int(row['Capacidade_ml']) if row['Capacidade_ml'] != 0 else 0,
                'categoria': str(row['Categoria']).strip(),
                'ativo': str(row['Ativo']).upper() == 'TRUE',
                'descricao': str(row.get('Descricao', '')).strip(),
                'updated_at': pd.Timestamp.now().isoformat()
            }
            
            try:
                db.collection('embalagens_master').add(embalagem_data)
                success_count += 1
            except Exception as e:
                st.warning(f"Erro ao salvar {embalagem_data['nome']}: {str(e)}")
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro geral no upload: {str(e)}")
        return 0

def upload_to_firebase_custos(df):
    """Salva custos fixos no Firestore"""
    try:
        from utils.firestore_client import get_firestore_client
        
        db = get_firestore_client()
        if not db:
            return 0
        
        success_count = 0
        
        for _, row in df.iterrows():
            custo_data = {
                'categoria': str(row['Categoria']).strip(),
                'item': str(row['Item']).strip(),
                'custo_mensal': float(row['Custo_Mensal']),
                'rateio_por_marmita': float(row['Rateio_por_Marmita']),
                'descricao': str(row.get('Descricao', '')).strip(),
                'updated_at': pd.Timestamp.now().isoformat()
            }
            
            try:
                db.collection('custos_fixos_master').add(custo_data)
                success_count += 1
            except Exception as e:
                st.warning(f"Erro ao salvar {custo_data['categoria']}: {str(e)}")
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro geral no upload: {str(e)}")
        return 0

# Função para incluir no menu principal
def show_admin_menu_item():
    """Mostra item de menu admin se usuário for administrador"""
    
    if 'user' in st.session_state:
        user_email = st.session_state.user.get('email', '')
        
        if is_admin(user_email):
            return True
    
    return False