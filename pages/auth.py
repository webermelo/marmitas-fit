# -*- coding: utf-8 -*-
"""
Sistema de Autenticação
"""

import streamlit as st
import time
from config.firebase_config import get_firebase_manager
from utils.database import get_database_manager

class AuthManager:
    def __init__(self):
        self.firebase = get_firebase_manager()
        self.auth = self.firebase.get_auth_client()
        self.db_manager = get_database_manager()
    
    def login_user(self, email, password):
        """Faz login do usuário"""
        try:
            if not self.auth:
                # Modo demo - login automático
                st.session_state.user = {
                    "email": email,
                    "uid": "demo_user",
                    "display_name": email.split("@")[0].title()
                }
                self.db_manager.init_user_data("demo_user")
                return True
            
            # Login real com Firebase
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            if user:
                st.session_state.user = {
                    "email": email,
                    "uid": user["localId"],
                    "token": user["idToken"],
                    "display_name": email.split("@")[0].title()
                }
                
                # Inicializar dados do usuário se necessário
                self.db_manager.init_user_data(user["localId"])
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Erro no login: {e}")
            return False
    
    def register_user(self, email, password):
        """Registra novo usuário"""
        try:
            if not self.auth:
                # Modo demo
                st.success("✅ Conta criada em modo demonstração!")
                time.sleep(1)
                return self.login_user(email, password)
            
            # Registro real com Firebase
            user = self.auth.create_user_with_email_and_password(email, password)
            
            if user:
                st.success("✅ Conta criada com sucesso!")
                time.sleep(1)
                return self.login_user(email, password)
            
            return False
            
        except Exception as e:
            st.error(f"Erro no registro: {e}")
            return False
    
    def logout_user(self):
        """Faz logout do usuário"""
        if 'user' in st.session_state:
            del st.session_state.user
        st.rerun()
    
    def is_authenticated(self):
        """Verifica se usuário está logado"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self):
        """Retorna usuário atual"""
        return st.session_state.get('user', None)

def show_auth_page():
    """Página de autenticação"""
    st.title("🥗 Marmitas Fit - Sistema Web")
    st.markdown("### Sistema de Gestão de Marmitas para Múltiplos Usuários")
    
    auth_manager = AuthManager()
    
    # Tabs para Login e Registro
    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Criar Conta"])
    
    with tab_login:
        st.subheader("Fazer Login")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
            
            login_button = st.form_submit_button("🚀 Entrar", use_container_width=True)
            
            if login_button:
                if email and password:
                    with st.spinner("Fazendo login..."):
                        if auth_manager.login_user(email, password):
                            st.success("✅ Login realizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Email ou senha incorretos!")
                else:
                    st.error("❌ Preencha todos os campos!")
    
    with tab_register:
        st.subheader("Criar Nova Conta")
        
        with st.form("register_form"):
            reg_email = st.text_input("📧 Email", placeholder="seu@email.com", key="reg_email")
            reg_password = st.text_input("🔒 Senha", type="password", placeholder="Escolha uma senha", key="reg_password")
            reg_password_confirm = st.text_input("🔒 Confirmar Senha", type="password", placeholder="Confirme sua senha")
            
            register_button = st.form_submit_button("✨ Criar Conta", use_container_width=True)
            
            if register_button:
                if reg_email and reg_password and reg_password_confirm:
                    if reg_password == reg_password_confirm:
                        if len(reg_password) >= 6:
                            with st.spinner("Criando conta..."):
                                if auth_manager.register_user(reg_email, reg_password):
                                    st.rerun()
                        else:
                            st.error("❌ A senha deve ter pelo menos 6 caracteres!")
                    else:
                        st.error("❌ As senhas não coincidem!")
                else:
                    st.error("❌ Preencha todos os campos!")
    
    # Modo Demo
    st.markdown("---")
    st.info("💡 **Modo Demonstração**: Use qualquer email/senha para testar o sistema!")
    
    if st.button("🎮 Entrar em Modo Demo", use_container_width=True):
        with st.spinner("Iniciando modo demo..."):
            if auth_manager.login_user("demo@marmitasfit.com", "demo123"):
                st.success("✅ Modo demo ativado!")
                time.sleep(1)
                st.rerun()

def check_authentication():
    """Verifica autenticação e mostra página apropriada"""
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        show_auth_page()
        return False
    
    return True

def show_user_info_sidebar():
    """Mostra informações do usuário na sidebar"""
    auth_manager = AuthManager()
    
    if auth_manager.is_authenticated():
        user = auth_manager.get_current_user()
        
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"👤 **{user['display_name']}**")
            st.markdown(f"📧 {user['email']}")
            
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.logout_user()