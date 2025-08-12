# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Tokens Firebase
Correção crítica para o problema de persistência de dados
"""

import streamlit as st
from datetime import datetime, timedelta
import requests
import json
from typing import Optional, Dict, Any

class TokenManager:
    """Gerenciador robusto de tokens Firebase com renovação automática"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> str:
        """Obtém API key do Firebase"""
        try:
            config = st.secrets.get("firebase", {})
            if config:
                return config.get("apiKey", "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90")
            return "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
        except:
            return "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
    
    def is_token_expired(self, token_timestamp: Optional[str] = None) -> bool:
        """Verifica se o token está expirado (Firebase tokens duram 1 hora)"""
        if not token_timestamp:
            return True
        
        try:
            token_time = datetime.fromisoformat(token_timestamp)
            # Considerar expirado após 50 minutos (margem de segurança)
            expiry_time = token_time + timedelta(minutes=50)
            return datetime.now() > expiry_time
        except:
            return True
    
    def get_valid_token(self) -> Optional[str]:
        """
        Retorna token válido, renovando automaticamente se necessário
        
        Esta é a função CRÍTICA que resolve o problema de persistência
        """
        if 'user' not in st.session_state:
            st.error("❌ Usuário não está logado")
            return None
        
        user = st.session_state.user
        
        # Verificar se token existe
        if 'token' not in user:
            st.error("❌ Token não encontrado na sessão")
            return None
        
        # Verificar se token tem timestamp
        token_timestamp = user.get('token_timestamp')
        if not token_timestamp:
            # Adicionar timestamp atual se não existir
            st.session_state.user['token_timestamp'] = datetime.now().isoformat()
            return user['token']
        
        # Verificar se token está expirado
        if self.is_token_expired(token_timestamp):
            st.warning("🔄 Token expirado, renovando...")
            
            # Tentar renovar token
            new_token = self.refresh_token(user.get('refresh_token'))
            if new_token:
                st.session_state.user['token'] = new_token['token']
                st.session_state.user['token_timestamp'] = datetime.now().isoformat()
                if 'refresh_token' in new_token:
                    st.session_state.user['refresh_token'] = new_token['refresh_token']
                st.success("✅ Token renovado com sucesso")
                return new_token['token']
            else:
                st.error("❌ Falha ao renovar token - usuário precisa fazer login novamente")
                return None
        
        # Token válido
        return user['token']
    
    def refresh_token(self, refresh_token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Renova token Firebase usando refresh_token"""
        if not refresh_token:
            return None
        
        try:
            url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
            
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "token": data["id_token"],
                    "refresh_token": data.get("refresh_token", refresh_token)
                }
            else:
                st.error(f"❌ Erro ao renovar token: {response.status_code}")
                return None
        
        except Exception as e:
            st.error(f"❌ Exceção ao renovar token: {str(e)}")
            return None
    
    def validate_token(self, token: str) -> bool:
        """Valida se token é válido fazendo uma chamada de teste"""
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.api_key}"
            payload = {"idToken": token}
            
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        
        except:
            return False

# Instância global para uso na aplicação
token_manager = TokenManager()

def get_valid_token() -> Optional[str]:
    """Função de conveniência para obter token válido"""
    return token_manager.get_valid_token()

def is_token_valid(token: str) -> bool:
    """Função de conveniência para validar token"""
    return token_manager.validate_token(token)

def ensure_token_timestamp():
    """Garante que o token atual tenha timestamp"""
    if 'user' in st.session_state and 'token' in st.session_state.user:
        if 'token_timestamp' not in st.session_state.user:
            st.session_state.user['token_timestamp'] = datetime.now().isoformat()