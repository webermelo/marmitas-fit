# -*- coding: utf-8 -*-
"""
Configurações do Firebase para Marmitas Fit Web App
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
import pyrebase

# Configuração do Firebase usando Streamlit Secrets (seguro para deploy)
try:
    # Em produção (Streamlit Cloud) - usar secrets
    FIREBASE_CONFIG = {
        "apiKey": st.secrets["firebase"]["apiKey"],
        "authDomain": st.secrets["firebase"]["authDomain"],
        "projectId": st.secrets["firebase"]["projectId"],
        "storageBucket": st.secrets["firebase"]["storageBucket"],
        "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
        "appId": st.secrets["firebase"]["appId"],
        "measurementId": st.secrets["firebase"]["measurementId"],
        "databaseURL": st.secrets["firebase"]["databaseURL"]
    }
except (KeyError, AttributeError):
    # Em desenvolvimento local - usar credenciais diretas
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90",
        "authDomain": "marmita-fit-6a3ca.firebaseapp.com", 
        "projectId": "marmita-fit-6a3ca",
        "storageBucket": "marmita-fit-6a3ca.firebasestorage.app",
        "messagingSenderId": "183148230819",
        "appId": "1:183148230819:web:c72f2a2c545ea0f443a716",
        "measurementId": "G-1XD2XZTWGC",
        "databaseURL": "https://marmita-fit-6a3ca-default-rtdb.firebaseio.com/"
    }

class FirebaseManager:
    def __init__(self):
        self.db = None
        self.auth = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Inicializa Firebase Admin e Pyrebase"""
        try:
            # Inicializar Pyrebase para autenticação (mais simples)
            firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            self.auth = firebase.auth()
            
            # Se chegou até aqui, Firebase está funcionando
            print("✅ Firebase inicializado com sucesso!")
            
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Firebase: {e}")
            # Usar modo offline/demo
            self.db = None
            self.auth = None
    
    def get_firestore_client(self):
        """Retorna cliente do Firestore"""
        return self.db
    
    def get_auth_client(self):
        """Retorna cliente de autenticação"""
        return self.auth

# Instância global do Firebase Manager
def get_firebase_manager():
    if 'firebase_manager' not in st.session_state:
        st.session_state.firebase_manager = FirebaseManager()
    return st.session_state.firebase_manager

# Coleções do Firestore
COLLECTIONS = {
    "users": "usuarios",
    "ingredients": "ingredientes", 
    "recipes": "receitas",
    "productions": "producoes"
}