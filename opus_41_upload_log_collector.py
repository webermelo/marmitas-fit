#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPUS 4.1 UPLOAD LOG COLLECTOR
Sistema especializado para coletar logs detalhados do upload parcial
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import traceback
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

class Opus41UploadLogCollector:
    """Coletor especializado de logs para análise de upload parcial"""
    
    def __init__(self):
        self.logs = {
            "upload_attempts": [],
            "success_items": [],
            "failed_items": [],
            "network_events": [],
            "firebase_responses": [],
            "timing_data": [],
            "memory_usage": [],
            "error_patterns": {},
            "csv_analysis": {},
            "batch_performance": []
        }
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def main(self):
        st.set_page_config(
            page_title="OPUS 4.1 Upload Log Collector",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 OPUS 4.1 UPLOAD LOG COLLECTOR")
        st.markdown("---")
        
        st.error("🔬 ANÁLISE PROFUNDA: Por que 198 ingredientes → apenas parte salva?")
        
        if 'user' not in st.session_state:
            st.error("❌ Faça login primeiro")
            return
            
        st.success(f"✅ Firebase conectado - Sessão: {self.session_id}")
        
        # Coleta de logs em múltiplos níveis
        self.collect_environment_info()
        self.collect_csv_analysis()
        self.collect_firebase_state()
        self.perform_controlled_upload_test()
        self.analyze_failure_patterns()
        self.generate_comprehensive_report()
    
    def collect_environment_info(self):
        """Coleta informações do ambiente"""
        st.header("🔍 1. ANÁLISE DO AMBIENTE")
        
        env_info = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "user_id": st.session_state.user.get('uid', 'Unknown'),
            "streamlit_version": st.__version__,
            "python_version": sys.version,
            "session_state_keys": list(st.session_state.keys()),
            "memory_info": self._get_memory_info()
        }
        
        # Token status
        token_info = self._analyze_token_status()
        env_info.update(token_info)
        
        self.logs["environment"] = env_info
        
        with st.expander("🔍 Environment Info", expanded=False):
            st.json(env_info)
        
        st.success(f"✅ Ambiente analisado - User: {env_info['user_id'][:10]}...")
    
    def _get_memory_info(self):
        """Coleta informações de memória"""
        try:
            import psutil
            process = psutil.Process()
            return {
                "memory_percent": process.memory_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent()
            }
        except:
            return {"error": "psutil not available"}
    
    def _analyze_token_status(self):
        """Analisa status do token atual"""
        if 'user' not in st.session_state:
            return {"token_status": "NO_USER"}
        
        user = st.session_state.user
        
        token_info = {
            "has_token": 'token' in user and bool(user.get('token')),
            "has_refresh_token": 'refresh_token' in user and bool(user.get('refresh_token')),
            "has_timestamp": 'token_timestamp' in user,
            "token_length": len(user.get('token', ''))
        }
        
        # Verificar idade do token
        if token_info["has_timestamp"]:
            try:
                token_time = datetime.fromisoformat(user['token_timestamp'])
                age_minutes = (datetime.now() - token_time).total_seconds() / 60
                token_info["token_age_minutes"] = age_minutes
                token_info["token_fresh"] = age_minutes < 50  # Fresh se < 50 min
            except:
                token_info["timestamp_error"] = True
        
        return {"token_analysis": token_info}
    
    def collect_csv_analysis(self):
        """Análise detalhada do arquivo CSV"""
        st.header("📋 2. ANÁLISE DO ARQUIVO CSV")
        
        uploaded_file = st.file_uploader(
            "📤 Upload o MESMO arquivo que causou o problema parcial",
            type=['csv'],
            key="csv_analysis"
        )
        
        if not uploaded_file:
            st.warning("⚠️ Faça upload do CSV para análise completa")
            return
        
        try:
            # Análise detalhada do CSV
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            
            csv_analysis = {
                "total_rows": len(df),
                "columns": list(df.columns),
                "file_size_bytes": uploaded_file.size,
                "encoding": "utf-8-sig",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Análise de dados
            csv_analysis["data_quality"] = {
                "null_counts": df.isnull().sum().to_dict(),
                "duplicate_names": df.duplicated(subset=['Nome']).sum() if 'Nome' in df.columns else 0,
                "data_types": df.dtypes.astype(str).to_dict(),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
            # Análise de conteúdo crítico
            if 'Ativo' in df.columns:
                csv_analysis["boolean_analysis"] = {
                    "ativo_values": df['Ativo'].value_counts().to_dict(),
                    "ativo_types": df['Ativo'].apply(type).value_counts().to_dict(),
                    "problematic_booleans": (df['Ativo'].astype(str).isin(['True', 'False', '1', '0'])).sum()
                }
            
            # Análise de caracteres especiais
            problematic_chars = 0
            long_fields = 0
            
            for col in df.select_dtypes(include=['object']).columns:
                # Caracteres especiais
                has_special = df[col].astype(str).str.contains('[^\w\s\.\,\-\(\)]', na=False)
                problematic_chars += has_special.sum()
                
                # Campos muito longos
                long_fields += (df[col].astype(str).str.len() > 200).sum()
            
            csv_analysis["content_issues"] = {
                "special_characters": problematic_chars,
                "long_fields": long_fields,
                "total_string_fields": len(df.select_dtypes(include=['object']).columns)
            }
            
            # Amostra dos dados
            csv_analysis["sample_data"] = {
                "first_5_rows": df.head(5).to_dict('records'),
                "last_5_rows": df.tail(5).to_dict('records'),
                "random_5_rows": df.sample(min(5, len(df))).to_dict('records')
            }
            
            self.logs["csv_analysis"] = csv_analysis
            
            # Display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Ingredientes", csv_analysis["total_rows"])
                st.metric("Tamanho Arquivo", f"{csv_analysis['file_size_bytes']/1024:.1f} KB")
            
            with col2:
                st.metric("Colunas", len(csv_analysis["columns"]))
                st.metric("Duplicatas", csv_analysis["data_quality"]["duplicate_names"])
            
            with col3:
                st.metric("Chars Especiais", csv_analysis["content_issues"]["special_characters"])
                st.metric("Campos Longos", csv_analysis["content_issues"]["long_fields"])
            
            # Issues encontrados
            issues = []
            if csv_analysis["data_quality"]["duplicate_names"] > 0:
                issues.append(f"📋 {csv_analysis['data_quality']['duplicate_names']} nomes duplicados")
            
            if csv_analysis["content_issues"]["special_characters"] > 10:
                issues.append(f"⚠️ {csv_analysis['content_issues']['special_characters']} campos com caracteres especiais")
            
            if csv_analysis["data_quality"]["memory_usage_mb"] > 5:
                issues.append(f"💾 Arquivo grande: {csv_analysis['data_quality']['memory_usage_mb']:.1f} MB em memória")
            
            if issues:
                st.subheader("⚠️ POSSÍVEIS PROBLEMAS IDENTIFICADOS")
                for issue in issues:
                    st.warning(issue)
            else:
                st.success("✅ CSV parece estar bem formatado")
            
            with st.expander("📋 Análise Completa CSV", expanded=False):
                st.json(csv_analysis)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro na análise CSV: {e}")
            st.code(traceback.format_exc())
            return None
    
    def collect_firebase_state(self):
        """Coleta estado atual do Firebase"""
        st.header("🔥 3. ESTADO ATUAL DO FIREBASE")
        
        try:
            from utils.database import get_database_manager
            
            db_manager = get_database_manager()
            user_id = st.session_state.user['uid']
            
            # Verificar ingredientes atuais
            current_df = db_manager.get_user_ingredients(user_id)
            
            firebase_state = {
                "current_ingredient_count": len(current_df),
                "firebase_connected": True,
                "collection_path": f"users/{user_id}/ingredients",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            if not current_df.empty:
                firebase_state["current_ingredients"] = {
                    "by_category": current_df.groupby('Categoria').size().to_dict() if 'Categoria' in current_df.columns else {},
                    "sample_names": current_df['Nome'].head(10).tolist() if 'Nome' in current_df.columns else [],
                    "data_types": current_df.dtypes.astype(str).to_dict(),
                    "has_test_data": current_df['Nome'].str.contains('TESTE', case=False, na=False).any() if 'Nome' in current_df.columns else False
                }
            
            self.logs["firebase_state"] = firebase_state
            
            # Display
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Ingredientes Atuais", firebase_state["current_ingredient_count"])
                if firebase_state["current_ingredient_count"] > 0:
                    st.success("✅ Firebase tem dados")
                else:
                    st.warning("⚠️ Firebase vazio")
            
            with col2:
                st.metric("Gap Esperado", max(0, 198 - firebase_state["current_ingredient_count"]))
                if firebase_state["current_ingredient_count"] < 198:
                    missing = 198 - firebase_state["current_ingredient_count"]
                    st.error(f"❌ Faltam {missing} ingredientes")
            
            # Se houver dados parciais, mostrar categorias
            if firebase_state["current_ingredient_count"] > 0 and "current_ingredients" in firebase_state:
                st.subheader("📊 INGREDIENTES POR CATEGORIA (atual)")
                categories = firebase_state["current_ingredients"]["by_category"]
                if categories:
                    st.bar_chart(categories)
            
            with st.expander("🔥 Estado Firebase Completo", expanded=False):
                st.json(firebase_state)
        
        except Exception as e:
            st.error(f"❌ Erro ao analisar Firebase: {e}")
            firebase_state = {
                "error": str(e),
                "firebase_connected": False,
                "analysis_timestamp": datetime.now().isoformat()
            }
            self.logs["firebase_state"] = firebase_state
    
    def perform_controlled_upload_test(self):
        """Teste controlado com logs detalhados"""
        st.header("🧪 4. TESTE CONTROLADO COM LOGS INTENSIVOS")
        
        if 'csv_analysis' not in self.logs or not hasattr(st.session_state, 'test_df'):
            st.warning("⚠️ Faça upload do CSV primeiro para executar teste")
            return
        
        if st.button("🚀 EXECUTAR TESTE CONTROLADO (10 INGREDIENTES)", type="primary"):
            self._run_controlled_test()
    
    def _run_controlled_test(self):
        """Executa teste controlado com 10 ingredientes"""
        try:
            # Usar DataFrame do CSV analysis
            if 'csv_analysis' not in self.logs:
                st.error("❌ CSV não analisado")
                return
            
            # Simular dados de teste baseados na análise
            test_data = self.logs["csv_analysis"]["sample_data"]["first_5_rows"][:3]  # Usar 3 primeiros
            
            if not test_data:
                st.error("❌ Sem dados para teste")
                return
            
            from utils.firestore_client import get_firestore_client
            
            client = get_firestore_client()
            if not client:
                st.error("❌ Firebase client não disponível")
                return
            
            user_id = st.session_state.user['uid']
            collection_path = f"users/{user_id}/ingredients"
            
            st.info(f"🧪 Testando {len(test_data)} ingredientes com logs detalhados...")
            
            test_results = {
                "start_time": time.time(),
                "attempts": [],
                "success_count": 0,
                "failure_count": 0,
                "total_items": len(test_data)
            }
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            for i, item in enumerate(test_data):
                attempt_start = time.time()
                
                try:
                    # Converter item para formato Firebase
                    ingredient_data = {
                        "nome": str(item.get('Nome', f'TestItem_{i}')),
                        "categoria": str(item.get('Categoria', 'Teste')),
                        "unid_receita": str(item.get('Unid_Receita', 'g')),
                        "unid_compra": str(item.get('Unid_Compra', 'kg')),
                        "preco": float(item.get('Preco', 0.0)),
                        "kcal_unid": float(item.get('Kcal_Unid', 0.0)),
                        "fator_conv": float(item.get('Fator_Conv', 1.0)),
                        "ativo": bool(item.get('Ativo', True)),
                        "observacoes": str(item.get('Observacoes', '')),
                        "user_id": user_id,
                        "created_at": datetime.now().isoformat(),
                        "test_session": self.session_id,
                        "test_item": True
                    }
                    
                    status_container.info(f"🔄 Salvando: {ingredient_data['nome']}")
                    
                    # Tentar salvar
                    result = client.collection(collection_path).add(ingredient_data)
                    
                    attempt_end = time.time()
                    duration = attempt_end - attempt_start
                    
                    if result:
                        # Sucesso
                        attempt_log = {
                            "item_index": i,
                            "item_name": ingredient_data['nome'],
                            "status": "SUCCESS",
                            "duration_seconds": duration,
                            "timestamp": datetime.now().isoformat(),
                            "firebase_response": str(result)[:200]  # Limitar tamanho
                        }
                        
                        test_results["success_count"] += 1
                        st.success(f"✅ {i+1}: {ingredient_data['nome']} - {duration:.2f}s")
                    else:
                        # Falha sem exceção
                        attempt_log = {
                            "item_index": i,
                            "item_name": ingredient_data['nome'],
                            "status": "FAILED_NO_RESULT",
                            "duration_seconds": duration,
                            "timestamp": datetime.now().isoformat(),
                            "error": "Firebase retornou None"
                        }
                        
                        test_results["failure_count"] += 1
                        st.error(f"❌ {i+1}: {ingredient_data['nome']} - Sem resultado")
                    
                    test_results["attempts"].append(attempt_log)
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(test_data))
                    
                    # Delay pequeno para observar padrões
                    time.sleep(0.5)
                
                except Exception as item_error:
                    attempt_end = time.time()
                    duration = attempt_end - attempt_start
                    
                    attempt_log = {
                        "item_index": i,
                        "item_name": item.get('Nome', f'Item_{i}'),
                        "status": "EXCEPTION",
                        "duration_seconds": duration,
                        "timestamp": datetime.now().isoformat(),
                        "error": str(item_error),
                        "traceback": traceback.format_exc()
                    }
                    
                    test_results["attempts"].append(attempt_log)
                    test_results["failure_count"] += 1
                    
                    st.error(f"🚨 {i+1}: EXCEÇÃO - {str(item_error)}")
            
            test_results["end_time"] = time.time()
            test_results["total_duration"] = test_results["end_time"] - test_results["start_time"]
            
            self.logs["controlled_test"] = test_results
            
            # Exibir resultados
            st.subheader("📊 RESULTADOS DO TESTE CONTROLADO")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Sucessos", test_results["success_count"])
            
            with col2:
                st.metric("Falhas", test_results["failure_count"])
            
            with col3:
                success_rate = (test_results["success_count"] / test_results["total_items"]) * 100
                st.metric("Taxa Sucesso", f"{success_rate:.1f}%")
            
            # Análise de padrões
            if test_results["failure_count"] > 0:
                st.subheader("❌ PADRÕES DE FALHA")
                
                failures = [a for a in test_results["attempts"] if a["status"] != "SUCCESS"]
                
                for failure in failures:
                    with st.expander(f"❌ Falha: {failure['item_name']}", expanded=False):
                        st.json(failure)
            
            with st.expander("📋 Log Completo do Teste", expanded=False):
                st.json(test_results)
        
        except Exception as e:
            st.error(f"🚨 Erro no teste controlado: {e}")
            st.code(traceback.format_exc())
    
    def analyze_failure_patterns(self):
        """Análise de padrões de falha"""
        st.header("🔍 5. ANÁLISE DE PADRÕES DE FALHA")
        
        if "controlled_test" not in self.logs:
            st.warning("⚠️ Execute teste controlado primeiro")
            return
        
        test_data = self.logs["controlled_test"]
        
        # Análise temporal
        attempts = test_data["attempts"]
        if attempts:
            durations = [a["duration_seconds"] for a in attempts]
            avg_duration = sum(durations) / len(durations)
            
            pattern_analysis = {
                "average_duration": avg_duration,
                "min_duration": min(durations),
                "max_duration": max(durations),
                "duration_variance": max(durations) - min(durations),
                "success_vs_failure_timing": {},
                "error_types": {},
                "temporal_patterns": []
            }
            
            # Sucesso vs falha timing
            success_durations = [a["duration_seconds"] for a in attempts if a["status"] == "SUCCESS"]
            failure_durations = [a["duration_seconds"] for a in attempts if a["status"] != "SUCCESS"]
            
            if success_durations:
                pattern_analysis["success_vs_failure_timing"]["success_avg"] = sum(success_durations) / len(success_durations)
            
            if failure_durations:
                pattern_analysis["success_vs_failure_timing"]["failure_avg"] = sum(failure_durations) / len(failure_durations)
            
            # Tipos de erro
            for attempt in attempts:
                if attempt["status"] != "SUCCESS":
                    error_type = attempt["status"]
                    if error_type not in pattern_analysis["error_types"]:
                        pattern_analysis["error_types"][error_type] = 0
                    pattern_analysis["error_types"][error_type] += 1
            
            self.logs["pattern_analysis"] = pattern_analysis
            
            # Display análise
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("⏱️ ANÁLISE TEMPORAL")
                st.metric("Duração Média", f"{avg_duration:.2f}s")
                st.metric("Duração Min/Max", f"{min(durations):.2f}s / {max(durations):.2f}s")
                
                if success_durations and failure_durations:
                    if pattern_analysis["success_vs_failure_timing"]["success_avg"] < pattern_analysis["success_vs_failure_timing"]["failure_avg"]:
                        st.info("✅ Sucessos são mais rápidos")
                    else:
                        st.warning("⚠️ Falhas são mais rápidas (suspeito)")
            
            with col2:
                st.subheader("🚨 TIPOS DE ERRO")
                error_types = pattern_analysis["error_types"]
                
                if error_types:
                    for error_type, count in error_types.items():
                        st.error(f"{error_type}: {count} ocorrências")
                else:
                    st.success("✅ Nenhum erro específico identificado")
            
            with st.expander("📊 Análise Completa de Padrões", expanded=False):
                st.json(pattern_analysis)
    
    def generate_comprehensive_report(self):
        """Gera relatório completo para análise"""
        st.header("📋 6. RELATÓRIO PARA ANÁLISE OPUS 4.1")
        
        # Compilar todos os logs
        comprehensive_report = {
            "report_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "analysis_version": "OPUS_4.1_UPLOAD_DIAGNOSTIC",
            "collected_data": self.logs
        }
        
        # Resumo executivo
        executive_summary = {
            "total_expected": 198,
            "currently_in_firebase": self.logs.get("firebase_state", {}).get("current_ingredient_count", 0),
            "missing_count": 198 - self.logs.get("firebase_state", {}).get("current_ingredient_count", 0),
            "firebase_connected": self.logs.get("firebase_state", {}).get("firebase_connected", False),
            "csv_analyzed": "csv_analysis" in self.logs,
            "controlled_test_executed": "controlled_test" in self.logs
        }
        
        if "controlled_test" in self.logs:
            test_data = self.logs["controlled_test"]
            executive_summary["test_success_rate"] = (test_data["success_count"] / test_data["total_items"]) * 100
            executive_summary["test_avg_duration"] = sum([a["duration_seconds"] for a in test_data["attempts"]]) / len(test_data["attempts"]) if test_data["attempts"] else 0
        
        comprehensive_report["executive_summary"] = executive_summary
        
        # Display resumo
        st.subheader("📊 RESUMO EXECUTIVO")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Esperado", executive_summary["total_expected"])
            st.metric("Atual Firebase", executive_summary["currently_in_firebase"])
        
        with col2:
            st.metric("Faltando", executive_summary["missing_count"])
            if executive_summary["missing_count"] > 0:
                st.error(f"❌ {executive_summary['missing_count']} ingredientes não salvos")
            else:
                st.success("✅ Todos os ingredientes presentes")
        
        with col3:
            if "test_success_rate" in executive_summary:
                st.metric("Taxa Teste", f"{executive_summary['test_success_rate']:.1f}%")
                if executive_summary["test_success_rate"] < 100:
                    st.warning("⚠️ Falhas detectadas no teste")
                else:
                    st.success("✅ Teste 100% sucesso")
        
        # Hipóteses baseadas nos dados coletados
        st.subheader("🎯 HIPÓTESES BASEADAS NOS DADOS")
        
        hypotheses = []
        
        # Análise das hipóteses
        if executive_summary["missing_count"] > 100:
            hypotheses.append({
                "hypothesis": "FALHA MASSIVA EARLY",
                "probability": "ALTA",
                "evidence": f"Mais de {executive_summary['missing_count']} faltando sugere falha cedo no processo",
                "investigation": "Verificar logs de erro nos primeiros uploads"
            })
        elif executive_summary["missing_count"] > 50:
            hypotheses.append({
                "hypothesis": "RATE LIMITING FIREBASE", 
                "probability": "ALTA",
                "evidence": "Upload parcial consistente com rate limiting",
                "investigation": "Analisar timing entre uploads"
            })
        elif executive_summary["missing_count"] > 0:
            hypotheses.append({
                "hypothesis": "FALHAS ESPECÍFICAS",
                "probability": "MÉDIA", 
                "evidence": "Alguns ingredientes específicos causando problemas",
                "investigation": "Comparar ingredientes salvos vs não salvos"
            })
        
        # Hipóteses baseadas no teste
        if "test_success_rate" in executive_summary and executive_summary["test_success_rate"] < 100:
            hypotheses.append({
                "hypothesis": "PROBLEMA SISTÊMICO",
                "probability": "ALTA",
                "evidence": f"Teste controlado falhou {100-executive_summary['test_success_rate']:.1f}% das vezes",
                "investigation": "Analisar logs específicos das falhas"
            })
        
        for i, hypothesis in enumerate(hypotheses):
            with st.expander(f"💡 Hipótese {i+1}: {hypothesis['hypothesis']} ({hypothesis['probability']} prob.)", expanded=True):
                st.info(f"**Evidência**: {hypothesis['evidence']}")
                st.info(f"**Investigação**: {hypothesis['investigation']}")
        
        # Download do relatório completo
        st.subheader("📥 DOWNLOAD RELATÓRIO COMPLETO")
        
        json_report = json.dumps(comprehensive_report, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 BAIXAR RELATÓRIO JSON",
            data=json_report,
            file_name=f"opus_41_upload_analysis_{self.session_id}.json",
            mime="application/json"
        )
        
        # Próximos passos recomendados
        st.subheader("🚀 PRÓXIMOS PASSOS RECOMENDADOS")
        
        recommendations = [
            "🔍 **Analisar relatório JSON** para padrões específicos",
            "🧪 **Executar batch_upload_optimizer.py** com lotes pequenos (10-20 items)",
            "📊 **Comparar ingredientes faltantes** com os que foram salvos", 
            "⏱️ **Implementar delays maiores** entre uploads (1-2 segundos)",
            "🔄 **Testar upload incremental** apenas dos ingredientes faltantes"
        ]
        
        for rec in recommendations:
            st.markdown(rec)
        
        # Log final
        self.logs["comprehensive_report"] = comprehensive_report
        
        st.success("✅ Coleta de logs completa! Use o relatório JSON para análise detalhada.")

def main():
    collector = Opus41UploadLogCollector()
    collector.main()

if __name__ == "__main__":
    main()