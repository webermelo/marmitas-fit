#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG UPLOAD PARCIAL - OPUS 4.0
Investigação profunda do problema de upload parcial
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import time
import traceback

class PartialUploadDebugger:
    """Debugger específico para problema de upload parcial"""
    
    def __init__(self):
        self.results = {
            "total_attempted": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "failed_items": []
        }
    
    def main(self):
        st.set_page_config(
            page_title="Debug Upload Parcial - Opus 4.0",
            page_icon="🔬",
            layout="wide"
        )
        
        st.title("🔬 DEBUG UPLOAD PARCIAL - OPUS 4.0")
        st.markdown("---")
        
        if 'user' not in st.session_state:
            st.error("❌ Usuário não logado - acesse app.py primeiro")
            return
        
        user_id = st.session_state.user['uid']
        st.success(f"✅ Usuário logado: {user_id}")
        
        # Análise 1: Verificar quantos ingredientes existem atualmente
        st.header("📊 ANÁLISE 1: Estado Atual do Firebase")
        
        if st.button("🔍 VERIFICAR INGREDIENTES ATUAIS"):
            self.check_current_ingredients(user_id)
        
        # Análise 2: Analisar arquivo CSV original
        st.header("📋 ANÁLISE 2: Arquivo CSV Original")
        
        uploaded_file = st.file_uploader(
            "📤 Faça upload do mesmo CSV que causou problema",
            type=['csv']
        )
        
        if uploaded_file:
            self.analyze_csv_file(uploaded_file)
        
        # Análise 3: Teste de upload controlado
        st.header("🧪 ANÁLISE 3: Upload Controlado com Debug")
        
        if uploaded_file and st.button("🚀 EXECUTAR UPLOAD CONTROLADO"):
            self.controlled_upload_test(uploaded_file, user_id)
        
        # Análise 4: Comparação e identificação de faltantes
        st.header("📈 ANÁLISE 4: Comparação CSV vs Firebase")
        
        if st.button("🔎 IDENTIFICAR INGREDIENTES FALTANTES"):
            self.compare_csv_vs_firebase(uploaded_file, user_id)
    
    def check_current_ingredients(self, user_id):
        """Verifica quantos ingredientes existem atualmente"""
        try:
            from utils.database import get_database_manager
            
            db_manager = get_database_manager()
            
            st.info("🔄 Carregando ingredientes atuais...")
            
            # Carregar ingredientes via DatabaseManager
            current_df = db_manager.get_user_ingredients(user_id)
            
            st.subheader("📊 RESULTADOS ATUAIS")
            
            if current_df.empty:
                st.error("❌ NENHUM ingrediente encontrado no Firebase")
                st.error("🚨 PROBLEMA GRAVE: Upload falhou completamente")
            else:
                count = len(current_df)
                st.success(f"✅ {count} ingredientes encontrados no Firebase")
                
                if count < 198:
                    st.warning(f"⚠️ UPLOAD PARCIAL: Esperados 198, encontrados {count}")
                    st.error(f"❌ FALTANDO: {198 - count} ingredientes")
                elif count == 198:
                    st.success("🎉 TODOS OS 198 INGREDIENTES PRESENTES!")
                else:
                    st.info(f"ℹ️ Encontrados {count} ingredientes (mais que 198)")
                
                # Mostrar amostra
                st.subheader("📋 AMOSTRA DOS INGREDIENTES ATUAIS")
                st.dataframe(current_df.head(10))
                
                # Estatísticas por categoria
                if 'Categoria' in current_df.columns:
                    st.subheader("📊 INGREDIENTES POR CATEGORIA")
                    category_counts = current_df['Categoria'].value_counts()
                    st.bar_chart(category_counts)
        
        except Exception as e:
            st.error(f"❌ ERRO ao verificar ingredientes: {e}")
            st.code(traceback.format_exc())
    
    def analyze_csv_file(self, uploaded_file):
        """Analisa arquivo CSV original"""
        try:
            # Ler CSV
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            
            st.subheader("📋 ANÁLISE DO ARQUIVO CSV")
            st.success(f"✅ CSV carregado: {len(df)} linhas")
            
            # Informações básicas
            st.info(f"📊 Colunas: {list(df.columns)}")
            st.info(f"📏 Shape: {df.shape}")
            
            # Verificar dados ausentes
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                st.warning("⚠️ DADOS AUSENTES DETECTADOS:")
                st.dataframe(missing_data[missing_data > 0])
            else:
                st.success("✅ Nenhum dado ausente")
            
            # Verificar duplicatas
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                st.warning(f"⚠️ {duplicates} linhas duplicadas encontradas")
            else:
                st.success("✅ Nenhuma duplicata")
            
            # Amostra dos dados
            st.subheader("📋 AMOSTRA DO CSV (Primeiras 10 linhas)")
            st.dataframe(df.head(10))
            
            # Verificar campos problemáticos
            st.subheader("🔍 ANÁLISE DE CAMPOS CRÍTICOS")
            
            for col in df.columns:
                if df[col].dtype == 'object':  # String fields
                    max_len = df[col].astype(str).str.len().max()
                    if max_len > 100:
                        st.warning(f"⚠️ {col}: Campo muito longo (max {max_len} chars)")
                    
                    # Verificar caracteres especiais
                    special_chars = df[col].astype(str).str.contains('[^\w\s\.\,\-\(\)]', na=False).sum()
                    if special_chars > 0:
                        st.info(f"ℹ️ {col}: {special_chars} registros com caracteres especiais")
            
            return df
            
        except Exception as e:
            st.error(f"❌ ERRO ao analisar CSV: {e}")
            st.code(traceback.format_exc())
            return None
    
    def controlled_upload_test(self, uploaded_file, user_id):
        """Teste de upload controlado com debug detalhado"""
        try:
            # Ler CSV
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            
            st.subheader("🧪 UPLOAD CONTROLADO INICIADO")
            st.info(f"📊 Total de ingredientes: {len(df)}")
            
            # Configurar Firebase client
            from utils.firestore_client import get_firestore_client
            
            client = get_firestore_client()
            if not client:
                st.error("❌ Não foi possível conectar ao Firebase")
                return
            
            collection_path = f"users/{user_id}/ingredients"
            st.info(f"📍 Salvando em: {collection_path}")
            
            # Reset resultados
            self.results = {
                "total_attempted": len(df),
                "successful": 0,
                "failed": 0,
                "errors": [],
                "failed_items": []
            }
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Upload em lotes pequenos (para debug)
            batch_size = 10  # Lotes pequenos para debug detalhado
            batches = [df[i:i+batch_size] for i in range(0, len(df), batch_size)]
            
            st.info(f"🔄 Processando em {len(batches)} lotes de {batch_size} items")
            
            for batch_idx, batch in enumerate(batches):
                status_text.text(f"📦 Processando lote {batch_idx + 1}/{len(batches)}")
                
                for idx, row in batch.iterrows():
                    try:
                        # Converter para dict
                        ingredient_data = {
                            "nome": str(row.get('Nome', '')),
                            "categoria": str(row.get('Categoria', '')),
                            "unid_receita": str(row.get('Unid_Receita', 'g')),
                            "unid_compra": str(row.get('Unid_Compra', 'kg')),
                            "preco": float(row.get('Preco', 0.0)),
                            "kcal_unid": float(row.get('Kcal_Unid', 0.0)),
                            "fator_conv": float(row.get('Fator_Conv', 1.0)),
                            "ativo": bool(row.get('Ativo', True)),
                            "observacoes": str(row.get('Observacoes', '')),
                            "user_id": user_id,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        # Tentar salvar
                        result = client.collection(collection_path).add(ingredient_data)
                        
                        if result:
                            self.results["successful"] += 1
                            st.success(f"✅ Item {idx + 1}: {ingredient_data['nome']}")
                        else:
                            self.results["failed"] += 1
                            error_msg = f"Falha ao salvar item {idx + 1}: {ingredient_data['nome']}"
                            self.results["errors"].append(error_msg)
                            self.results["failed_items"].append(ingredient_data)
                            st.error(f"❌ {error_msg}")
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.1)
                        
                    except Exception as item_error:
                        self.results["failed"] += 1
                        error_msg = f"Exceção item {idx + 1}: {str(item_error)}"
                        self.results["errors"].append(error_msg)
                        self.results["failed_items"].append(row.to_dict())
                        st.error(f"🚨 {error_msg}")
                
                # Update progress
                progress = (batch_idx + 1) / len(batches)
                progress_bar.progress(progress)
                
                # Delay between batches
                time.sleep(0.5)
            
            # Resultados finais
            st.subheader("📊 RESULTADOS DO UPLOAD CONTROLADO")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Tentativas", self.results["total_attempted"])
            
            with col2:
                st.metric("Sucessos", self.results["successful"])
            
            with col3:
                st.metric("Falhas", self.results["failed"])
            
            # Taxa de sucesso
            success_rate = (self.results["successful"] / self.results["total_attempted"]) * 100
            st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
            
            if self.results["errors"]:
                st.subheader("❌ ERROS ENCONTRADOS")
                for error in self.results["errors"][:10]:  # Mostrar primeiros 10
                    st.error(error)
            
            if self.results["failed_items"]:
                st.subheader("📋 ITEMS QUE FALHARAM")
                failed_df = pd.DataFrame(self.results["failed_items"])
                st.dataframe(failed_df)
            
        except Exception as e:
            st.error(f"🚨 ERRO no upload controlado: {e}")
            st.code(traceback.format_exc())
    
    def compare_csv_vs_firebase(self, uploaded_file, user_id):
        """Compara CSV original com o que está no Firebase"""
        try:
            if not uploaded_file:
                st.error("❌ Faça upload do arquivo CSV primeiro")
                return
            
            st.subheader("🔎 COMPARAÇÃO CSV vs FIREBASE")
            
            # Carregar CSV
            csv_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            st.info(f"📋 CSV: {len(csv_df)} ingredientes")
            
            # Carregar Firebase
            from utils.database import get_database_manager
            db_manager = get_database_manager()
            firebase_df = db_manager.get_user_ingredients(user_id)
            st.info(f"🔥 Firebase: {len(firebase_df)} ingredientes")
            
            if firebase_df.empty:
                st.error("❌ Firebase vazio - nenhum ingrediente encontrado")
                return
            
            # Comparar por nome
            csv_names = set(csv_df['Nome'].str.strip().str.lower())
            firebase_names = set(firebase_df['Nome'].str.strip().str.lower())
            
            # Ingredientes faltantes
            missing_in_firebase = csv_names - firebase_names
            extra_in_firebase = firebase_names - csv_names
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Faltando no Firebase", len(missing_in_firebase))
                if missing_in_firebase:
                    st.subheader("📋 INGREDIENTES FALTANDO")
                    missing_list = list(missing_in_firebase)[:20]  # Primeiros 20
                    for item in missing_list:
                        st.error(f"❌ {item}")
                    
                    if len(missing_in_firebase) > 20:
                        st.info(f"... e mais {len(missing_in_firebase) - 20} ingredientes")
            
            with col2:
                st.metric("Extras no Firebase", len(extra_in_firebase))
                if extra_in_firebase:
                    st.subheader("📋 INGREDIENTES EXTRAS")
                    extra_list = list(extra_in_firebase)[:20]  # Primeiros 20
                    for item in extra_list:
                        st.info(f"➕ {item}")
            
            # Análise de padrões
            if missing_in_firebase:
                st.subheader("🔍 ANÁLISE DE PADRÕES DOS FALTANTES")
                
                # Buscar padrões nos nomes faltantes
                missing_df = csv_df[csv_df['Nome'].str.strip().str.lower().isin(missing_in_firebase)]
                
                if not missing_df.empty:
                    # Por categoria
                    if 'Categoria' in missing_df.columns:
                        cat_counts = missing_df['Categoria'].value_counts()
                        st.bar_chart(cat_counts)
                        st.caption("Categorias dos ingredientes faltantes")
                    
                    # Características comuns
                    st.subheader("📊 CARACTERÍSTICAS DOS FALTANTES")
                    st.dataframe(missing_df.head(10))
            
        except Exception as e:
            st.error(f"❌ ERRO na comparação: {e}")
            st.code(traceback.format_exc())

def main():
    debugger = PartialUploadDebugger()
    debugger.main()

if __name__ == "__main__":
    main()