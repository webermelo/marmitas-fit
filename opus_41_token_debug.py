#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPUS 4.1 DEEP TOKEN ANALYSIS
Investigação profunda do problema de token Firebase
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time
import traceback
import base64

class Opus41TokenDebugger:
    """Debug profundo de tokens Firebase usando análise Opus 4.1"""
    
    def __init__(self):
        self.api_key = self._get_firebase_api_key()
        self.analysis_results = {
            "session_state": {},
            "token_validation": {},
            "token_structure": {},
            "refresh_attempts": [],
            "firebase_responses": [],
            "timeline": []
        }
    
    def _get_firebase_api_key(self):
        """Obtém API key com fallbacks múltiplos"""
        try:
            # Método 1: Streamlit secrets
            if hasattr(st, 'secrets'):
                config = st.secrets.get("firebase", {})
                if config and "apiKey" in config:
                    return config["apiKey"]
            
            # Método 2: Config local
            from config.firebase_config import FIREBASE_CONFIG
            if "apiKey" in FIREBASE_CONFIG:
                return FIREBASE_CONFIG["apiKey"]
            
            # Método 3: Fallback hardcoded
            return "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
            
        except Exception as e:
            st.error(f"🚨 OPUS 4.1: Erro ao obter API Key: {e}")
            return "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
    
    def main(self):
        st.set_page_config(
            page_title="OPUS 4.1 Token Debug",
            page_icon="🔬",
            layout="wide"
        )
        
        st.title("🔬 OPUS 4.1 DEEP TOKEN ANALYSIS")
        st.markdown("---")
        
        st.error("🚨 INVESTIGAÇÃO PROFUNDA: Token inválido Firebase")
        
        # Análise 1: Estado da Sessão
        self.analyze_session_state()
        
        # Análise 2: Estrutura do Token
        self.analyze_token_structure()
        
        # Análise 3: Validação do Token
        self.validate_token_direct()
        
        # Análise 4: Tentativa de Renovação
        self.attempt_token_refresh()
        
        # Análise 5: Timeline de Eventos
        self.create_event_timeline()
        
        # Análise 6: Diagnóstico Final
        self.final_diagnosis()
    
    def analyze_session_state(self):
        """Análise profunda do estado da sessão"""
        st.header("🔍 ANÁLISE 1: Estado da Sessão")
        
        self.log_event("SESSION_ANALYSIS", "Iniciando análise do session_state")
        
        if 'user' not in st.session_state:
            st.error("❌ CRITICAL: 'user' ausente no session_state")
            self.analysis_results["session_state"]["has_user"] = False
            self.log_event("CRITICAL_ERROR", "user não encontrado no session_state")
            return
        
        user = st.session_state.user
        self.analysis_results["session_state"]["has_user"] = True
        
        # Verificar campos obrigatórios
        required_fields = ['uid', 'token', 'email']
        missing_fields = []
        
        for field in required_fields:
            if field not in user:
                missing_fields.append(field)
                st.error(f"❌ Campo ausente: {field}")
            else:
                st.success(f"✅ Campo presente: {field}")
        
        self.analysis_results["session_state"]["missing_fields"] = missing_fields
        
        # Análise do token
        if 'token' in user:
            token = user['token']
            
            st.subheader("🔑 ANÁLISE DO TOKEN")
            st.info(f"Token length: {len(token) if token else 0} caracteres")
            st.info(f"Token preview: {token[:50] if token else 'NENHUM'}...")
            
            # Verificar timestamp do token
            token_timestamp = user.get('token_timestamp')
            if token_timestamp:
                try:
                    token_time = datetime.fromisoformat(token_timestamp)
                    age = datetime.now() - token_time
                    st.info(f"Token age: {age.total_seconds():.0f} segundos")
                    
                    # Firebase tokens duram 1 hora
                    if age.total_seconds() > 3600:
                        st.error(f"❌ TOKEN EXPIRADO! Idade: {age.total_seconds():.0f}s > 3600s")
                        self.analysis_results["session_state"]["token_expired"] = True
                    else:
                        st.success(f"✅ Token dentro da validade: {age.total_seconds():.0f}s < 3600s")
                        self.analysis_results["session_state"]["token_expired"] = False
                        
                except Exception as e:
                    st.error(f"❌ Erro ao analisar timestamp: {e}")
            else:
                st.warning("⚠️ Token sem timestamp - impossível verificar expiração")
                self.analysis_results["session_state"]["no_timestamp"] = True
        
        # Mostrar dados completos da sessão
        with st.expander("📋 Session State Completo", expanded=False):
            # Censurar token sensível
            safe_user = user.copy()
            if 'token' in safe_user and safe_user['token']:
                safe_user['token'] = f"{safe_user['token'][:20]}...{safe_user['token'][-10:]}"
            if 'refresh_token' in safe_user and safe_user['refresh_token']:
                safe_user['refresh_token'] = f"{safe_user['refresh_token'][:20]}...{safe_user['refresh_token'][-10:]}"
            
            st.json(safe_user)
    
    def analyze_token_structure(self):
        """Análise da estrutura JWT do token"""
        st.header("🧬 ANÁLISE 2: Estrutura do Token")
        
        if 'user' not in st.session_state or 'token' not in st.session_state.user:
            st.error("❌ Token não disponível para análise")
            return
        
        token = st.session_state.user['token']
        
        try:
            # JWT tem 3 partes separadas por pontos
            parts = token.split('.')
            
            st.info(f"JWT Parts: {len(parts)} (esperado: 3)")
            
            if len(parts) != 3:
                st.error("❌ ESTRUTURA JWT INVÁLIDA: Não tem 3 partes")
                self.analysis_results["token_structure"]["valid_jwt"] = False
                return
            
            self.analysis_results["token_structure"]["valid_jwt"] = True
            
            # Decodificar header (parte 1)
            try:
                # Adicionar padding se necessário
                header_b64 = parts[0] + '=' * (4 - len(parts[0]) % 4)
                header_json = base64.urlsafe_b64decode(header_b64)
                header = json.loads(header_json)
                
                st.subheader("📄 JWT Header")
                st.json(header)
                
                self.analysis_results["token_structure"]["header"] = header
                
            except Exception as e:
                st.error(f"❌ Erro ao decodificar header: {e}")
            
            # Decodificar payload (parte 2)
            try:
                # Adicionar padding se necessário
                payload_b64 = parts[1] + '=' * (4 - len(parts[1]) % 4)
                payload_json = base64.urlsafe_b64decode(payload_b64)
                payload = json.loads(payload_json)
                
                st.subheader("📋 JWT Payload")
                
                # Verificar campos importantes
                important_fields = ['exp', 'iat', 'aud', 'iss', 'sub', 'auth_time']
                
                for field in important_fields:
                    if field in payload:
                        if field in ['exp', 'iat', 'auth_time']:
                            # Converter timestamp para data legível
                            timestamp = payload[field]
                            readable_date = datetime.fromtimestamp(timestamp).isoformat()
                            st.info(f"{field}: {timestamp} ({readable_date})")
                        else:
                            st.info(f"{field}: {payload[field]}")
                
                # Verificar expiração
                if 'exp' in payload:
                    exp_time = datetime.fromtimestamp(payload['exp'])
                    now = datetime.now()
                    
                    if now > exp_time:
                        st.error(f"❌ TOKEN JWT EXPIRADO! Expirou em: {exp_time}")
                        self.analysis_results["token_structure"]["jwt_expired"] = True
                    else:
                        remaining = exp_time - now
                        st.success(f"✅ Token JWT válido por mais: {remaining.total_seconds():.0f} segundos")
                        self.analysis_results["token_structure"]["jwt_expired"] = False
                
                # Mostrar payload completo (censurado)
                safe_payload = payload.copy()
                for sensitive_field in ['email', 'phone_number']:
                    if sensitive_field in safe_payload:
                        safe_payload[sensitive_field] = "***CENSURADO***"
                
                with st.expander("📋 Payload Completo", expanded=False):
                    st.json(safe_payload)
                
                self.analysis_results["token_structure"]["payload"] = safe_payload
                
            except Exception as e:
                st.error(f"❌ Erro ao decodificar payload: {e}")
                st.code(traceback.format_exc())
        
        except Exception as e:
            st.error(f"❌ Erro na análise da estrutura: {e}")
    
    def validate_token_direct(self):
        """Validação direta do token com Firebase"""
        st.header("🔐 ANÁLISE 3: Validação Direta Firebase")
        
        if 'user' not in st.session_state or 'token' not in st.session_state.user:
            st.error("❌ Token não disponível para validação")
            return
        
        token = st.session_state.user['token']
        
        # Endpoint de validação do Firebase
        validation_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.api_key}"
        
        payload = {"idToken": token}
        
        try:
            st.info("🔄 Validando token com Firebase Identity Toolkit...")
            
            response = requests.post(
                validation_url,
                json=payload,
                timeout=10
            )
            
            self.analysis_results["token_validation"]["status_code"] = response.status_code
            self.analysis_results["token_validation"]["response_time"] = time.time()
            
            st.info(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Token válido
                data = response.json()
                st.success("✅ TOKEN VÁLIDO! Firebase confirmou autenticação")
                
                if 'users' in data and len(data['users']) > 0:
                    user_info = data['users'][0]
                    st.success(f"✅ Usuário autenticado: {user_info.get('email', 'N/A')}")
                    
                    # Informações do usuário
                    important_user_fields = ['localId', 'email', 'emailVerified', 'lastLoginAt', 'createdAt']
                    for field in important_user_fields:
                        if field in user_info:
                            st.info(f"{field}: {user_info[field]}")
                    
                    self.analysis_results["token_validation"]["valid"] = True
                    self.analysis_results["token_validation"]["user_info"] = user_info
                
            elif response.status_code == 400:
                # Token inválido
                error_data = response.json()
                st.error("❌ TOKEN INVÁLIDO! Firebase rejeitou")
                
                if 'error' in error_data:
                    error_info = error_data['error']
                    st.error(f"Código: {error_info.get('code', 'N/A')}")
                    st.error(f"Mensagem: {error_info.get('message', 'N/A')}")
                    
                    # Analisar tipo específico do erro
                    message = error_info.get('message', '').lower()
                    if 'expired' in message:
                        st.error("🚨 CAUSA: Token expirado")
                    elif 'malformed' in message:
                        st.error("🚨 CAUSA: Token malformado")
                    elif 'invalid' in message:
                        st.error("🚨 CAUSA: Token inválido ou revogado")
                
                self.analysis_results["token_validation"]["valid"] = False
                self.analysis_results["token_validation"]["error"] = error_data
                
                with st.expander("📋 Detalhes do Erro", expanded=False):
                    st.json(error_data)
            
            else:
                # Outro erro
                st.error(f"🚨 ERRO HTTP {response.status_code}")
                st.error(f"Response: {response.text}")
                
                self.analysis_results["token_validation"]["valid"] = False
                self.analysis_results["token_validation"]["http_error"] = response.status_code
        
        except requests.exceptions.RequestException as e:
            st.error(f"🚨 ERRO DE REDE: {str(e)}")
            self.analysis_results["token_validation"]["network_error"] = str(e)
        
        except Exception as e:
            st.error(f"🚨 ERRO INESPERADO: {str(e)}")
            st.code(traceback.format_exc())
    
    def attempt_token_refresh(self):
        """Tentativa de renovação do token"""
        st.header("🔄 ANÁLISE 4: Tentativa de Renovação")
        
        if 'user' not in st.session_state:
            st.error("❌ Usuário não disponível para renovação")
            return
        
        user = st.session_state.user
        refresh_token = user.get('refresh_token')
        
        if not refresh_token:
            st.error("❌ Refresh token não disponível")
            self.analysis_results["refresh_attempts"].append({
                "timestamp": datetime.now().isoformat(),
                "status": "NO_REFRESH_TOKEN"
            })
            return
        
        st.info(f"Refresh token disponível: {refresh_token[:20]}...")
        
        # Endpoint de refresh do Firebase
        refresh_url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            st.info("🔄 Tentando renovar token...")
            
            response = requests.post(
                refresh_url,
                json=payload,
                timeout=10
            )
            
            refresh_attempt = {
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ TOKEN RENOVADO COM SUCESSO!")
                
                new_token = data.get("id_token")
                new_refresh_token = data.get("refresh_token", refresh_token)
                
                if new_token:
                    st.info(f"Novo token: {new_token[:20]}...")
                    
                    # Atualizar session state
                    st.session_state.user['token'] = new_token
                    st.session_state.user['refresh_token'] = new_refresh_token
                    st.session_state.user['token_timestamp'] = datetime.now().isoformat()
                    
                    st.success("✅ Session state atualizado com novo token")
                    
                    refresh_attempt["new_token_length"] = len(new_token)
                    refresh_attempt["token_updated"] = True
                else:
                    st.error("❌ Resposta sem novo token")
                    refresh_attempt["token_updated"] = False
            
            else:
                st.error(f"❌ FALHA NA RENOVAÇÃO: {response.status_code}")
                error_text = response.text
                st.error(f"Erro: {error_text}")
                
                refresh_attempt["error"] = error_text
                
                # Analisar erro específico
                if response.status_code == 400:
                    st.error("🚨 Refresh token inválido ou expirado")
                elif response.status_code == 401:
                    st.error("🚨 Não autorizado - API key inválida?")
            
            self.analysis_results["refresh_attempts"].append(refresh_attempt)
        
        except Exception as e:
            st.error(f"🚨 ERRO na renovação: {str(e)}")
            
            refresh_attempt = {
                "timestamp": datetime.now().isoformat(),
                "status": "EXCEPTION",
                "error": str(e)
            }
            
            self.analysis_results["refresh_attempts"].append(refresh_attempt)
    
    def create_event_timeline(self):
        """Cria timeline de eventos de autenticação"""
        st.header("📅 ANÁLISE 5: Timeline de Eventos")
        
        events = []
        
        # Evento de login (baseado em timestamps disponíveis)
        if 'user' in st.session_state:
            user = st.session_state.user
            
            if 'token_timestamp' in user:
                events.append({
                    "time": user['token_timestamp'],
                    "event": "TOKEN_CREATED",
                    "description": "Token criado/renovado"
                })
            
            # Adicionar outros eventos dos analysis_results
            for attempt in self.analysis_results.get("refresh_attempts", []):
                events.append({
                    "time": attempt["timestamp"],
                    "event": "REFRESH_ATTEMPT",
                    "description": f"Tentativa renovação: {attempt.get('status', 'Unknown')}"
                })
        
        # Ordenar por tempo
        events.sort(key=lambda x: x["time"])
        
        if events:
            st.subheader("📋 Timeline de Autenticação")
            
            for i, event in enumerate(events):
                try:
                    event_time = datetime.fromisoformat(event["time"])
                    time_ago = datetime.now() - event_time
                    
                    st.info(f"**{event['event']}** - {event_time.strftime('%H:%M:%S')} ({time_ago.total_seconds():.0f}s atrás)")
                    st.caption(event['description'])
                    
                except Exception as e:
                    st.info(f"**{event['event']}** - {event['time']}")
        else:
            st.warning("⚠️ Nenhum evento de timeline encontrado")
    
    def final_diagnosis(self):
        """Diagnóstico final baseado em toda a análise"""
        st.header("🎯 ANÁLISE 6: Diagnóstico Final OPUS 4.1")
        
        # Compilar descobertas
        issues = []
        recommendations = []
        
        # Análise de session state
        if not self.analysis_results["session_state"].get("has_user", False):
            issues.append("❌ CRÍTICO: Usuário não está logado")
            recommendations.append("🔧 Fazer login novamente")
        
        if self.analysis_results["session_state"].get("missing_fields"):
            missing = self.analysis_results["session_state"]["missing_fields"]
            issues.append(f"❌ Campos ausentes: {missing}")
            recommendations.append("🔧 Login corrompido - fazer logout/login")
        
        if self.analysis_results["session_state"].get("token_expired", False):
            issues.append("❌ Token expirado por idade")
            recommendations.append("🔧 Implementar renovação automática")
        
        if self.analysis_results["session_state"].get("no_timestamp", False):
            issues.append("⚠️ Token sem timestamp")
            recommendations.append("🔧 Adicionar timestamp no próximo login")
        
        # Análise de estrutura JWT
        if not self.analysis_results["token_structure"].get("valid_jwt", False):
            issues.append("❌ CRÍTICO: Estrutura JWT inválida")
            recommendations.append("🔧 Regenerar token através de novo login")
        
        if self.analysis_results["token_structure"].get("jwt_expired", False):
            issues.append("❌ Token JWT expirado")
            recommendations.append("🔧 Renovar token ou fazer novo login")
        
        # Análise de validação
        if not self.analysis_results["token_validation"].get("valid", True):
            issues.append("❌ CRÍTICO: Firebase rejeitou token")
            recommendations.append("🔧 Token inválido - fazer logout e login novamente")
        
        # Análise de renovação
        failed_refreshes = [a for a in self.analysis_results.get("refresh_attempts", []) if not a.get("success", False)]
        if failed_refreshes:
            issues.append(f"❌ {len(failed_refreshes)} falhas na renovação")
            recommendations.append("🔧 Refresh token inválido - fazer login manual")
        
        # Apresentar diagnóstico
        st.subheader("🔍 PROBLEMAS IDENTIFICADOS")
        
        if issues:
            for issue in issues:
                st.error(issue)
        else:
            st.success("✅ Nenhum problema crítico identificado")
        
        st.subheader("💡 RECOMENDAÇÕES")
        
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success("✅ Sistema aparenta estar funcionando corretamente")
        
        # Diagnóstico específico mais provável
        st.subheader("🎯 DIAGNÓSTICO MAIS PROVÁVEL")
        
        if not self.analysis_results["token_validation"].get("valid", True):
            st.error("🚨 **TOKEN INVÁLIDO/EXPIRADO**")
            st.error("**Causa raiz**: Token Firebase não é mais aceito pelo servidor")
            st.info("**Solução**: Forçar logout e login novamente")
            
            if st.button("🔄 FORÇAR LOGOUT AGORA", type="primary"):
                # Limpar session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Session state limpo - faça login novamente")
                st.rerun()
        
        elif self.analysis_results["session_state"].get("token_expired", False):
            st.warning("⚠️ **TOKEN EXPIRADO POR TEMPO**")
            st.info("**Causa raiz**: Token passou da validade de 1 hora")
            st.info("**Solução**: Implementar renovação automática")
        
        else:
            st.info("ℹ️ **INVESTIGAÇÃO ADICIONAL NECESSÁRIA**")
            st.info("Token parece válido mas Firebase Client não consegue usar")
            st.info("Possível problema na implementação do FirestoreClient")
        
        # Log de análise completa
        self.log_event("ANALYSIS_COMPLETE", f"Encontrados {len(issues)} problemas")
        
        with st.expander("📋 Análise Completa (JSON)", expanded=False):
            st.json(self.analysis_results)
    
    def log_event(self, event_type, description):
        """Log de evento para timeline"""
        self.analysis_results["timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "description": description
        })

def main():
    debugger = Opus41TokenDebugger()
    debugger.main()

if __name__ == "__main__":
    main()