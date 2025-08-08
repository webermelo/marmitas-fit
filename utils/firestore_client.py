# -*- coding: utf-8 -*-
"""
Cliente Firestore para Marmitas Fit
Conexão com banco de dados Firebase usando REST API
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class FirestoreClient:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"
        self.auth_token = None
    
    def set_auth_token(self, token: str):
        """Define o token de autenticação"""
        self.auth_token = token
    
    def _get_headers(self):
        """Retorna headers para requisições"""
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        return headers
    
    def collection(self, collection_name: str):
        """Retorna uma referência de coleção"""
        return FirestoreCollection(self, collection_name)
    
    def _convert_to_firestore_value(self, value):
        """Converte valor Python para formato Firestore"""
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, bool):
            return {"booleanValue": value}
        elif isinstance(value, dict):
            fields = {}
            for k, v in value.items():
                fields[k] = self._convert_to_firestore_value(v)
            return {"mapValue": {"fields": fields}}
        else:
            return {"stringValue": str(value)}
    
    def _convert_from_firestore_value(self, firestore_value):
        """Converte valor Firestore para formato Python"""
        if "stringValue" in firestore_value:
            return firestore_value["stringValue"]
        elif "integerValue" in firestore_value:
            return int(firestore_value["integerValue"])
        elif "doubleValue" in firestore_value:
            return firestore_value["doubleValue"]
        elif "booleanValue" in firestore_value:
            return firestore_value["booleanValue"]
        elif "mapValue" in firestore_value:
            result = {}
            for k, v in firestore_value["mapValue"]["fields"].items():
                result[k] = self._convert_from_firestore_value(v)
            return result
        else:
            return str(firestore_value)

class FirestoreCollection:
    def __init__(self, client: FirestoreClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name
    
    def add(self, data: Dict):
        """Adiciona documento à coleção"""
        url = f"{self.client.base_url}/{self.collection_name}"
        
        # Converter dados para formato Firestore
        firestore_data = {"fields": {}}
        for key, value in data.items():
            firestore_data["fields"][key] = self.client._convert_to_firestore_value(value)
        
        # Debug info (será mostrado via logging no app principal)
        
        response = requests.post(
            url, 
            json=firestore_data,
            headers=self.client._get_headers()
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Erro ao adicionar documento: {response.text}")
    
    def get(self):
        """Lista todos os documentos da coleção"""
        url = f"{self.client.base_url}/{self.collection_name}"
        
        response = requests.get(url, headers=self.client._get_headers())
        
        if response.status_code == 200:
            data = response.json()
            documents = []
            
            if 'documents' in data:
                for doc in data['documents']:
                    doc_data = {}
                    if 'fields' in doc:
                        for key, value in doc['fields'].items():
                            doc_data[key] = self.client._convert_from_firestore_value(value)
                    
                    doc_data['id'] = doc['name'].split('/')[-1]
                    documents.append(doc_data)
            
            return documents
        else:
            # Log error but don't print to console
            return []
    
    def document(self, doc_id: str):
        """Retorna referência para um documento específico"""
        return FirestoreDocument(self.client, self.collection_name, doc_id)

class FirestoreDocument:
    def __init__(self, client: FirestoreClient, collection_name: str, doc_id: str):
        self.client = client
        self.collection_name = collection_name
        self.doc_id = doc_id
    
    def set(self, data: Dict):
        """Define dados do documento"""
        url = f"{self.client.base_url}/{self.collection_name}/{self.doc_id}"
        
        # Converter dados para formato Firestore
        firestore_data = {"fields": {}}
        for key, value in data.items():
            firestore_data["fields"][key] = self.client._convert_to_firestore_value(value)
        
        response = requests.patch(
            url, 
            json=firestore_data,
            headers=self.client._get_headers()
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Erro ao definir documento: {response.text}")
    
    def get(self):
        """Obtém dados do documento"""
        url = f"{self.client.base_url}/{self.collection_name}/{self.doc_id}"
        
        response = requests.get(url, headers=self.client._get_headers())
        
        if response.status_code == 200:
            doc = response.json()
            doc_data = {}
            
            if 'fields' in doc:
                for key, value in doc['fields'].items():
                    doc_data[key] = self.client._convert_from_firestore_value(value)
            
            doc_data['id'] = self.doc_id
            return doc_data
        else:
            return None

@st.cache_resource
def get_firestore_client():
    """Obtém cliente Firestore cached"""
    try:
        # Tentar obter configuração do Streamlit secrets
        config = st.secrets.get("firebase", {})
        if config:
            project_id = config.get("projectId", "marmita-fit-6a3ca")
        else:
            # Fallback para configuração local
            project_id = "marmita-fit-6a3ca"
        
        client = FirestoreClient(project_id)
        
        # Definir token se usuário está autenticado
        if 'user' in st.session_state and 'token' in st.session_state.user:
            client.set_auth_token(st.session_state.user['token'])
        
        return client
        
    except Exception as e:
        st.error(f"Erro ao inicializar Firestore: {e}")
        return None