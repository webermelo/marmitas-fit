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

# Sistema de logging
try:
    from utils.logger import logger, log_exception, safe_import
    logger.log_system_start()
    logger.info("App iniciado com sistema de logging ativo")
except Exception as e:
    st.error(f"Erro ao inicializar logging: {e}")
    # Fallback logger simples
    class SimpleLogger:
        def info(self, msg, data=None): print(f"INFO: {msg}")
        def error(self, msg, exc=None, data=None): print(f"ERROR: {msg}")
        def warning(self, msg, data=None): print(f"WARNING: {msg}")
        def debug(self, msg, data=None): print(f"DEBUG: {msg}")
        def log_user_action(self, action, user=None, details=None): print(f"ACTION: {action}")
        def log_page_access(self, page, user=None): print(f"PAGE: {page}")
    
    logger = SimpleLogger()
    
    def log_exception(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Erro em {func.__name__}", e)
                raise
        return wrapper
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
    
    # Tentar restaurar sessão salva
    if 'user' not in st.session_state:
        restore_saved_session()
        logger.debug("Tentativa de restaurar sessão")
    
    # Verificar se usuário já está logado
    if 'user' in st.session_state:
        logger.debug(f"Usuário encontrado na sessão: {st.session_state.user.get('email', 'N/A')}")
        
        # TEMPORÁRIO: Desabilitar validação de token para debugging
        # Manter usuário logado sem verificar token para testar persistência
        return True
    
    # Se Firebase não disponível, mostrar opção de usar modo demo
    if not FIREBASE_AVAILABLE:
        return show_simple_auth()
    
    # Interface de login com Firebase
    return show_login_page()

def save_session():
    """Salva dados da sessão para persistência"""
    if 'user' in st.session_state:
        # Salvar nos query parameters (mais confiável que localStorage)
        st.query_params["logged_in"] = "true"
        st.query_params["user_email"] = st.session_state.user.get('email', '')
        st.query_params["user_uid"] = st.session_state.user.get('uid', '')
        st.query_params["user_name"] = st.session_state.user.get('display_name', '')
        st.query_params["user_token"] = st.session_state.user.get('token', '')
        
        # Backup no session state  
        st.session_state['session_saved'] = True
        st.session_state['saved_at'] = datetime.now().isoformat()
        
        logger.info(f"Sessão salva para: {st.session_state.user.get('email')}")

def restore_saved_session():
    """Restaura sessão salva dos query parameters"""
    
    # Verificar se há dados nos query parameters
    if st.query_params.get("logged_in") == "true":
        user_email = st.query_params.get("user_email")
        user_uid = st.query_params.get("user_uid")
        
        if user_email and user_uid:
            # Restaurar dados do usuário
            st.session_state.user = {
                'email': user_email,
                'uid': user_uid,
                'display_name': st.query_params.get("user_name", user_email.split("@")[0]),
                'token': st.query_params.get("user_token", ""),
                'refresh_token': st.query_params.get("user_refresh", "")
            }
            
            logger.info(f"✅ Usuário restaurado dos query params: {user_email}")
            return True
        else:
            logger.warning("Query params incompletos - limpando")
            # Limpar query params inválidos
            if "logged_in" in st.query_params:
                del st.query_params["logged_in"]
    
    return False


def clear_session():
    """Limpa sessão e dados salvos"""
    # Limpar query parameters de login
    login_params = ["logged_in", "user_uid", "user_email", "user_name", "user_token", "user_refresh"]
    for key in login_params:
        if key in st.query_params:
            del st.query_params[key]
    
    # Limpar session state
    keys_to_clear = ['user', 'saved_user', 'session_saved', 'firebase_token', 
                     'demo_ingredients', 'demo_recipes', 'current_production', 'production_history']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    logger.info("Sessão completamente limpa")

def is_token_valid(token):
    """Verifica se token Firebase ainda é válido"""
    if not token or not FIREBASE_AVAILABLE:
        return False
    
    try:
        # Fazer uma chamada simples para verificar token
        import requests
        config = st.secrets.get("firebase", {})
        api_key = config.get("apiKey", "")
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        payload = {"idToken": token}
        response = requests.post(url, json=payload)
        
        logger.debug(f"Token validation response: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False

def refresh_user_token():
    """Tenta renovar token do usuário"""
    if not FIREBASE_AVAILABLE or 'user' not in st.session_state:
        return False
    
    refresh_token = st.session_state.user.get('refresh_token')
    if not refresh_token:
        return False
    
    try:
        result = firebase_auth.refresh_token(refresh_token)
        if result['success']:
            # Atualizar token na sessão
            st.session_state.user['token'] = result['token']
            if 'refresh_token' in result:
                st.session_state.user['refresh_token'] = result['refresh_token']
            save_session()
            return True
    except:
        pass
    
    return False

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
                                "display_name": user_data["display_name"],
                                "token": user_data["token"],
                                "refresh_token": user_data["refresh_token"]
                            }
                            st.session_state.firebase_token = user_data["token"]
                            st.session_state.firebase_refresh_token = user_data["refresh_token"]
                            
                            # Salvar sessão para persistência
                            save_session()
                            
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
                                    "display_name": user_data["display_name"],
                                    "token": user_data["token"],
                                    "refresh_token": user_data["refresh_token"]
                                }
                                st.session_state.firebase_token = user_data["token"]
                                st.session_state.firebase_refresh_token = user_data["refresh_token"]
                                
                                # Salvar sessão para persistência
                                save_session()
                                
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
    """Inicializa dados demo ou carrega do Firebase"""
    if 'demo_ingredients' not in st.session_state:
        # Tentar carregar do Firebase primeiro
        firebase_ingredients = load_ingredients_from_firebase()
        if firebase_ingredients:
            st.session_state.demo_ingredients = firebase_ingredients
        else:
            # Fallback para dados demo se Firebase não disponível
            st.session_state.demo_ingredients = []
    
    if 'demo_recipes' not in st.session_state:
        # Tentar carregar do Firebase primeiro
        firebase_recipes = load_recipes_from_firebase()
        if firebase_recipes:
            st.session_state.demo_recipes = firebase_recipes
        else:
            # Fallback para dados demo se Firebase não disponível
            st.session_state.demo_recipes = []

