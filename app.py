# -*- coding: utf-8 -*-
"""
Marmitas Fit - Sistema Web Multi-usuário CORRIGIDO
Versão sem problemas de cache
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração da página
st.set_page_config(
    page_title="Marmitas Fit - Web (Corrigido)",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Firebase usando REST API (sem pyrebase4)
try:
    from utils.firebase_auth import get_firebase_auth
    firebase_auth = get_firebase_auth()
    FIREBASE_AVAILABLE = firebase_auth is not None
except Exception as e:
    FIREBASE_AVAILABLE = False
    st.error(f"⚠️ Erro Firebase: {e}")

def check_auth():
    """Verificação de autenticação com Firebase ou modo demo"""
    
    # Verificar se usuário já está logado (Firebase ou demo)
    if 'user' in st.session_state:
        return True
    
    # Se Firebase não disponível, mostrar opção de usar modo demo
    if not FIREBASE_AVAILABLE:
        return show_simple_auth()
    
    # Interface de login com Firebase
    return show_login_page()

def show_login_page():
    """Exibe página de login com Firebase"""
    st.title("🔐 Login - Marmitas Fit")
    
    # Abas de Login e Registro
    tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Registrar"])
    
    with tab1:
        st.subheader("Entrar na sua conta")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔒 Senha", type="password")
            
            if st.form_submit_button("🔑 Entrar", use_container_width=True):
                if email and password:
                    if firebase_auth:
                        # Fazer login com Firebase REST API
                        result = firebase_auth.sign_in_with_email_password(email, password)
                        
                        if result["success"]:
                            user_data = result["user"]
                            
                            # Salvar dados do usuário na sessão
                            st.session_state.user = {
                                "email": user_data["email"],
                                "uid": user_data["uid"],
                                "display_name": user_data["display_name"]
                            }
                            st.session_state.firebase_token = user_data["token"]
                            st.session_state.firebase_refresh_token = user_data["refresh_token"]
                            
                            st.success("✅ Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                    else:
                        st.error("❌ Firebase não disponível.")
                else:
                    st.error("❌ Preencha email e senha.")
    
    with tab2:
        st.subheader("Criar nova conta")
        
        with st.form("register_form"):
            nome = st.text_input("👤 Nome completo")
            email_reg = st.text_input("📧 Email", placeholder="seu@email.com", key="reg_email")
            password_reg = st.text_input("🔒 Senha", type="password", key="reg_password", help="Mínimo 6 caracteres")
            password_confirm = st.text_input("🔒 Confirmar senha", type="password")
            
            if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                if nome and email_reg and password_reg and password_confirm:
                    if password_reg != password_confirm:
                        st.error("❌ As senhas não conferem.")
                    elif len(password_reg) < 6:
                        st.error("❌ A senha deve ter pelo menos 6 caracteres.")
                    else:
                        if firebase_auth:
                            # Criar usuário no Firebase
                            result = firebase_auth.sign_up_with_email_password(email_reg, password_reg, nome)
                            
                            if result["success"]:
                                user_data = result["user"]
                                
                                # Salvar dados do usuário na sessão
                                st.session_state.user = {
                                    "email": user_data["email"],
                                    "uid": user_data["uid"],
                                    "display_name": user_data["display_name"]
                                }
                                st.session_state.firebase_token = user_data["token"]
                                st.session_state.firebase_refresh_token = user_data["refresh_token"]
                                
                                st.success("✅ Conta criada com sucesso!")
                                st.rerun()
                            else:
                                st.error(f"❌ {result['error']}")
                        else:
                            st.error("❌ Firebase não disponível.")
                else:
                    st.error("❌ Preencha todos os campos.")
    
    # Modo demo
    st.markdown("---")
    st.info("💡 **Modo Demonstração**: Clique abaixo para testar sem criar conta")
    
    if st.button("🎮 Usar Modo Demo", use_container_width=True):
        st.session_state.user = {
            "email": "demo@marmitasfit.com",
            "uid": "demo_user",
            "display_name": "Usuário Demo"
        }
        st.success("✅ Modo demo ativado!")
        st.rerun()
    
    return False

def show_simple_auth():
    """Autenticação simplificada quando Firebase não está disponível"""
    st.title("🥗 Marmitas Fit - Sistema Web")
    
    st.info("🔧 **Firebase não configurado** - O sistema funcionará em modo demonstração")
    
    st.markdown("""
    ### 🎮 Modo Demonstração
    
    **O que você pode fazer:**
    - ✅ Cadastrar ingredientes
    - ✅ Criar receitas completas
    - ✅ Planejar produção
    - ✅ Gerar listas de compras
    - ✅ Baixar PDFs
    - ✅ Ver histórico de produções
    
    **Limitações:**
    - ⚠️ Dados salvos apenas na sessão do navegador
    - ⚠️ Dados perdidos ao fechar o navegador
    - ⚠️ Sem multi-usuário real
    
    **Para usar Firebase:**
    Configure as credenciais corretas no arquivo `config/firebase_config.py`
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎮 Continuar em Modo Demo", use_container_width=True):
            st.session_state.user = {
                "email": "demo@marmitasfit.com",
                "uid": "demo_user",
                "display_name": "Usuário Demo"
            }
            st.success("✅ Modo demo ativado!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Tentar Reconectar Firebase", use_container_width=True):
            # Limpar cache e tentar novamente
            if 'firebase_manager' in st.session_state:
                del st.session_state['firebase_manager']
            st.rerun()
    
    return False

