#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGÊNCIA PRODUÇÃO - OPUS 4.0
Correção definitiva com debug intensivo para produção
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class FixedFirestoreClient:
    """Cliente Firestore com correção FORÇADA para produção"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"
        self.auth_token = None
        
        # DEBUG: Log de inicialização
        st.error(f"🔧 EMERGENCY FIX: FixedFirestoreClient inicializado - {datetime.now().isoformat()}")
    
    def set_auth_token(self, token: str):
        """Define o token de autenticação"""
        self.auth_token = token
        st.error(f"🔑 EMERGENCY FIX: Token configurado - {token[:20] if token else 'NENHUM'}...")
    
    def _get_headers(self):
        """Retorna headers para requisições"""
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        return headers
    
    def collection(self, collection_name: str):
        """Retorna uma referência de coleção"""
        return FixedFirestoreCollection(self, collection_name)
    
    def _convert_to_firestore_value(self, value):
        """
        CORREÇÃO CRÍTICA FORÇADA - PRODUÇÃO
        
        Esta função TEM que funcionar corretamente!
        """
        
        # DEBUG CRÍTICO: Log cada conversão
        st.error(f"🔬 CONVERTING: {value} (type: {type(value).__name__})")
        
        # VERIFICAÇÕES DE TIPO EM ORDEM CRÍTICA
        if isinstance(value, str):
            st.info(f"   -> STRING: {value}")
            return {"stringValue": value}
        
        # 🚨 CRITICAL FIX: BOOL DEVE VIR ANTES DE INT
        elif isinstance(value, bool):
            st.success(f"   -> BOOLEAN DETECTADO: {value} será booleanValue")
            return {"booleanValue": value}
        
        # INT VEM DEPOIS (nunca deve pegar boolean)
        elif isinstance(value, int):
            # Se chegou aqui com boolean, é ERRO CRÍTICO
            if value is True or value is False:
                st.error(f"🚨 ERRO CRÍTICO: Boolean {value} chegou como INT!")
                st.error("🚨 A CORREÇÃO NÃO ESTÁ FUNCIONANDO!")
                # Forçar correção manual
                return {"booleanValue": bool(value)}
            
            st.info(f"   -> INTEGER: {value}")
            return {"integerValue": str(value)}
        
        elif isinstance(value, float):
            st.info(f"   -> FLOAT: {value}")
            return {"doubleValue": value}
        
        elif isinstance(value, dict):
            st.info(f"   -> DICT: {value}")
            fields = {}
            for k, v in value.items():
                fields[k] = self._convert_to_firestore_value(v)
            return {"mapValue": {"fields": fields}}
        
        else:
            st.warning(f"   -> FALLBACK STRING: {value}")
            return {"stringValue": str(value)}

class FixedFirestoreCollection:
    """Coleção com correção forçada"""
    
    def __init__(self, client: FixedFirestoreClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name
        
        st.error(f"📁 EMERGENCY COLLECTION: {collection_name}")
    
    def add(self, data: Dict):
        """Adiciona documento à coleção com DEBUG INTENSIVO"""
        
        st.error(f"💾 EMERGENCY ADD INICIADO: {len(data)} campos")
        
        url = f"{self.client.base_url}/{self.collection_name}"
        
        # Converter dados para formato Firestore com DEBUG
        firestore_data = {"fields": {}}
        
        st.error("🔄 CONVERTENDO CAMPOS:")
        
        for i, (key, value) in enumerate(data.items()):
            st.error(f"   Campo {i}: {key} = {value} ({type(value).__name__})")
            
            converted = self.client._convert_to_firestore_value(value)
            firestore_data["fields"][key] = converted
            
            # Verificar se boolean foi convertido corretamente
            if isinstance(value, bool):
                if "booleanValue" in converted:
                    st.success(f"   ✅ Campo {i}: Boolean OK - {converted}")
                else:
                    st.error(f"   ❌ Campo {i}: Boolean ERRO - {converted}")
        
        # Mostrar dados finais antes do envio
        st.error("📤 DADOS FINAIS PARA FIREBASE:")
        st.json(firestore_data)
        
        # Enviar para Firebase
        response = requests.post(
            url, 
            json=firestore_data,
            headers=self.client._get_headers()
        )
        
        st.error(f"📨 RESPOSTA FIREBASE: Status {response.status_code}")
        
        if response.status_code in [200, 201]:
            st.success("✅ SUCESSO NO FIREBASE!")
            return response.json()
        else:
            error_text = response.text
            st.error(f"❌ ERRO FIREBASE: {error_text}")
            
            # Analisar erro específico
            if "integer_value" in error_text and "True" in error_text:
                st.error("🚨 CONFIRMADO: Boolean ainda sendo convertido como INTEGER!")
                st.error("🚨 A CORREÇÃO NÃO ESTÁ ATIVA EM PRODUÇÃO!")
            
            raise Exception(f"EMERGENCY ERROR: {error_text}")
    
    def get(self):
        """Lista documentos com debug"""
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
                            doc_data[key] = self._convert_from_firestore_value(value)
                    
                    doc_data['id'] = doc['name'].split('/')[-1]
                    documents.append(doc_data)
            
            return documents
        elif response.status_code == 404:
            return []
        else:
            raise Exception(f"ERRO na leitura: {response.text}")
    
    def _convert_from_firestore_value(self, firestore_value):
        """Converte valor Firestore para Python"""
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

def get_emergency_firestore_client():
    """
    Cliente de emergência FORÇADO para produção
    
    Este cliente TEM que usar a conversão correta!
    """
    
    try:
        # Obter token válido
        if 'user' not in st.session_state:
            st.error("❌ EMERGENCY: Usuário não logado")
            return None
        
        token = st.session_state.user.get('token')
        if not token:
            st.error("❌ EMERGENCY: Token não encontrado")
            return None
        
        # Configuração Firebase
        try:
            config = st.secrets.get("firebase", {})
            project_id = config.get("projectId", "marmita-fit-6a3ca")
        except:
            project_id = "marmita-fit-6a3ca"
        
        # Criar cliente FORÇADO
        client = FixedFirestoreClient(project_id)
        client.set_auth_token(token)
        
        st.error(f"🚨 EMERGENCY CLIENT CRIADO: {project_id}")
        
        return client
        
    except Exception as e:
        st.error(f"❌ ERRO EMERGENCY CLIENT: {e}")
        return None

def test_emergency_fix():
    """Teste do fix de emergência"""
    
    st.title("🚨 TESTE EMERGENCIAL - OPUS 4.0")
    st.markdown("---")
    
    st.error("🔬 TESTANDO CORREÇÃO FORÇADA EM PRODUÇÃO")
    
    # Obter cliente de emergência
    client = get_emergency_firestore_client()
    
    if not client:
        st.error("❌ Não foi possível criar cliente de emergência")
        return
    
    # Dados de teste com boolean
    test_data = {
        "nome": "TESTE_EMERGENCY_PRODUCAO",
        "categoria": "Teste",
        "preco": 99.99,
        "ativo": True,  # CAMPO CRÍTICO
        "observacoes": f"Emergency test {datetime.now().isoformat()}"
    }
    
    st.error("📋 DADOS DE TESTE:")
    st.json(test_data)
    
    if st.button("🚀 EXECUTAR TESTE EMERGENCIAL"):
        try:
            user_id = st.session_state.user['uid']
            collection_path = f"users/{user_id}/ingredients"
            
            st.error(f"📍 SALVANDO EM: {collection_path}")
            
            # Usar cliente de emergência
            result = client.collection(collection_path).add(test_data)
            
            if result:
                st.balloons()
                st.success("🎉 SUCESSO! Correção funcionando em produção!")
            else:
                st.error("❌ Falhou mesmo com correção forçada")
                
        except Exception as e:
            st.error(f"🚨 ERRO NO TESTE: {str(e)}")
            st.code(str(e))

if __name__ == "__main__":
    test_emergency_fix()