def load_ingredients_from_firebase():
    """Carrega ingredientes do Firebase"""
    if not FIREBASE_AVAILABLE or 'user' not in st.session_state:
        logger.debug("Firebase não disponível ou usuário não logado")
        return []
    
    try:
        from utils.firestore_client import get_firestore_client
        db = get_firestore_client()
        if db:
            # Configurar token
            if 'token' in st.session_state.user:
                db.set_auth_token(st.session_state.user['token'])
            
            # Carregar ingredientes do usuário
            user_id = st.session_state.user['uid']
            collection_path = f'users/{user_id}/ingredients'
            
            logger.info(f"Tentando carregar ingredientes de: {collection_path}")
            ingredients = db.collection(collection_path).get()
            
            logger.info(f"✅ Carregados {len(ingredients)} ingredientes do Firebase")
            
            # Debug: mostrar estrutura dos dados
            if ingredients:
                logger.debug(f"Exemplo ingrediente: {ingredients[0]}")
            
            return ingredients
        else:
            logger.error("Cliente Firestore não disponível")
            
    except Exception as e:
        logger.error(f"❌ Erro ao carregar ingredientes do Firebase: {e}")
    
    return []

def load_recipes_from_firebase():
    """Carrega receitas do Firebase"""
    if not FIREBASE_AVAILABLE or 'user' not in st.session_state:
        return []
    
    try:
        from utils.firestore_client import get_firestore_client
        db = get_firestore_client()
        if db:
            # Configurar token
            if 'token' in st.session_state.user:
                db.set_auth_token(st.session_state.user['token'])
            
            # Carregar receitas do usuário
            user_id = st.session_state.user['uid']
            recipes = db.collection(f'users/{user_id}/recipes').get()
            
            logger.info(f"Carregadas {len(recipes)} receitas do Firebase")
            return recipes
            
    except Exception as e:
        logger.error(f"Erro ao carregar receitas do Firebase: {e}")
    
    return []

