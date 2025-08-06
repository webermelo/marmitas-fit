# -*- coding: utf-8 -*-
"""
Firebase Authentication usando REST API direta
Solução sem pyrebase4 para compatibilidade com Streamlit Cloud
"""

import streamlit as st
import requests
import json
from typing import Dict, Optional

class FirebaseAuth:
    def __init__(self, api_key: str, auth_domain: str):
        self.api_key = api_key
        self.auth_domain = auth_domain
        self.base_url = f"https://identitytoolkit.googleapis.com/v1/accounts"
    
    def sign_up_with_email_password(self, email: str, password: str, display_name: str = None) -> Dict:
        """Criar conta no Firebase"""
        url = f"{self.base_url}:signUp?key={self.api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        if display_name:
            payload["displayName"] = display_name
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user": {
                    "uid": data["localId"],
                    "email": data["email"],
                    "token": data["idToken"],
                    "refresh_token": data["refreshToken"],
                    "display_name": display_name or email.split("@")[0]
                }
            }
        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Erro desconhecido")
            return {
                "success": False,
                "error": self._translate_error(error_message)
            }
    
    def sign_in_with_email_password(self, email: str, password: str) -> Dict:
        """Fazer login no Firebase"""
        url = f"{self.base_url}:signInWithPassword?key={self.api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user": {
                    "uid": data["localId"],
                    "email": data["email"],
                    "token": data["idToken"],
                    "refresh_token": data["refreshToken"],
                    "display_name": data.get("displayName", email.split("@")[0])
                }
            }
        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Erro desconhecido")
            return {
                "success": False,
                "error": self._translate_error(error_message)
            }
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Renovar token de acesso"""
        url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data["id_token"],
                "refresh_token": data["refresh_token"]
            }
        else:
            return {"success": False, "error": "Erro ao renovar token"}
    
    def verify_token(self, token: str) -> Dict:
        """Verificar se token é válido"""
        url = f"{self.base_url}:lookup?key={self.api_key}"
        
        payload = {
            "idToken": token
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            user_data = data["users"][0]
            return {
                "success": True,
                "user": {
                    "uid": user_data["localId"],
                    "email": user_data["email"],
                    "display_name": user_data.get("displayName", user_data["email"].split("@")[0])
                }
            }
        else:
            return {"success": False, "error": "Token inválido"}
    
    def _translate_error(self, error_message: str) -> str:
        """Traduzir mensagens de erro do Firebase"""
        error_translations = {
            "EMAIL_EXISTS": "Este email já está em uso",
            "OPERATION_NOT_ALLOWED": "Operação não permitida",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Muitas tentativas. Tente novamente mais tarde",
            "EMAIL_NOT_FOUND": "Email não encontrado. Você precisa criar uma conta primeiro.",
            "INVALID_PASSWORD": "Senha incorreta",
            "INVALID_LOGIN_CREDENTIALS": "Email ou senha incorretos. Verifique suas credenciais.",
            "USER_DISABLED": "Usuário desabilitado",
            "INVALID_EMAIL": "Email inválido",
            "WEAK_PASSWORD": "Senha muito fraca. Use pelo menos 6 caracteres"
        }
        
        return error_translations.get(error_message, f"Erro: {error_message}")

# Função para obter instância do Firebase Auth
@st.cache_resource
def get_firebase_auth():
    """Obter instância cached do Firebase Auth"""
    try:
        # Tentar usar secrets primeiro
        config = st.secrets.get("firebase", {})
        if config:
            api_key = config["apiKey"]
            auth_domain = config["authDomain"]
        else:
            # Fallback para configuração local
            api_key = "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
            auth_domain = "marmita-fit-6a3ca.firebaseapp.com"
        
        return FirebaseAuth(api_key, auth_domain)
    
    except Exception as e:
        st.error(f"Erro ao inicializar Firebase: {e}")
        return None