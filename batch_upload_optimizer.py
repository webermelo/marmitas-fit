#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BATCH UPLOAD OPTIMIZER - OPUS 4.0
Sistema otimizado para upload de grandes volumes de dados
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import asyncio
import traceback
from typing import List, Dict, Any

class BatchUploadOptimizer:
    """Sistema otimizado para uploads em lote"""
    
    def __init__(self):
        self.batch_size = 50  # Tamanho otimizado do lote
        self.delay_between_batches = 1.0  # Delay em segundos
        self.delay_between_items = 0.05  # Delay entre items
        self.max_retries = 3  # Número máximo de tentativas
        
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "retried": 0,
            "start_time": None,
            "end_time": None
        }
        
        self.failed_items = []
        self.errors = []
    
    def main(self):
        st.set_page_config(
            page_title="Batch Upload Optimizer - Opus 4.0",
            page_icon="🚀",
            layout="wide"
        )
        
        st.title("🚀 BATCH UPLOAD OPTIMIZER - OPUS 4.0")
        st.markdown("---")
        
        if 'user' not in st.session_state:
            st.error("❌ Usuário não logado")
            return
        
        st.success(f"✅ Usuário: {st.session_state.user['uid']}")
        
        # Configurações
        self.render_config_section()
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "📤 Selecione arquivo CSV com ingredientes",
            type=['csv']
        )
        
        if uploaded_file:
            self.analyze_file(uploaded_file)
            
            if st.button("🚀 INICIAR UPLOAD OTIMIZADO", type="primary"):
                self.optimized_upload(uploaded_file)
    
    def render_config_section(self):
        """Renderiza seção de configurações"""
        st.sidebar.header("⚙️ CONFIGURAÇÕES")
        
        self.batch_size = st.sidebar.slider(
            "Tamanho do Lote",
            min_value=10,
            max_value=100,
            value=50,
            help="Número de items por lote"
        )
        
        self.delay_between_batches = st.sidebar.slider(
            "Delay entre Lotes (segundos)",
            min_value=0.5,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Pausa entre lotes para evitar rate limiting"
        )
        
        self.delay_between_items = st.sidebar.slider(
            "Delay entre Items (segundos)",
            min_value=0.01,
            max_value=0.5,
            value=0.05,
            step=0.01,
            help="Pausa entre items individuais"
        )
        
        self.max_retries = st.sidebar.slider(
            "Tentativas Máximas",
            min_value=1,
            max_value=5,
            value=3,
            help="Número de tentativas para items que falharam"
        )
        
        st.sidebar.info(f"""
        **Configuração Atual:**
        - Lote: {self.batch_size} items
        - Delay lotes: {self.delay_between_batches}s
        - Delay items: {self.delay_between_items}s
        - Max tentativas: {self.max_retries}
        """)
    
    def analyze_file(self, uploaded_file):
        """Analisa arquivo antes do upload"""
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            
            st.subheader("📊 ANÁLISE DO ARQUIVO")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Ingredientes", len(df))
            
            with col2:
                batches_count = (len(df) + self.batch_size - 1) // self.batch_size
                st.metric("Lotes Necessários", batches_count)
            
            with col3:
                estimated_time = (batches_count * self.delay_between_batches) + (len(df) * self.delay_between_items)
                st.metric("Tempo Estimado", f"{estimated_time:.1f}s")
            
            # Verificação de dados
            st.subheader("🔍 VERIFICAÇÃO DE DADOS")
            
            # Campos obrigatórios
            required_fields = ['Nome', 'Categoria', 'Preco', 'Ativo']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                st.error(f"❌ Campos obrigatórios ausentes: {missing_fields}")
                return False
            else:
                st.success("✅ Todos os campos obrigatórios presentes")
            
            # Dados ausentes
            null_counts = df.isnull().sum()
            critical_nulls = null_counts[null_counts > 0]
            
            if len(critical_nulls) > 0:
                st.warning("⚠️ Campos com dados ausentes:")
                st.dataframe(critical_nulls)
            else:
                st.success("✅ Nenhum dado ausente")
            
            # Duplicatas
            duplicates = df.duplicated(subset=['Nome']).sum()
            if duplicates > 0:
                st.warning(f"⚠️ {duplicates} nomes duplicados encontrados")
            else:
                st.success("✅ Nenhum nome duplicado")
            
            # Preview
            st.subheader("👁️ PREVIEW DOS DADOS")
            st.dataframe(df.head(5))
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao analisar arquivo: {e}")
            return False
    
    def optimized_upload(self, uploaded_file):
        """Executa upload otimizado"""
        try:
            # Preparar dados
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            user_id = st.session_state.user['uid']
            
            # Reset stats
            self.stats = {
                "total": len(df),
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "retried": 0,
                "start_time": datetime.now(),
                "end_time": None
            }
            
            self.failed_items = []
            self.errors = []
            
            # Configurar Firebase
            from utils.firestore_client import get_firestore_client
            
            client = get_firestore_client()
            if not client:
                st.error("❌ Erro ao conectar com Firebase")
                return
            
            collection_path = f"users/{user_id}/ingredients"
            
            # Dividir em lotes
            batches = [df[i:i+self.batch_size] for i in range(0, len(df), self.batch_size)]
            
            st.subheader("🚀 UPLOAD EM PROGRESSO")
            
            # Progress indicators
            overall_progress = st.progress(0)
            batch_progress = st.progress(0)
            status_text = st.empty()
            stats_container = st.empty()
            
            # Processar lotes
            for batch_idx, batch in enumerate(batches):
                status_text.text(f"📦 Processando lote {batch_idx + 1}/{len(batches)}")
                
                # Reset batch progress
                batch_progress.progress(0)
                
                # Processar items do lote
                for item_idx, (_, row) in enumerate(batch.iterrows()):
                    success = self.upload_single_item(client, collection_path, row, user_id)
                    
                    if success:
                        self.stats["successful"] += 1
                    else:
                        self.stats["failed"] += 1
                    
                    self.stats["processed"] += 1
                    
                    # Update progress
                    batch_progress.progress((item_idx + 1) / len(batch))
                    overall_progress.progress(self.stats["processed"] / self.stats["total"])
                    
                    # Update stats display
                    self.update_stats_display(stats_container)
                    
                    # Delay between items
                    if self.delay_between_items > 0:
                        time.sleep(self.delay_between_items)
                
                # Delay between batches
                if batch_idx < len(batches) - 1 and self.delay_between_batches > 0:
                    status_text.text(f"⏸️ Pausa entre lotes ({self.delay_between_batches}s)")
                    time.sleep(self.delay_between_batches)
            
            # Processar retry dos items que falharam
            self.retry_failed_items(client, collection_path, user_id, overall_progress, status_text, stats_container)
            
            # Finalizar
            self.stats["end_time"] = datetime.now()
            self.show_final_results()
            
        except Exception as e:
            st.error(f"🚨 Erro no upload otimizado: {e}")
            st.code(traceback.format_exc())
    
    def upload_single_item(self, client, collection_path, row, user_id) -> bool:
        """Upload de um item individual"""
        try:
            # Converter dados
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
                "created_at": datetime.now().isoformat(),
                "batch_upload": True
            }
            
            # Tentar upload
            result = client.collection(collection_path).add(ingredient_data)
            
            if result:
                return True
            else:
                self.failed_items.append({
                    "data": ingredient_data,
                    "error": "No result returned",
                    "attempts": 0
                })
                return False
                
        except Exception as e:
            self.failed_items.append({
                "data": row.to_dict(),
                "error": str(e),
                "attempts": 0
            })
            self.errors.append(f"Erro em '{row.get('Nome', 'Unknown')}': {str(e)}")
            return False
    
    def retry_failed_items(self, client, collection_path, user_id, progress_bar, status_text, stats_container):
        """Tenta novamente os items que falharam"""
        if not self.failed_items:
            return
        
        status_text.text("🔄 Tentando novamente items que falharam...")
        
        items_to_retry = [item for item in self.failed_items if item["attempts"] < self.max_retries]
        
        for item in items_to_retry:
            try:
                item["attempts"] += 1
                self.stats["retried"] += 1
                
                # Reconverter dados se necessário
                if "data" in item and isinstance(item["data"], dict):
                    if "nome" not in item["data"]:  # Precisa reconverter
                        row_data = item["data"]
                        ingredient_data = {
                            "nome": str(row_data.get('Nome', '')),
                            "categoria": str(row_data.get('Categoria', '')),
                            "unid_receita": str(row_data.get('Unid_Receita', 'g')),
                            "unid_compra": str(row_data.get('Unid_Compra', 'kg')),
                            "preco": float(row_data.get('Preco', 0.0)),
                            "kcal_unid": float(row_data.get('Kcal_Unid', 0.0)),
                            "fator_conv": float(row_data.get('Fator_Conv', 1.0)),
                            "ativo": bool(row_data.get('Ativo', True)),
                            "observacoes": str(row_data.get('Observacoes', '')),
                            "user_id": user_id,
                            "created_at": datetime.now().isoformat(),
                            "retry_attempt": item["attempts"]
                        }
                    else:
                        ingredient_data = item["data"]
                        ingredient_data["retry_attempt"] = item["attempts"]
                
                result = client.collection(collection_path).add(ingredient_data)
                
                if result:
                    self.stats["successful"] += 1
                    self.stats["failed"] -= 1
                
                # Update display
                self.update_stats_display(stats_container)
                
                time.sleep(self.delay_between_items * 2)  # Delay maior para retry
                
            except Exception as e:
                item["error"] = f"Retry {item['attempts']}: {str(e)}"
    
    def update_stats_display(self, container):
        """Atualiza display de estatísticas"""
        with container.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Processados", f"{self.stats['processed']}/{self.stats['total']}")
            
            with col2:
                st.metric("Sucessos", self.stats['successful'])
            
            with col3:
                st.metric("Falhas", self.stats['failed'])
            
            with col4:
                if self.stats['processed'] > 0:
                    success_rate = (self.stats['successful'] / self.stats['processed']) * 100
                    st.metric("Taxa Sucesso", f"{success_rate:.1f}%")
                else:
                    st.metric("Taxa Sucesso", "0%")
    
    def show_final_results(self):
        """Mostra resultados finais"""
        st.subheader("🎯 RESULTADOS FINAIS")
        
        duration = self.stats['end_time'] - self.stats['start_time']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Processados", self.stats['total'])
            st.metric("Sucessos", self.stats['successful'])
        
        with col2:
            st.metric("Falhas", self.stats['failed'])
            st.metric("Tentativas", self.stats['retried'])
        
        with col3:
            success_rate = (self.stats['successful'] / self.stats['total']) * 100
            st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
            st.metric("Duração", f"{duration.total_seconds():.1f}s")
        
        if success_rate >= 95:
            st.success("🎉 UPLOAD CONCLUÍDO COM SUCESSO!")
        elif success_rate >= 80:
            st.warning("⚠️ Upload parcialmente bem-sucedido")
        else:
            st.error("❌ Upload falhou - muitos erros")
        
        # Mostrar erros se houver
        if self.errors:
            with st.expander(f"❌ Erros ({len(self.errors)})", expanded=False):
                for error in self.errors[:50]:  # Primeiros 50
                    st.error(error)
        
        # Items que falharam permanentemente
        permanent_failures = [item for item in self.failed_items if item["attempts"] >= self.max_retries]
        if permanent_failures:
            with st.expander(f"🚨 Falhas Permanentes ({len(permanent_failures)})", expanded=False):
                for item in permanent_failures[:20]:  # Primeiros 20
                    st.error(f"Item: {item['data'].get('nome', 'Unknown')} - Erro: {item['error']}")

def main():
    optimizer = BatchUploadOptimizer()
    optimizer.main()

if __name__ == "__main__":
    main()