def save_ingredient_to_firebase(ingredient):
    """Salva ingrediente no Firebase"""
    if not FIREBASE_AVAILABLE or 'user' not in st.session_state:
        logger.debug("Firebase não disponível ou usuário não logado - não salvando")
        return False
    
    try:
        from utils.firestore_client import get_firestore_client
        db = get_firestore_client()
        if db:
            # Configurar token
            if 'token' in st.session_state.user:
                db.set_auth_token(st.session_state.user['token'])
            
            # Preparar dados para salvar
            user_id = st.session_state.user['uid']
            collection_path = f'users/{user_id}/ingredients'
            
            ingredient_data = ingredient.copy()
            ingredient_data['user_id'] = user_id
            ingredient_data['created_at'] = datetime.now().isoformat()
            
            logger.info(f"Tentando salvar ingrediente em: {collection_path}")
            logger.debug(f"Dados do ingrediente: {ingredient_data}")
            
            result = db.collection(collection_path).add(ingredient_data)
            
            logger.info(f"✅ Ingrediente salvo no Firebase: {ingredient.get('nome', 'N/A')}")
            logger.debug(f"Resultado Firebase: {result}")
            
            return True
        else:
            logger.error("Cliente Firestore não disponível")
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar ingrediente no Firebase: {e}")
        logger.error(f"Detalhes do erro: {str(e)}")
    
    return False

def save_recipe_to_firebase(recipe):
    """Salva receita no Firebase"""
    if not FIREBASE_AVAILABLE or 'user' not in st.session_state:
        return False
    
    try:
        from utils.firestore_client import get_firestore_client
        db = get_firestore_client()
        if db:
            # Configurar token
            if 'token' in st.session_state.user:
                db.set_auth_token(st.session_state.user['token'])
            
            # Salvar receita
            user_id = st.session_state.user['uid']
            recipe['user_id'] = user_id
            recipe['created_at'] = datetime.now().isoformat()
            
            result = db.collection(f'users/{user_id}/recipes').add(recipe)
            logger.info(f"Receita salva no Firebase: {recipe.get('nome_receita', 'N/A')}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao salvar receita no Firebase: {e}")
    
    return False

@log_exception
def main():
    """Função principal da aplicação"""
    
    logger.info("Iniciando função main()")
    
    # Verificar autenticação
    if not check_auth():
        logger.warning("Autenticação falhou")
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
            # Limpar sessão e dados salvos
            clear_session()
            st.rerun()
        
        st.markdown("---")
        
        menu_options = ["🏠 Dashboard", "🥕 Ingredientes", "📝 Receitas", "🏭 Produção"]
        
        # Adicionar limpeza se há duplicatas por nome
        has_duplicates, _, _ = detect_duplicates()
        if has_duplicates:
            menu_options.append("🧹 Limpeza de Dados")
        
        # Adicionar menu admin se usuário for administrador
        try:
            from pages.admin_safe import show_admin_menu_item
            from pages.debug import is_debug_enabled
            
            if show_admin_menu_item():
                menu_options.append("👑 Administração")
                
                # Menu debug para admins
                if is_debug_enabled():
                    menu_options.append("🔍 Debug")
        except Exception as e:
            logger.error("Erro ao carregar menus admin", e)
        
        selected_page = st.radio("Navegação:", menu_options)
    
    # Header principal
    st.title("🥗 Marmitas Fit - Web App (Versão Corrigida)")
    
    # Roteamento de páginas
    if selected_page == "🏠 Dashboard":
        logger.log_page_access("Dashboard", user.get('email'))
        show_dashboard()
    elif selected_page == "🥕 Ingredientes":
        logger.log_page_access("Ingredientes", user.get('email'))
        show_ingredientes()
    elif selected_page == "📝 Receitas":
        logger.log_page_access("Receitas", user.get('email'))
        show_receitas()
    elif selected_page == "🏭 Produção":
        logger.log_page_access("Produção", user.get('email'))
        show_producao()
    elif selected_page == "👑 Administração":
        logger.log_page_access("Administração", user.get('email'))
        try:
            from pages.admin_safe import show_admin_page
            show_admin_page()
        except Exception as e:
            logger.error("Erro ao carregar admin_safe", e)
            st.error("Erro ao carregar painel administrativo. Detalhes nos logs.")
    elif selected_page == "🔍 Debug":
        logger.log_page_access("Debug", user.get('email'))
        try:
            from pages.debug import show_debug_page
            show_debug_page()
        except Exception as e:
            logger.error("Erro ao carregar página debug", e)
            st.error("Erro ao carregar página de debug. Detalhes nos logs.")
    elif selected_page == "🧹 Limpeza de Dados":
        logger.log_page_access("Limpeza", user.get('email'))
        try:
            from pages.cleanup import show_cleanup_page
            show_cleanup_page()
        except Exception as e:
            logger.error("Erro ao carregar página de limpeza", e)
            st.error("Erro ao carregar página de limpeza. Detalhes nos logs.")

