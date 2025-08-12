#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOKEN RECOVERY SYSTEM - OPUS 4.1
Sistema robusto de recuperação e manutenção de tokens Firebase
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time
import traceback

class TokenRecoverySystem:
    """Sistema robusto de recuperação de tokens Firebase"""
    
    def __init__(self):
        self.api_key = self._get_firebase_api_key()
        self.recovery_log = []
        
    def _get_firebase_api_key(self):
        """Obtém API key Firebase"""
        try:
            # Método 1: Secrets
            config = st.secrets.get("firebase", {})
            if config and "apiKey" in config:
                return config["apiKey"]
            
            # Método 2: Config local
            from config.firebase_config import FIREBASE_CONFIG
            return FIREBASE_CONFIG.get("apiKey", "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90")
            
        except:
            return "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
    
    def main(self):
        st.set_page_config(
            page_title="Token Recovery System",
            page_icon="🔧",
            layout="wide"
        )
        
        st.title("🔧 TOKEN RECOVERY SYSTEM - OPUS 4.1")
        st.markdown("---")
        
        # Status atual do token
        self.show_current_status()
        
        # Opções de recuperação
        self.show_recovery_options()
        
        # Log de recuperação
        self.show_recovery_log()
    
    def show_current_status(self):
        """Mostra status atual do token"""
        st.header("📊 STATUS ATUAL DO TOKEN")
        
        if 'user' not in st.session_state:
            st.error("❌ USUÁRIO NÃO LOGADO")
            st.info("👉 Faça login primeiro para usar o sistema de recuperação")
            return False
        
        user = st.session_state.user
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Presença de campos
            has_token = 'token' in user and user['token']
            has_refresh = 'refresh_token' in user and user['refresh_token']
            has_timestamp = 'token_timestamp' in user
            
            st.metric("Token Presente", "✅" if has_token else "❌")
            st.metric("Refresh Token", "✅" if has_refresh else "❌")  
            st.metric("Timestamp", "✅" if has_timestamp else "❌")
        
        with col2:
            # Idade do token
            if has_timestamp:
                try:
                    token_time = datetime.fromisoformat(user['token_timestamp'])
                    age_seconds = (datetime.now() - token_time).total_seconds()
                    age_minutes = age_seconds / 60
                    
                    st.metric("Idade (minutos)", f"{age_minutes:.1f}")
                    
                    # Status baseado na idade
                    if age_seconds > 3600:  # 1 hora
                        st.error("🚨 TOKEN EXPIRADO")
                    elif age_seconds > 3000:  # 50 minutos
                        st.warning("⚠️ TOKEN PRÓXIMO DO VENCIMENTO")
                    else:
                        st.success("✅ TOKEN VÁLIDO")
                        
                except:
                    st.metric("Idade", "❌ Erro")
            else:
                st.metric("Idade", "❌ Sem timestamp")
        
        with col3:
            # Tamanho do token (indicador de validade)
            if has_token:
                token_length = len(user['token'])
                st.metric("Tamanho Token", token_length)
                
                # Tokens Firebase JWT normalmente têm 800-1500+ caracteres
                if token_length < 500:
                    st.warning("⚠️ Token muito pequeno")
                elif token_length > 2000:
                    st.warning("⚠️ Token muito grande")
                else:
                    st.success("✅ Tamanho normal")
            else:
                st.metric("Tamanho", "0")
        
        return has_token
    
    def show_recovery_options(self):
        """Mostra opções de recuperação"""
        st.header("🔧 OPÇÕES DE RECUPERAÇÃO")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Renovação Automática")
            
            if st.button("🚀 TENTAR RENOVAR TOKEN", type="primary"):
                self.attempt_token_refresh()
            
            st.caption("Tenta renovar usando refresh_token atual")
            
            st.subheader("🧪 Validação Direta")
            
            if st.button("🔍 VALIDAR TOKEN ATUAL"):
                self.validate_current_token()
            
            st.caption("Verifica se token atual é aceito pelo Firebase")
        
        with col2:
            st.subheader("🚨 Recuperação Manual")
            
            if st.button("🔄 FORÇAR NOVO LOGIN", type="secondary"):
                self.force_relogin()
            
            st.caption("Limpa sessão e força login do zero")
            
            st.subheader("🔧 Reparar Session State")
            
            if st.button("🛠️ REPARAR SESSÃO"):
                self.repair_session_state()
            
            st.caption("Tenta reparar dados corrompidos na sessão")
    
    def attempt_token_refresh(self):
        """Tenta renovar o token"""
        st.subheader("🔄 RENOVAÇÃO EM PROGRESSO")
        
        if 'user' not in st.session_state:
            st.error("❌ Usuário não disponível")
            return
        
        user = st.session_state.user
        refresh_token = user.get('refresh_token')
        
        if not refresh_token:
            st.error("❌ Refresh token não disponível")
            self.log_recovery("REFRESH_FAILED", "Sem refresh_token disponível")
            return
        
        try:
            # Endpoint de renovação
            url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
            
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            st.info("🔄 Enviando requisição para Firebase...")
            
            with st.spinner("Renovando token..."):
                response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair novos tokens
                new_token = data.get("id_token")
                new_refresh_token = data.get("refresh_token", refresh_token)
                
                if new_token:
                    # Atualizar session state
                    st.session_state.user['token'] = new_token
                    st.session_state.user['refresh_token'] = new_refresh_token
                    st.session_state.user['token_timestamp'] = datetime.now().isoformat()
                    
                    st.success("✅ TOKEN RENOVADO COM SUCESSO!")
                    st.success(f"✅ Novo token: {len(new_token)} caracteres")
                    
                    self.log_recovery("REFRESH_SUCCESS", f"Token renovado - length: {len(new_token)}")
                    
                    # Testar novo token imediatamente
                    st.info("🧪 Testando novo token...")
                    if self.test_new_token(new_token):
                        st.success("🎉 NOVO TOKEN FUNCIONANDO!")
                    else:
                        st.warning("⚠️ Novo token renovado mas com problemas")
                else:
                    st.error("❌ Resposta sem novo token")
                    self.log_recovery("REFRESH_PARTIAL", "Resposta sem id_token")
            
            else:
                st.error(f"❌ FALHA NA RENOVAÇÃO: HTTP {response.status_code}")
                
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', 'Unknown error')
                        st.error(f"Erro: {error_msg}")
                        
                        # Diagnóstico específico
                        if 'TOKEN_EXPIRED' in error_msg or 'INVALID_REFRESH_TOKEN' in error_msg:
                            st.error("🚨 REFRESH TOKEN EXPIRADO - necessário login manual")
                            self.log_recovery("REFRESH_TOKEN_EXPIRED", error_msg)
                        else:
                            self.log_recovery("REFRESH_ERROR", error_msg)
                    
                    with st.expander("📋 Detalhes do Erro"):
                        st.json(error_data)
                        
                except:
                    st.error(f"Erro HTTP: {response.text}")
                    self.log_recovery("REFRESH_HTTP_ERROR", f"{response.status_code}: {response.text}")
        
        except requests.exceptions.Timeout:
            st.error("🚨 TIMEOUT: Firebase não respondeu em 15s")
            self.log_recovery("REFRESH_TIMEOUT", "Timeout de 15s")
            
        except requests.exceptions.RequestException as e:
            st.error(f"🚨 ERRO DE REDE: {str(e)}")
            self.log_recovery("REFRESH_NETWORK_ERROR", str(e))
            
        except Exception as e:
            st.error(f"🚨 ERRO INESPERADO: {str(e)}")
            st.code(traceback.format_exc())
            self.log_recovery("REFRESH_EXCEPTION", str(e))
    
    def validate_current_token(self):
        """Valida o token atual"""
        st.subheader("🔍 VALIDAÇÃO DO TOKEN")
        
        if 'user' not in st.session_state or 'token' not in st.session_state.user:
            st.error("❌ Token não disponível")
            return
        
        token = st.session_state.user['token']
        
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.api_key}"
            payload = {"idToken": token}
            
            st.info("🔄 Validando com Firebase Identity Toolkit...")
            
            with st.spinner("Validando..."):
                response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'users' in data and len(data['users']) > 0:
                    user_info = data['users'][0]
                    st.success("✅ TOKEN VÁLIDO!")
                    st.success(f"✅ Email: {user_info.get('email', 'N/A')}")
                    st.success(f"✅ Verificado: {user_info.get('emailVerified', False)}")
                    
                    self.log_recovery("VALIDATION_SUCCESS", f"Token válido para {user_info.get('email')}")
                    
                    # Se token é válido, problema pode estar no FirestoreClient
                    st.info("💡 Token válido - problema pode estar no FirestoreClient")
                    
                    if st.button("🔧 TESTAR FIRESTORE CLIENT"):
                        self.test_firestore_client()
                else:
                    st.error("❌ Resposta sem dados de usuário")
                    self.log_recovery("VALIDATION_NO_USER", "Response sem user data")
            
            else:
                st.error(f"❌ TOKEN INVÁLIDO: HTTP {response.status_code}")
                
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown')
                    st.error(f"Erro: {error_msg}")
                    
                    self.log_recovery("VALIDATION_INVALID", error_msg)
                    
                    # Sugerir ação baseada no erro
                    if 'INVALID_ID_TOKEN' in error_msg:
                        st.warning("🚨 TOKEN CORROMPIDO - necessário login novamente")
                    elif 'TOKEN_EXPIRED' in error_msg:
                        st.warning("🚨 TOKEN EXPIRADO - tentar renovação")
                        
                except:
                    st.error(f"Erro: {response.text}")
        
        except Exception as e:
            st.error(f"🚨 Erro na validação: {str(e)}")
            self.log_recovery("VALIDATION_EXCEPTION", str(e))
    
    def test_new_token(self, token):
        """Testa se um novo token funciona"""
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.api_key}"
            payload = {"idToken": token}
            
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
            
        except:
            return False
    
    def test_firestore_client(self):
        """Testa o FirestoreClient especificamente"""
        st.subheader("🔥 TESTE FIRESTORE CLIENT")
        
        try:
            from utils.firestore_client import get_firestore_client
            
            st.info("🔄 Criando FirestoreClient...")
            client = get_firestore_client()
            
            if client:
                st.success("✅ FirestoreClient criado")
                st.success(f"✅ Project ID: {client.project_id}")
                st.success(f"✅ Token definido: {'Sim' if client.auth_token else 'Não'}")
                
                if client.auth_token:
                    st.info(f"Token length: {len(client.auth_token)}")
                    
                    # Testar uma operação simples
                    if st.button("🧪 TESTAR OPERAÇÃO FIRESTORE"):
                        self.test_firestore_operation(client)
                else:
                    st.error("❌ FirestoreClient sem token definido")
                    self.log_recovery("FIRESTORE_NO_TOKEN", "Client criado mas sem auth_token")
            else:
                st.error("❌ Falha ao criar FirestoreClient")
                self.log_recovery("FIRESTORE_CLIENT_FAILED", "get_firestore_client retornou None")
        
        except Exception as e:
            st.error(f"🚨 Erro no teste Firestore: {str(e)}")
            st.code(traceback.format_exc())
            self.log_recovery("FIRESTORE_TEST_EXCEPTION", str(e))
    
    def test_firestore_operation(self, client):
        """Testa uma operação real do Firestore"""
        try:
            user_id = st.session_state.user['uid']
            collection_path = f"users/{user_id}/test"
            
            # Testar GET (menos invasivo)
            st.info("🔄 Testando operação GET...")
            
            docs = client.collection(collection_path).get()
            
            if docs is not None:
                st.success(f"✅ GET funcionou - {len(docs)} documentos")
                self.log_recovery("FIRESTORE_GET_SUCCESS", f"GET retornou {len(docs)} docs")
                
                # Testar ADD se GET funcionou
                if st.button("🧪 TESTAR ADD (CRIA DOCUMENTO)"):
                    test_data = {
                        "test": True,
                        "timestamp": datetime.now().isoformat(),
                        "recovery_test": True
                    }
                    
                    try:
                        result = client.collection(collection_path).add(test_data)
                        
                        if result:
                            st.success("✅ ADD funcionou - documento criado")
                            st.json(result)
                            self.log_recovery("FIRESTORE_ADD_SUCCESS", "ADD criou documento")
                        else:
                            st.error("❌ ADD falhou - sem resultado")
                            self.log_recovery("FIRESTORE_ADD_FAILED", "ADD sem resultado")
                            
                    except Exception as add_error:
                        st.error(f"❌ ADD falhou: {str(add_error)}")
                        self.log_recovery("FIRESTORE_ADD_EXCEPTION", str(add_error))
            else:
                st.error("❌ GET falhou - retornou None")
                self.log_recovery("FIRESTORE_GET_FAILED", "GET retornou None")
        
        except Exception as e:
            st.error(f"🚨 Erro na operação: {str(e)}")
            self.log_recovery("FIRESTORE_OPERATION_EXCEPTION", str(e))
    
    def force_relogin(self):
        """Força um novo login"""
        st.subheader("🚨 FORÇANDO NOVO LOGIN")
        
        st.warning("⚠️ Esta ação irá limpar toda a sessão atual")
        
        if st.button("🗑️ CONFIRMAR LOGOUT COMPLETO", type="secondary"):
            # Limpar tudo do session state
            keys_to_clear = list(st.session_state.keys())
            
            for key in keys_to_clear:
                del st.session_state[key]
            
            st.success("✅ Session state limpo completamente")
            self.log_recovery("FORCED_LOGOUT", f"Limpas {len(keys_to_clear)} chaves")
            
            st.info("👉 Acesse app.py para fazer login novamente")
            
            # Rerun para aplicar mudanças
            st.rerun()
    
    def repair_session_state(self):
        """Tenta reparar session state corrompido"""
        st.subheader("🛠️ REPARANDO SESSION STATE")
        
        if 'user' not in st.session_state:
            st.error("❌ Usuário não encontrado - não há o que reparar")
            return
        
        user = st.session_state.user
        repairs = []
        
        # Reparar timestamp ausente
        if 'token' in user and 'token_timestamp' not in user:
            st.session_state.user['token_timestamp'] = datetime.now().isoformat()
            repairs.append("Adicionado token_timestamp")
        
        # Reparar UID ausente
        if 'email' in user and 'uid' not in user:
            # Gerar UID baseado no email (temporário)
            import hashlib
            temp_uid = hashlib.md5(user['email'].encode()).hexdigest()[:20]
            st.session_state.user['uid'] = temp_uid
            repairs.append("Gerado UID temporário baseado no email")
        
        # Verificar estrutura do token
        if 'token' in user and user['token']:
            token = user['token']
            if '.' not in token:  # JWT deve ter pontos
                st.error("❌ Token não é um JWT válido - necessário novo login")
                self.log_recovery("REPAIR_INVALID_JWT", "Token sem estrutura JWT")
            else:
                repairs.append("Token com estrutura JWT válida")
        
        if repairs:
            st.success("✅ Reparos aplicados:")
            for repair in repairs:
                st.success(f"  • {repair}")
                
            self.log_recovery("REPAIR_SUCCESS", f"Aplicados {len(repairs)} reparos")
            
            st.info("🧪 Testando sessão reparada...")
            
            # Testar se reparo funcionou
            if st.button("🔍 TESTAR SESSÃO REPARADA"):
                self.validate_current_token()
        else:
            st.info("ℹ️ Nenhum reparo necessário encontrado")
    
    def log_recovery(self, action, details):
        """Log das ações de recuperação"""
        self.recovery_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })
    
    def show_recovery_log(self):
        """Mostra log das tentativas de recuperação"""
        if self.recovery_log:
            st.header("📋 LOG DE RECUPERAÇÃO")
            
            with st.expander(f"📝 {len(self.recovery_log)} eventos registrados", expanded=False):
                for entry in reversed(self.recovery_log[-10:]):  # Últimas 10
                    timestamp = entry["timestamp"]
                    action = entry["action"]
                    details = entry["details"]
                    
                    st.info(f"**{timestamp}** - {action}")
                    st.caption(details)

def main():
    recovery_system = TokenRecoverySystem()
    recovery_system.main()

if __name__ == "__main__":
    main()