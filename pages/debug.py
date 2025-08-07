# -*- coding: utf-8 -*-
"""
Página de Debug e Logs - Marmitas Fit
Visualização de logs e diagnóstico do sistema
"""

import streamlit as st
import sys
from datetime import datetime
from pathlib import Path

def show_debug_page():
    """Página de debug e logs"""
    
    st.title("🔍 Debug & Logs")
    st.info("Página para diagnóstico técnico e visualização de logs")
    
    # Tabs de debug
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Logs", "🐍 Sistema", "📊 Session State", "🔧 Ações"])
    
    with tab1:
        show_logs_section()
    
    with tab2:
        show_system_info()
    
    with tab3:
        show_session_state()
    
    with tab4:
        show_debug_actions()

def show_logs_section():
    """Seção de visualização de logs"""
    
    st.header("📄 System Logs")
    
    # Tentar obter logs do sistema
    try:
        from utils.logger import logger
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            lines_to_show = st.selectbox("Linhas:", [10, 25, 50, 100, 200], index=2)
            auto_refresh = st.checkbox("Auto-refresh (5s)")
        
        with col1:
            st.subheader(f"📋 Últimas {lines_to_show} linhas")
        
        # Exibir logs
        log_content = logger.get_recent_logs(lines_to_show)
        
        if log_content.strip():
            st.code(log_content, language="text")
        else:
            st.warning("Nenhum log encontrado")
        
        # Auto-refresh
        if auto_refresh:
            import time
            time.sleep(5)
            st.experimental_rerun()
        
    except Exception as e:
        st.error(f"Erro ao carregar logs: {e}")
        st.info("Sistema de logging não disponível")

def show_system_info():
    """Informações do sistema"""
    
    st.header("🐍 Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Python & Ambiente")
        st.code(f"""
Python Version: {sys.version}
Executable: {sys.executable}
Platform: {sys.platform}
Working Directory: {Path.cwd()}
        """)
        
        st.subheader("Streamlit Info")
        try:
            st.code(f"""
Streamlit Version: {st.__version__}
Session ID: {st.session_state.get('session_id', 'N/A')}
Timestamp: {datetime.now().isoformat()}
            """)
        except Exception as e:
            st.error(f"Erro ao obter info Streamlit: {e}")
    
    with col2:
        st.subheader("Módulos Importados")
        
        # Verificar módulos críticos
        modules_to_check = [
            'pandas',
            'streamlit',
            'utils.logger',
            'utils.firebase_auth',
            'utils.firestore_client',
            'pages.admin_safe'
        ]
        
        status_data = []
        for module in modules_to_check:
            try:
                __import__(module)
                status = "✅ OK"
            except Exception as e:
                status = f"❌ ERRO: {str(e)[:50]}..."
            
            status_data.append(f"{module}: {status}")
        
        st.code("\n".join(status_data))

def show_session_state():
    """Mostra estado da sessão"""
    
    st.header("📊 Session State")
    
    if st.session_state:
        # Filtros
        show_all = st.checkbox("Mostrar todos os campos")
        
        # Campos importantes
        important_keys = ['user', 'authenticated', 'demo_ingredients', 'demo_recipes']
        
        # Selecionar chaves para exibir
        keys_to_show = list(st.session_state.keys()) if show_all else [k for k in important_keys if k in st.session_state]
        
        if keys_to_show:
            for key in sorted(keys_to_show):
                with st.expander(f"🔑 {key}"):
                    try:
                        value = st.session_state[key]
                        st.json(value if isinstance(value, (dict, list)) else str(value))
                    except Exception as e:
                        st.error(f"Erro ao exibir {key}: {e}")
        else:
            st.warning("Nenhum dados de sessão encontrados")
    else:
        st.error("Session state não disponível")

def show_debug_actions():
    """Ações de debug"""
    
    st.header("🔧 Ações de Debug")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Limpeza")
        
        if st.button("🗑️ Limpar Session State"):
            st.session_state.clear()
            st.success("Session state limpo!")
            st.experimental_rerun()
        
        if st.button("🔄 Reinicializar Dados Demo"):
            try:
                # Limpar dados demo
                keys_to_clear = [k for k in st.session_state.keys() if k.startswith('demo_')]
                for key in keys_to_clear:
                    del st.session_state[key]
                
                st.success("Dados demo reinicializados!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
    
    with col2:
        st.subheader("Testes")
        
        if st.button("🧪 Testar Logger"):
            try:
                from utils.logger import logger
                logger.info("Teste de log - INFO")
                logger.warning("Teste de log - WARNING")
                logger.debug("Teste de log - DEBUG")
                st.success("Logs de teste enviados!")
            except Exception as e:
                st.error(f"Erro no teste de logging: {e}")
        
        if st.button("🔥 Simular Erro"):
            try:
                from utils.logger import logger
                # Simular erro para teste
                raise Exception("Erro simulado para teste do sistema de logging")
            except Exception as e:
                logger.error("Erro simulado capturado", e)
                st.warning("Erro simulado capturado e registrado nos logs")

def is_debug_enabled():
    """Verifica se debug está habilitado"""
    # Habilitar debug para admins ou em desenvolvimento
    try:
        from pages.admin_safe import is_admin
        
        if 'user' in st.session_state:
            user_email = st.session_state.user.get('email', '')
            return is_admin(user_email)
        
        return False
    except:
        return False