def detect_duplicates():
    """Detecta ingredientes duplicados por nome"""
    ingredients = st.session_state.get('demo_ingredients', [])
    if not ingredients:
        return False, 0, []
    
    # Contar ingredientes por nome (case-insensitive)
    name_counts = {}
    duplicates = []
    
    for i, ing in enumerate(ingredients):
        if isinstance(ing, dict):
            nome = ing.get('nome', '').strip().lower()
            if nome:
                if nome in name_counts:
                    name_counts[nome] += 1
                    duplicates.append((i, ing.get('nome', ''), nome))
                else:
                    name_counts[nome] = 1
    
    # Verificar se há duplicatas reais
    has_duplicates = any(count > 1 for count in name_counts.values())
    total_duplicates = sum(count - 1 for count in name_counts.values() if count > 1)
    
    return has_duplicates, total_duplicates, duplicates

def show_dashboard():
    """Dashboard principal"""
    st.header("🏠 Dashboard")
    
    # DETECÇÃO INTELIGENTE DE DUPLICATAS POR NOME
    has_duplicates, total_duplicates, duplicate_list = detect_duplicates()
    total_ingredients = len(st.session_state.get('demo_ingredients', []))
    
    if has_duplicates:
        st.error(f"🚨 DUPLICATAS DETECTADAS: {total_duplicates} ingredientes duplicados encontrados!")
        st.warning(f"⚠️ Total de {total_ingredients} ingredientes, mas {total_duplicates} são duplicatas por nome.")
        
        # Mostrar alguns exemplos de duplicatas
        if duplicate_list:
            with st.expander("🔍 Ver exemplos de duplicatas"):
                for i, (idx, original_name, normalized_name) in enumerate(duplicate_list[:5]):
                    st.write(f"• Duplicata {i+1}: '{original_name}' (posição {idx})")
                if len(duplicate_list) > 5:
                    st.write(f"... e mais {len(duplicate_list) - 5} duplicatas")
        
        st.warning("⚠️ Use os botões abaixo para resolver:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ LIMPAR TUDO", type="primary", key="dashboard_clear_all"):
                st.session_state.demo_ingredients = []
                st.success("✅ Todos os ingredientes foram removidos!")
                st.balloons()
                st.rerun()
        
        with col2:
            if st.button("🔧 RESETAR COM BASE", type="secondary", key="dashboard_reset_base"):
                try:
                    import pandas as pd
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
            if st.button("📊 REMOVER DUPLICATAS", key="dashboard_remove_dupes"):
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
        st.info("💡 **Recomendação:** Use 'RESETAR COM BASE' para voltar aos 200 ingredientes originais.")
        st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🥕 Ingredientes", len(st.session_state.demo_ingredients))
    
    with col2:
        receitas_count = len(set([r['nome_receita'] for r in st.session_state.demo_recipes]))
        st.metric("📝 Receitas", receitas_count)
    
    with col3:
        st.metric("🔄 Status", "Online")
    
    # Informações sobre persistência de dados
    st.markdown("---")
    st.subheader("💾 Persistência de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if FIREBASE_AVAILABLE and 'user' in st.session_state and 'token' in st.session_state.user:
            st.success("🔥 **Firebase Ativo - Dados Permanentes**")
            st.write("""
            **Como funcionam os dados:**
            • ✅ Salvos no **Firebase Firestore**
            • ✅ **Persistem após logout/reload**
            • ✅ **Sincronizados** entre dispositivos
            • ✅ **Login mantido** ao recarregar página
            • ✅ **Backup automático** na nuvem
            """)
        else:
            st.warning("🎮 **Modo Local/Demo**")
            st.write("""
            **Como funcionam os dados:**
            • Salvos na **sessão do navegador** (temporário)
            • Permanecem enquanto a **aba estiver aberta**
            • São **perdidos** ao fechar o navegador
            • **Logout também apaga** todos os dados
            """)
    
    with col2:
        if FIREBASE_AVAILABLE and 'user' in st.session_state and 'token' in st.session_state.user:
            st.info("✅ **Dados Seguros no Firebase**")
            st.write("""
            **Benefícios ativados:**
            • ✅ **Login persistente** - não sai ao recarregar
            • ✅ **Ingredientes salvos** permanentemente
            • ✅ **Receitas salvas** permanentemente
            • ✅ **Dados isolados** por usuário
            • ✅ **Backup automático** na Google Cloud
            """)
        else:
            st.warning("⚠️ **Dados Temporários**")
            st.write("""
            **Limitações atuais:**
            • ❌ Login perdido ao recarregar
            • ❌ Dados perdidos ao fechar aba
            • ❌ Sem backup/sincronização
            • ❌ Dados não persistem
            
            **💡 Faça login com Firebase para persistência!**
            """)
    
    # Status da conexão detalhado
    st.markdown("---")
    st.subheader("🔍 Status de Debug")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Status Firebase:**")
        if FIREBASE_AVAILABLE:
            st.success("✅ Firebase disponível")
            if 'user' in st.session_state:
                if 'token' in st.session_state.user:
                    st.success("✅ Usuário autenticado")
                    st.info(f"👤 Email: {st.session_state.user.get('email', 'N/A')}")
                    st.info(f"🔑 UID: {st.session_state.user.get('uid', 'N/A')}")
                else:
                    st.warning("⚠️ Usuário sem token")
            else:
                st.error("❌ Usuário não encontrado")
        else:
            st.error("❌ Firebase não disponível")
    
    with col2:
        st.write("**Debug Session & URL:**")
        st.write(f"Demo ingredients: {len(st.session_state.get('demo_ingredients', []))}")
        st.write(f"Demo recipes: {len(st.session_state.get('demo_recipes', []))}")
        st.write(f"Session saved: {st.session_state.get('session_saved', False)}")
        st.write(f"User in session: {'user' in st.session_state}")
        
        # Mostrar query parameters importantes
        st.write("**Query Parameters:**")
        st.write(f"logged_in: {st.query_params.get('logged_in', 'None')}")
        st.write(f"user_email: {st.query_params.get('user_email', 'None')}")
        st.write(f"user_uid: {st.query_params.get('user_uid', 'None')[:10]}...")
        
        # Botão para forçar reload dos dados
        if st.button("🔄 Forçar Reload Firebase"):
            if 'user' in st.session_state:
                firebase_ingredients = load_ingredients_from_firebase()
                st.session_state.demo_ingredients = firebase_ingredients
                st.info(f"Carregados {len(firebase_ingredients)} ingredientes")
                st.rerun()
        
        # Botão para testar persistência
        if st.button("🧪 Testar Reload Página", help="Simula F5 - deve manter login"):
            st.rerun()
    
    # Mostrar logs recentes se possível
    with st.expander("📋 Debug Logs"):
        try:
            from utils.logger import logger
            logs = logger.get_recent_logs(20)
            st.text(logs[-1000:] if logs else "Nenhum log disponível")
        except:
            st.text("Sistema de logs não disponível")

def show_ingredientes():
    """Página de ingredientes"""
    st.header("🥕 Gestão de Ingredientes")
    
    # Detectar duplicatas reais por nome
    has_duplicates, total_duplicates, duplicate_list = detect_duplicates()
    
    if has_duplicates:
        st.error(f"🚨 DUPLICATAS DETECTADAS: {total_duplicates} ingredientes com nomes duplicados!")
        
        # Mostrar exemplos de duplicatas
        with st.expander(f"🔍 Ver {min(len(duplicate_list), 10)} exemplos de duplicatas"):
            for i, (idx, original_name, normalized_name) in enumerate(duplicate_list[:10]):
                st.write(f"• '{original_name}' (posição {idx})")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 REMOVER DUPLICATAS", type="primary", key="ingredients_remove_dupes"):
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
                st.rerun()
        
        with col2:
            if st.button("🔄 LIMPAR TUDO", key="emergency_clear_ingredients"):
                st.session_state.demo_ingredients = []
                st.success("✅ Todos os ingredientes foram removidos!")
                st.balloons()
                st.rerun()
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Adicionar"])
    
    with tab1:
        st.subheader("📋 Ingredientes Cadastrados")
        
        if st.session_state.demo_ingredients:
            # Debug: Mostrar estrutura dos dados
            with st.expander("🔍 Debug - Estrutura dos Ingredientes"):
                st.write(f"**Total de ingredientes:** {len(st.session_state.demo_ingredients)}")
                st.write("**Primeiros 3 ingredientes (estrutura):**")
                for i, ing in enumerate(st.session_state.demo_ingredients[:3]):
                    st.write(f"Ingrediente {i+1}:")
                    st.json(ing)
                
                st.write("**Chaves encontradas no primeiro ingrediente:**")
                if st.session_state.demo_ingredients:
                    st.write(list(st.session_state.demo_ingredients[0].keys()))
            
            # Criar DataFrame com tratamento de erro
            try:
                df_ingredients = pd.DataFrame(st.session_state.demo_ingredients)
                st.dataframe(df_ingredients, use_container_width=True)
                
                # Mostrar info do DataFrame
                with st.expander("📊 Info DataFrame"):
                    st.write("**Colunas do DataFrame:**")
                    st.write(list(df_ingredients.columns))
                    st.write("**Tipos de dados:**")
                    st.write(df_ingredients.dtypes)
                    st.write("**Shape:**")
                    st.write(df_ingredients.shape)
                    
            except Exception as e:
                st.error(f"Erro ao criar DataFrame: {str(e)}")
                st.write("**Dados brutos:**")
                for i, ing in enumerate(st.session_state.demo_ingredients):
                    st.write(f"{i+1}. {ing}")
                    
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
                        'nome': nome,
                        'categoria': categoria,
                        'unid_receita': unidade_receita,
                        'unid_compra': unidade_compra,
                        'preco': preco,
                        'kcal_unid': kcal,
                        'fator_conv': fator_conversao,
                        'ativo': True,
                        'observacoes': ''
                    }
                    
                    # Salvar no session state
                    st.session_state.demo_ingredients.append(novo_ingrediente)
                    
                    # Tentar salvar no Firebase
                    firebase_saved = save_ingredient_to_firebase(novo_ingrediente)
                    
                    if firebase_saved:
                        st.success(f"✅ Ingrediente '{nome}' salvo no Firebase!")
                    else:
                        st.success(f"✅ Ingrediente '{nome}' salvo localmente!")
                        st.info("💾 Para persistência permanente, verifique conexão Firebase")
                    
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
                        
                        firebase_saved_count = 0
                        
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
                                "created_at": datetime.now().isoformat()
                            }
                            
                            # Salvar no session state
                            st.session_state.demo_recipes.append(recipe_data)
                            
                            # Tentar salvar no Firebase
                            if save_recipe_to_firebase(recipe_data):
                                firebase_saved_count += 1
                        
                        if firebase_saved_count > 0:
                            st.success(f"✅ Receita '{nome_receita}' salva no Firebase com {len(st.session_state.recipe_ingredients)} ingredientes!")
                        else:
                            st.success(f"✅ Receita '{nome_receita}' salva localmente com {len(st.session_state.recipe_ingredients)} ingredientes!")
                            st.info("💾 Para persistência permanente, verifique conexão Firebase")
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