# Inicializar dados demo
def init_demo_data():
    if 'demo_ingredients' not in st.session_state:
        st.session_state.demo_ingredients = [
            {'Nome': 'Frango (peito)', 'Categoria': 'Proteína Animal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 18.9, 'Kcal_Por_Unidade_Receita': 1.65, 'Fator_Conversao': 1000},
            {'Nome': 'Arroz integral', 'Categoria': 'Carboidrato', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 1.11, 'Fator_Conversao': 1000},
            {'Nome': 'Brócolis', 'Categoria': 'Vegetal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 0.34, 'Fator_Conversao': 1000},
        ]
    
    if 'demo_recipes' not in st.session_state:
        st.session_state.demo_recipes = []

def main():
    """Função principal da aplicação"""
    
    # Verificar autenticação
    if not check_auth():
        return
    
    # Inicializar dados
    init_demo_data()
    
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.success(f"👤 {user['display_name']}")
        st.caption(f"📧 {user['email']}")
        
        # Status da conexão
        if FIREBASE_AVAILABLE and 'firebase_token' in st.session_state:
            st.success("🔗 Firebase conectado")
        else:
            st.warning("🎮 Modo demonstração")
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True):
            # Limpar dados da sessão
            for key in ['user', 'firebase_token', 'demo_ingredients', 'demo_recipes', 'current_production', 'production_history']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        menu_options = ["🏠 Dashboard", "🥕 Ingredientes", "📝 Receitas", "🏭 Produção"]
        
        # Adicionar menu admin se usuário for administrador
        from pages.admin import show_admin_menu_item
        if show_admin_menu_item():
            menu_options.append("👑 Administração")
        
        selected_page = st.radio("Navegação:", menu_options)
    
    # Header principal
    st.title("🥗 Marmitas Fit - Web App (Versão Corrigida)")
    
    # Roteamento de páginas
    if selected_page == "🏠 Dashboard":
        show_dashboard()
    elif selected_page == "🥕 Ingredientes":
        show_ingredientes()
    elif selected_page == "📝 Receitas":
        show_receitas()
    elif selected_page == "🏭 Produção":
        show_producao()
    elif selected_page == "👑 Administração":
        # Temporariamente desabilitado devido a problemas de cache
        st.error("🚧 **Painel Admin em Manutenção**")
        st.info("""
        **Problema temporário**: O Streamlit Cloud está com cache de arquivos antigos.
        
        **Solução**: Aguarde algumas horas para o cache limpar automaticamente.
        
        **Alternativa**: Acesse os templates diretamente:
        """)
        
        # Templates diretamente aqui como alternativa
        st.subheader("📥 Templates CSV (Alternativa Temporária)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🥕 Ingredientes**")
            csv_ingredientes = """Nome,Categoria,Preço (R$),Unid.Receita,Unid.Compra,Kcal/Unid,Fator Conv.,Ativo,Observações
Frango (peito),Proteína Animal,18.90,g,kg,1.65,1000,TRUE,Sem pele congelado
Arroz integral,Carboidrato,8.90,g,kg,1.11,1000,TRUE,Grão longo tipo 1
Brócolis,Vegetal,6.50,g,kg,0.34,1000,TRUE,Fresco preço médio
Azeite extra virgem,Gordura,12.00,ml,L,8.84,1000,TRUE,Primeira prensagem
Sal refinado,Tempero,1.20,g,kg,0.00,1000,TRUE,Iodado"""
            
            st.download_button(
                "📥 Download Ingredientes",
                csv_ingredientes.encode('utf-8'),
                f"ingredientes_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            st.write("**📦 Embalagens**")
            csv_embalagens = """Nome,Tipo,Preço (R$),Capacidade (ml),Categoria,Ativo,Descrição
Marmita 500ml,descartavel,0.50,500,principal,TRUE,PP transparente com tampa
Marmita 750ml,descartavel,0.65,750,principal,TRUE,PP transparente com tampa
Marmita 1000ml,descartavel,0.80,1000,principal,TRUE,PP transparente com tampa
Pote sobremesa 150ml,descartavel,0.25,150,complemento,TRUE,Para doces e frutas
Talher plástico,utensilio,0.08,0,utensilio,TRUE,Garfo + faca + colher
Guardanapo,higiene,0.05,0,higiene,TRUE,Papel 20x20cm
Sacola plástica,transporte,0.12,0,transporte,TRUE,30x40cm alça camiseta"""
            
            st.download_button(
                "📥 Download Embalagens",
                csv_embalagens.encode('utf-8'),
                f"embalagens_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col3:
            st.write("**🏠 Custos Fixos**")
            csv_custos = """Categoria,Item,Custo Mensal (R$),Rateio por Marmita,Descrição
Energia,Conta de luz,150.00,0.30,Fogão geladeira freezer
Gás,Botijão 13kg,80.00,0.16,Consumo médio mensal
Água,Conta de água,60.00,0.12,Limpeza e preparo
Aluguel,Espaço cozinha,800.00,1.60,Proporcional ao uso
Mão de obra,Salário próprio,2000.00,4.00,Base: 500 marmitas/mês
TOTAL,,3090.00,6.18,Base: 500 marmitas/mês"""
            
            st.download_button(
                "📥 Download Custos Fixos",
                csv_custos.encode('utf-8'),
                f"custos_fixos_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )

def show_dashboard():
    """Dashboard principal"""
    st.header("🏠 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🥕 Ingredientes", len(st.session_state.demo_ingredients))
    
    with col2:
        receitas_count = len(set([r['nome_receita'] for r in st.session_state.demo_recipes]))
        st.metric("📝 Receitas", receitas_count)
    
    with col3:
        st.metric("🔄 Status", "Online")
    
    st.info("💡 Sistema funcionando em modo demonstração. Dados são salvos na sessão do navegador.")

def show_ingredientes():
    """Página de ingredientes"""
    st.header("🥕 Gestão de Ingredientes")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Adicionar"])
    
    with tab1:
        st.subheader("📋 Ingredientes Cadastrados")
        
        if st.session_state.demo_ingredients:
            df_ingredients = pd.DataFrame(st.session_state.demo_ingredients)
            st.dataframe(df_ingredients, use_container_width=True)
        else:
            st.info("Nenhum ingrediente cadastrado.")
    
    with tab2:
        st.subheader("➕ Adicionar Ingrediente")
        
        with st.form("add_ingredient"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Ingrediente")
                categoria = st.selectbox("Categoria", ['Proteína Animal', 'Carboidrato', 'Vegetal', 'Tempero'])
                unidade_receita = st.selectbox("Unidade Receita", ['g', 'ml', 'unidade'])
            
            with col2:
                unidade_compra = st.selectbox("Unidade Compra", ['kg', 'L', 'unidade'])
                preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)
                kcal = st.number_input("Kcal por unidade", min_value=0.0, step=0.01)
            
            fator_conversao = st.number_input("Fator de Conversão", min_value=1, value=1000)
            
            if st.form_submit_button("💾 Salvar Ingrediente"):
                if nome and categoria:
                    novo_ingrediente = {
                        'Nome': nome,
                        'Categoria': categoria,
                        'Unidade_Receita': unidade_receita,
                        'Unidade_Compra': unidade_compra,
                        'Preco_Padrao': preco,
                        'Kcal_Por_Unidade_Receita': kcal,
                        'Fator_Conversao': fator_conversao
                    }
                    
                    st.session_state.demo_ingredients.append(novo_ingrediente)
                    st.success(f"✅ Ingrediente '{nome}' adicionado!")
                    st.rerun()
                else:
                    st.error("❌ Preencha pelo menos o nome e categoria!")

def show_receitas():
    """Página de receitas"""
    st.header("📝 Gestão de Receitas")
    
    tab1, tab2 = st.tabs(["📋 Minhas Receitas", "👨‍🍳 Criar Receita"])
    
    with tab1:
        st.subheader("📋 Suas Receitas")
        
        if st.session_state.demo_recipes:
            # Agrupar receitas por nome
            df_recipes = pd.DataFrame(st.session_state.demo_recipes)
            
            st.write(f"**Total de registros:** {len(df_recipes)}")
            
            if 'nome_receita' in df_recipes.columns:
                receitas_agrupadas = df_recipes.groupby('nome_receita').agg({
                    'custo_total': 'first',
                    'calorias_total': 'first',
                    'created_at': 'first'
                }).reset_index()
                
                st.write(f"**Receitas únicas:** {len(receitas_agrupadas)}")
                
                # Mostrar receitas
                for _, receita in receitas_agrupadas.iterrows():
                    with st.expander(f"🍽️ {receita['nome_receita']}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("💰 Custo", f"R$ {receita['custo_total']:.2f}")
                        
                        with col2:
                            st.metric("🔥 Calorias", f"{receita['calorias_total']:.0f} kcal")
                        
                        # Mostrar ingredientes da receita
                        ingredientes_receita = df_recipes[df_recipes['nome_receita'] == receita['nome_receita']]
                        
                        st.write("**Ingredientes:**")
                        for _, ing in ingredientes_receita.iterrows():
                            st.write(f"• {ing['ingrediente']}: {ing['quantidade']} {ing['unidade']}")
            
            # Debug info
            with st.expander("🔍 Debug Info"):
                st.write("**Dados brutos:**")
                st.dataframe(df_recipes)
        else:
            st.info("Nenhuma receita cadastrada ainda. Use a aba 'Criar Receita' para adicionar receitas.")
    
    with tab2:
        st.subheader("👨‍🍳 Criar Nova Receita")
        
        # Nome da receita
        nome_receita = st.text_input("📛 Nome da Receita", placeholder="Ex: Frango Grelhado com Arroz")
        
        # Ingredientes disponíveis
        if st.session_state.demo_ingredients:
            ingredientes_disponiveis = [ing['Nome'] for ing in st.session_state.demo_ingredients]
            
            # Lista de ingredientes da receita
            if 'recipe_ingredients' not in st.session_state:
                st.session_state.recipe_ingredients = []
            
            # Adicionar ingrediente
            with st.form("add_ingredient_to_recipe"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    ingrediente_selecionado = st.selectbox("Ingrediente", ingredientes_disponiveis)
                
                with col2:
                    quantidade = st.number_input("Quantidade", min_value=0.1, step=0.1)
                
                with col3:
                    # Buscar unidade do ingrediente
                    unidade = 'g'  # padrão
                    for ing in st.session_state.demo_ingredients:
                        if ing['Nome'] == ingrediente_selecionado:
                            unidade = ing['Unidade_Receita']
                            break
                    st.text_input("Unidade", value=unidade, disabled=True)
                
                if st.form_submit_button("➕ Adicionar Ingrediente"):
                    if ingrediente_selecionado and quantidade > 0:
                        # Verificar se já foi adicionado
                        ja_adicionado = any(ing['nome'] == ingrediente_selecionado for ing in st.session_state.recipe_ingredients)
                        
                        if not ja_adicionado:
                            # Buscar dados do ingrediente
                            ing_data = None
                            for ing in st.session_state.demo_ingredients:
                                if ing['Nome'] == ingrediente_selecionado:
                                    ing_data = ing
                                    break
                            
                            if ing_data:
                                custo_unitario = ing_data['Preco_Padrao'] / ing_data['Fator_Conversao']
                                kcal_unitario = ing_data['Kcal_Por_Unidade_Receita']
                                
                                st.session_state.recipe_ingredients.append({
                                    'nome': ingrediente_selecionado,
                                    'quantidade': quantidade,
                                    'unidade': unidade,
                                    'custo_unitario': custo_unitario,
                                    'kcal_unitario': kcal_unitario
                                })
                                
                                st.success(f"✅ {ingrediente_selecionado} adicionado!")
                                st.rerun()
                        else:
                            st.error("❌ Ingrediente já adicionado!")
            
            # Mostrar ingredientes adicionados
            if st.session_state.recipe_ingredients:
                st.markdown("**Ingredientes da Receita:**")
                
                custo_total = 0
                calorias_total = 0
                
                for i, ing in enumerate(st.session_state.recipe_ingredients):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    custo_ingrediente = ing['quantidade'] * ing['custo_unitario']
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
                
                # Totais
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Custo Total", f"R$ {custo_total:.2f}")
                with col2:
                    st.metric("🔥 Calorias Totais", f"{calorias_total:.0f} kcal")
                
                # Salvar receita
                if st.button("💾 Salvar Receita", use_container_width=True):
                    if nome_receita and st.session_state.recipe_ingredients:
                        
                        # Salvar cada ingrediente como um registro
                        for ingrediente in st.session_state.recipe_ingredients:
                            recipe_data = {
                                "nome_receita": nome_receita,
                                "ingrediente": ingrediente['nome'],
                                "quantidade": ingrediente['quantidade'],
                                "unidade": ingrediente['unidade'],
                                "custo_unitario": ingrediente['custo_unitario'],
                                "custo_total": custo_total,
                                "calorias_unitario": ingrediente['kcal_unitario'],
                                "calorias_total": calorias_total,
                                "created_at": datetime.now()
                            }
                            
                            st.session_state.demo_recipes.append(recipe_data)
                        
                        st.success(f"✅ Receita '{nome_receita}' salva com {len(st.session_state.recipe_ingredients)} ingredientes!")
                        st.session_state.recipe_ingredients = []  # Limpar
                        st.rerun()
                    else:
                        st.error("❌ Preencha o nome da receita e adicione ingredientes!")
        
        else:
            st.warning("⚠️ Cadastre ingredientes primeiro!")

def show_producao():
    """Página de produção"""
    st.header("🏭 Planejamento de Produção")
    
    if not st.session_state.demo_recipes:
        st.warning("⚠️ Você precisa ter receitas cadastradas para fazer planejamento de produção!")
        st.info("💡 Vá para a seção 'Receitas' e crie algumas receitas primeiro.")
        return
    
    tab1, tab2 = st.tabs(["🎯 Planejar Produção", "📋 Histórico"])
    
    with tab1:
        st.subheader("🎯 Nova Produção")
        
        # Inicializar lista de produção na sessão
        if 'current_production' not in st.session_state:
            st.session_state.current_production = []
        
        # Obter receitas únicas
        df_recipes = pd.DataFrame(st.session_state.demo_recipes)
        receitas_disponiveis = df_recipes['nome_receita'].unique().tolist()
        
        # Seleção de receita e quantidade
        with st.form("add_to_production"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                receita_selecionada = st.selectbox("🍽️ Escolha a Receita", receitas_disponiveis)
            
            with col2:
                quantidade_marmitas = st.number_input("📦 Quantidade de Marmitas", min_value=1, value=10, step=1)
            
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)  # Espaço para alinhar
                
            if st.form_submit_button("➕ Adicionar à Produção"):
                if receita_selecionada and quantidade_marmitas > 0:
                    # Verificar se a receita já está na produção
                    ja_na_producao = any(item['receita'] == receita_selecionada for item in st.session_state.current_production)
                    
                    if not ja_na_producao:
                        # Obter custo e calorias da receita
                        receita_info = df_recipes[df_recipes['nome_receita'] == receita_selecionada].iloc[0]
                        
                        st.session_state.current_production.append({
                            'receita': receita_selecionada,
                            'quantidade': quantidade_marmitas,
                            'custo_unitario': receita_info['custo_total'],
                            'calorias_unitario': receita_info['calorias_total']
                        })
                        
                        st.success(f"✅ {quantidade_marmitas}x {receita_selecionada} adicionada à produção!")
                        st.rerun()
                    else:
                        st.error("❌ Esta receita já está na produção atual!")
        
        # Mostrar itens da produção atual
        if st.session_state.current_production:
            st.markdown("---")
            st.subheader("📦 Produção Atual")
            
            custo_total_producao = 0
            calorias_total_producao = 0
            
            for i, item in enumerate(st.session_state.current_production):
                custo_item = item['quantidade'] * item['custo_unitario']
                calorias_item = item['quantidade'] * item['calorias_unitario']
                
                custo_total_producao += custo_item
                calorias_total_producao += calorias_item
                
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"🍽️ **{item['receita']}**")
                
                with col2:
                    st.write(f"📦 {item['quantidade']} un")
                
                with col3:
                    st.write(f"💰 R$ {custo_item:.2f}")
                
                with col4:
                    st.write(f"🔥 {calorias_item:.0f} kcal")
                
                with col5:
                    if st.button("🗑️", key=f"remove_prod_{i}"):
                        st.session_state.current_production.pop(i)
                        st.rerun()
            
            # Totais da produção
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 Custo Total", f"R$ {custo_total_producao:.2f}")
            
            with col2:
                st.metric("🔥 Calorias Totais", f"{calorias_total_producao:.0f} kcal")
            
            with col3:
                total_marmitas = sum(item['quantidade'] for item in st.session_state.current_production)
                custo_por_marmita = custo_total_producao / total_marmitas if total_marmitas > 0 else 0
                st.metric("📊 Custo por Marmita", f"R$ {custo_por_marmita:.2f}")
            
            # Botões de ação
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🛒 Gerar Lista de Compras", use_container_width=True):
                    st.session_state.show_shopping_list = True
                    st.rerun()
            
            with col2:
                if st.button("💾 Salvar Produção", use_container_width=True):
                    # Salvar no histórico
                    if 'production_history' not in st.session_state:
                        st.session_state.production_history = []
                    
                    producao_data = {
                        'id': len(st.session_state.production_history) + 1,
                        'data': datetime.now(),
                        'itens': st.session_state.current_production.copy(),
                        'custo_total': custo_total_producao,
                        'calorias_total': calorias_total_producao,
                        'total_marmitas': total_marmitas
                    }
                    
                    st.session_state.production_history.append(producao_data)
                    st.session_state.current_production = []  # Limpar produção atual
                    
                    st.success(f"✅ Produção salva! {total_marmitas} marmitas - R$ {custo_total_producao:.2f}")
                    st.rerun()
            
            # Mostrar lista de compras se solicitada
            if hasattr(st.session_state, 'show_shopping_list') and st.session_state.show_shopping_list:
                show_shopping_list()
        
        else:
            st.info("📝 Adicione receitas à produção para começar o planejamento.")
    
    with tab2:
        st.subheader("📋 Histórico de Produções")
        
        if hasattr(st.session_state, 'production_history') and st.session_state.production_history:
            for producao in reversed(st.session_state.production_history):  # Mais recentes primeiro
                with st.expander(f"🏭 Produção #{producao['id']} - {producao['data'].strftime('%d/%m/%Y %H:%M')}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("💰 Custo Total", f"R$ {producao['custo_total']:.2f}")
                    
                    with col2:
                        st.metric("📦 Total Marmitas", producao['total_marmitas'])
                    
                    with col3:
                        custo_medio = producao['custo_total'] / producao['total_marmitas'] if producao['total_marmitas'] > 0 else 0
                        st.metric("📊 Custo Médio", f"R$ {custo_medio:.2f}")
                    
                    st.markdown("**Receitas produzidas:**")
                    for item in producao['itens']:
                        st.write(f"• {item['receita']}: {item['quantidade']} marmitas")
        else:
            st.info("📝 Nenhuma produção salva ainda.")

def show_shopping_list():
    """Gera e exibe a lista de compras consolidada"""
    st.markdown("---")
    st.subheader("🛒 Lista de Compras")
    
    if not st.session_state.current_production:
        return
    
    # Calcular ingredientes necessários
    ingredientes_necessarios = {}
    df_recipes = pd.DataFrame(st.session_state.demo_recipes)
    
    for item_producao in st.session_state.current_production:
        receita_nome = item_producao['receita']
        quantidade_marmitas = item_producao['quantidade']
        
        # Buscar ingredientes desta receita
        ingredientes_receita = df_recipes[df_recipes['nome_receita'] == receita_nome]
        
        for _, ingrediente in ingredientes_receita.iterrows():
            nome_ingrediente = ingrediente['ingrediente']
            quantidade_por_marmita = ingrediente['quantidade']
            unidade = ingrediente['unidade']
            
            quantidade_total = quantidade_por_marmita * quantidade_marmitas
            
            if nome_ingrediente in ingredientes_necessarios:
                ingredientes_necessarios[nome_ingrediente]['quantidade'] += quantidade_total
            else:
                # Buscar dados do ingrediente nos ingredientes cadastrados
                preco_kg = 0
                fator_conversao = 1000
                unidade_compra = 'kg'
                
                for ing_cadastrado in st.session_state.demo_ingredients:
                    if ing_cadastrado['Nome'] == nome_ingrediente:
                        preco_kg = ing_cadastrado['Preco_Padrao']
                        fator_conversao = ing_cadastrado['Fator_Conversao']
                        unidade_compra = ing_cadastrado['Unidade_Compra']
                        break
                
                ingredientes_necessarios[nome_ingrediente] = {
                    'quantidade': quantidade_total,
                    'unidade_receita': unidade,
                    'unidade_compra': unidade_compra,
                    'preco_unitario': preco_kg,
                    'fator_conversao': fator_conversao
                }
    
    # Exibir lista de compras
    if ingredientes_necessarios:
        st.markdown("**🛒 Ingredientes para comprar:**")
        
        custo_total_compras = 0
        
        # Criar tabela de compras
        compras_data = []
        
        for nome_ingrediente, dados in ingredientes_necessarios.items():
            quantidade_receita = dados['quantidade']
            quantidade_compra = quantidade_receita / dados['fator_conversao']
            custo_item = quantidade_compra * dados['preco_unitario']
            custo_total_compras += custo_item
            
            # Formatação especial para gramas (sem decimais)
            if dados['unidade_receita'].lower() == 'g':
                qtd_receita_str = f"{quantidade_receita:.0f} {dados['unidade_receita']}"
            else:
                qtd_receita_str = f"{quantidade_receita:.1f} {dados['unidade_receita']}"
            
            compras_data.append({
                'Ingrediente': nome_ingrediente,
                'Quantidade (receita)': qtd_receita_str,
                'Quantidade (compra)': f"{quantidade_compra:.2f} {dados['unidade_compra']}",
                'Preço Unit.': f"R$ {dados['preco_unitario']:.2f}",
                'Custo Total': f"R$ {custo_item:.2f}"
            })
        
        df_compras = pd.DataFrame(compras_data)
        st.dataframe(df_compras, use_container_width=True)
        
        st.metric("💰 Custo Total das Compras", f"R$ {custo_total_compras:.2f}")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            # Gerar PDF
            pdf_buffer = generate_shopping_list_pdf(compras_data, custo_total_compras, st.session_state.current_production)
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_buffer,
                file_name=f"lista_compras_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            if st.button("✅ Fechar Lista de Compras", use_container_width=True):
                st.session_state.show_shopping_list = False
                st.rerun()
    
    else:
        st.error("❌ Erro ao calcular ingredientes necessários!")

def generate_shopping_list_pdf(compras_data, custo_total, producao_items):
    """Gera PDF da lista de compras formatado"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=30,
        textColor=colors.darkgreen
    )
    story.append(Paragraph("🛒 Lista de Compras - Marmitas Fit", title_style))
    
    # Data e hora
    data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    story.append(Paragraph(f"<b>Data:</b> {data_hora}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Resumo da produção
    story.append(Paragraph("<b>📦 Resumo da Produção:</b>", styles['Heading2']))
    
    for item in producao_items:
        story.append(Paragraph(f"• {item['receita']}: {item['quantidade']} marmitas", styles['Normal']))
    
    total_marmitas = sum(item['quantidade'] for item in producao_items)
    story.append(Paragraph(f"<b>Total de marmitas:</b> {total_marmitas}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Tabela de ingredientes
    story.append(Paragraph("<b>🥕 Ingredientes para Comprar:</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Preparar dados da tabela
    table_data = [['Ingrediente', 'Qtd. Receita', 'Qtd. Compra', 'Preço Unit.', 'Custo Total']]
    
    for item in compras_data:
        table_data.append([
            item['Ingrediente'],
            item['Quantidade (receita)'],
            item['Quantidade (compra)'],
            item['Preço Unit.'],
            item['Custo Total']
        ])
    
    # Criar tabela
    table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch])
    
    # Estilo da tabela
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Total
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.darkgreen,
        spaceAfter=20
    )
    story.append(Paragraph(f"<b>💰 CUSTO TOTAL DAS COMPRAS: R$ {custo_total:.2f}</b>", total_style))
    
    # Rodapé
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1  # Centro
    )
    story.append(Paragraph("Gerado automaticamente pelo Sistema Marmitas Fit", footer_style))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    main()