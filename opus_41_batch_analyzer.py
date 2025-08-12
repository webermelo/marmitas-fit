#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPUS 4.1 BATCH ANALYZER
Análise específica de por que uploads em batch falham parcialmente
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import requests
import traceback

class Opus41BatchAnalyzer:
    """Análise especializada para uploads em batch que falham parcialmente"""
    
    def __init__(self):
        self.analysis_results = {
            "batch_scenarios": [],
            "rate_limit_tests": [],
            "memory_snapshots": [],
            "network_patterns": [],
            "firebase_responses": [],
            "failure_distribution": {}
        }
    
    def main(self):
        st.set_page_config(
            page_title="OPUS 4.1 Batch Analyzer",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 OPUS 4.1 BATCH ANALYZER")
        st.markdown("---")
        
        st.error("🔬 FOCO: Por que 198 ingredientes → apenas parcialmente salvos?")
        
        if 'user' not in st.session_state:
            st.error("❌ Login necessário")
            return
        
        # Análises específicas para batch
        self.analyze_current_state()
        self.test_batch_scenarios() 
        self.analyze_rate_limiting()
        self.test_memory_constraints()
        self.analyze_network_patterns()
        self.generate_batch_strategy()
    
    def analyze_current_state(self):
        """Análise do estado atual para entender o que foi salvo vs não salvo"""
        st.header("📊 1. ANÁLISE DO ESTADO ATUAL")
        
        try:
            from utils.database import get_database_manager
            
            db_manager = get_database_manager()
            user_id = st.session_state.user['uid']
            
            current_df = db_manager.get_user_ingredients(user_id)
            
            state_analysis = {
                "current_count": len(current_df),
                "expected_count": 198,
                "missing_count": 198 - len(current_df),
                "success_rate": (len(current_df) / 198) * 100 if len(current_df) > 0 else 0,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Salvos Atualmente", state_analysis["current_count"])
                
            with col2:
                st.metric("Faltando", state_analysis["missing_count"])
                
            with col3:
                st.metric("Taxa de Sucesso", f"{state_analysis['success_rate']:.1f}%")
            
            # Análise de distribuição se há dados
            if not current_df.empty:
                st.subheader("📈 DISTRIBUIÇÃO DOS DADOS SALVOS")
                
                # Por categoria se disponível
                if 'Categoria' in current_df.columns:
                    category_dist = current_df['Categoria'].value_counts()
                    st.bar_chart(category_dist)
                    
                    # Identificar categorias que podem ter sido mais afetadas
                    st.subheader("🎯 PADRÕES IDENTIFICADOS")
                    
                    total_categories = len(category_dist)
                    avg_per_category = len(current_df) / total_categories if total_categories > 0 else 0
                    
                    underrepresented = category_dist[category_dist < avg_per_category * 0.5]
                    
                    if not underrepresented.empty:
                        st.warning("⚠️ CATEGORIAS SUB-REPRESENTADAS (possível padrão de falha):")
                        for cat, count in underrepresented.items():
                            st.error(f"❌ {cat}: apenas {count} ingredientes")
                    
                # Análise temporal se há timestamps
                if 'created_at' in current_df.columns:
                    st.subheader("⏰ ANÁLISE TEMPORAL")
                    
                    try:
                        current_df['created_at_parsed'] = pd.to_datetime(current_df['created_at'])
                        
                        # Agrupar por minuto para ver quando parou
                        by_minute = current_df.groupby(current_df['created_at_parsed'].dt.floor('T')).size()
                        
                        st.line_chart(by_minute)
                        st.caption("Uploads por minuto - queda indica onde o upload parou")
                        
                    except Exception as e:
                        st.warning(f"⚠️ Erro na análise temporal: {e}")
                
                # Amostra dos dados salvos
                with st.expander("📋 Amostra dos Ingredientes Salvos", expanded=False):
                    st.dataframe(current_df.head(10))
            
            else:
                st.error("❌ NENHUM ingrediente encontrado no Firebase!")
                st.error("🚨 FALHA TOTAL do upload - problema mais grave")
            
            self.analysis_results["current_state"] = state_analysis
            
        except Exception as e:
            st.error(f"❌ Erro na análise de estado: {e}")
            st.code(traceback.format_exc())
    
    def test_batch_scenarios(self):
        """Testa diferentes cenários de batch para identificar falhas"""
        st.header("🧪 2. TESTE DE CENÁRIOS DE BATCH")
        
        scenarios = [
            {"name": "Micro Batch", "size": 5, "delay": 0.1},
            {"name": "Small Batch", "size": 10, "delay": 0.5}, 
            {"name": "Medium Batch", "size": 25, "delay": 1.0},
            {"name": "Large Batch", "size": 50, "delay": 2.0}
        ]
        
        st.info("🎯 Objetivo: Encontrar tamanho de batch que não falha")
        
        if st.button("🚀 EXECUTAR TESTES DE BATCH", type="primary"):
            self._run_batch_scenarios(scenarios)
    
    def _run_batch_scenarios(self, scenarios):
        """Executa testes de diferentes tamanhos de batch"""
        try:
            from utils.firestore_client import get_firestore_client
            
            client = get_firestore_client()
            if not client:
                st.error("❌ Cliente Firebase não disponível")
                return
            
            user_id = st.session_state.user['uid']
            collection_path = f"users/{user_id}/test_batches"
            
            st.subheader("📊 RESULTADOS DOS TESTES")
            
            for scenario in scenarios:
                st.write(f"🧪 **Testando: {scenario['name']}** ({scenario['size']} items, {scenario['delay']}s delay)")
                
                batch_result = {
                    "scenario": scenario,
                    "start_time": time.time(),
                    "attempts": [],
                    "success_count": 0,
                    "failure_count": 0
                }
                
                # Criar dados de teste para este batch
                test_items = []
                for i in range(scenario['size']):
                    test_item = {
                        "nome": f"BatchTest_{scenario['name']}_{i}",
                        "categoria": f"TestCat_{i % 3}",  # 3 categorias diferentes
                        "preco": 10.0 + (i * 0.5),
                        "ativo": True,
                        "test_batch": scenario['name'],
                        "test_timestamp": datetime.now().isoformat(),
                        "user_id": user_id
                    }
                    test_items.append(test_item)
                
                # Progress para este cenário
                progress = st.progress(0)
                status = st.empty()
                
                # Executar batch
                for i, item in enumerate(test_items):
                    try:
                        status.info(f"📦 {scenario['name']}: {i+1}/{scenario['size']} - {item['nome']}")
                        
                        item_start = time.time()
                        result = client.collection(collection_path).add(item)
                        item_duration = time.time() - item_start
                        
                        if result:
                            batch_result["success_count"] += 1
                            attempt_log = {
                                "item_index": i,
                                "status": "SUCCESS",
                                "duration": item_duration,
                                "timestamp": datetime.now().isoformat()
                            }
                        else:
                            batch_result["failure_count"] += 1
                            attempt_log = {
                                "item_index": i,
                                "status": "NO_RESULT",
                                "duration": item_duration,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        batch_result["attempts"].append(attempt_log)
                        
                        # Update progress
                        progress.progress((i + 1) / scenario['size'])
                        
                        # Delay entre items
                        time.sleep(scenario['delay'])
                    
                    except Exception as item_error:
                        batch_result["failure_count"] += 1
                        attempt_log = {
                            "item_index": i,
                            "status": "EXCEPTION",
                            "error": str(item_error),
                            "timestamp": datetime.now().isoformat()
                        }
                        batch_result["attempts"].append(attempt_log)
                
                batch_result["end_time"] = time.time()
                batch_result["total_duration"] = batch_result["end_time"] - batch_result["start_time"]
                batch_result["success_rate"] = (batch_result["success_count"] / scenario['size']) * 100
                
                self.analysis_results["batch_scenarios"].append(batch_result)
                
                # Mostrar resultado deste cenário
                if batch_result["success_rate"] == 100:
                    st.success(f"✅ {scenario['name']}: {batch_result['success_rate']:.1f}% sucesso em {batch_result['total_duration']:.1f}s")
                elif batch_result["success_rate"] > 80:
                    st.warning(f"⚠️ {scenario['name']}: {batch_result['success_rate']:.1f}% sucesso em {batch_result['total_duration']:.1f}s")
                else:
                    st.error(f"❌ {scenario['name']}: {batch_result['success_rate']:.1f}% sucesso em {batch_result['total_duration']:.1f}s")
                
                # Delay entre cenários
                time.sleep(2)
            
            # Análise comparativa
            st.subheader("📊 ANÁLISE COMPARATIVA")
            
            scenario_comparison = []
            for result in self.analysis_results["batch_scenarios"]:
                scenario_comparison.append({
                    "Cenário": result["scenario"]["name"],
                    "Tamanho": result["scenario"]["size"],
                    "Taxa Sucesso": f"{result['success_rate']:.1f}%",
                    "Duração Total": f"{result['total_duration']:.1f}s",
                    "Tempo/Item": f"{result['total_duration']/result['scenario']['size']:.2f}s"
                })
            
            comparison_df = pd.DataFrame(scenario_comparison)
            st.dataframe(comparison_df)
            
            # Identificar melhor cenário
            best_scenario = max(self.analysis_results["batch_scenarios"], key=lambda x: x["success_rate"])
            
            if best_scenario["success_rate"] == 100:
                st.success(f"🎉 **CENÁRIO IDEAL ENCONTRADO**: {best_scenario['scenario']['name']}")
                st.success(f"✅ Tamanho: {best_scenario['scenario']['size']} items")
                st.success(f"✅ Delay: {best_scenario['scenario']['delay']}s")
                st.success(f"✅ 100% sucesso em {best_scenario['total_duration']:.1f}s")
            else:
                st.warning(f"⚠️ **MELHOR CENÁRIO**: {best_scenario['scenario']['name']} ({best_scenario['success_rate']:.1f}% sucesso)")
                st.warning("🚨 Nenhum cenário atingiu 100% - problema sistêmico mais profundo")
            
        except Exception as e:
            st.error(f"🚨 Erro nos testes de batch: {e}")
            st.code(traceback.format_exc())
    
    def analyze_rate_limiting(self):
        """Análise específica de rate limiting do Firebase"""
        st.header("⏱️ 3. ANÁLISE DE RATE LIMITING")
        
        st.info("🎯 Objetivo: Detectar se Firebase está limitando operações por segundo")
        
        if st.button("🔍 TESTAR RATE LIMITING"):
            self._test_rate_limiting()
    
    def _test_rate_limiting(self):
        """Testa limites de rate do Firebase"""
        try:
            from utils.firestore_client import get_firestore_client
            
            client = get_firestore_client()
            if not client:
                st.error("❌ Cliente não disponível")
                return
            
            user_id = st.session_state.user['uid']
            collection_path = f"users/{user_id}/rate_limit_test"
            
            # Teste de velocidades diferentes
            rate_tests = [
                {"name": "Ultra Rápido", "delay": 0.01, "count": 20},
                {"name": "Muito Rápido", "delay": 0.1, "count": 20},
                {"name": "Rápido", "delay": 0.5, "count": 20},
                {"name": "Normal", "delay": 1.0, "count": 20}
            ]
            
            st.subheader("🔄 TESTANDO DIFERENTES VELOCIDADES")
            
            for test in rate_tests:
                st.write(f"⚡ **{test['name']}**: {test['count']} items com {test['delay']}s delay")
                
                rate_result = {
                    "test_config": test,
                    "start_time": time.time(),
                    "success_count": 0,
                    "failure_count": 0,
                    "response_times": [],
                    "errors": []
                }
                
                progress = st.progress(0)
                
                for i in range(test['count']):
                    try:
                        test_data = {
                            "nome": f"RateTest_{test['name']}_{i}",
                            "test_type": "rate_limit",
                            "delay_used": test['delay'],
                            "sequence": i,
                            "timestamp": datetime.now().isoformat(),
                            "user_id": user_id
                        }
                        
                        item_start = time.time()
                        result = client.collection(collection_path).add(test_data)
                        item_end = time.time()
                        
                        response_time = item_end - item_start
                        rate_result["response_times"].append(response_time)
                        
                        if result:
                            rate_result["success_count"] += 1
                        else:
                            rate_result["failure_count"] += 1
                            rate_result["errors"].append(f"Item {i}: No result")
                        
                        progress.progress((i + 1) / test['count'])
                        
                        # Delay configurado
                        time.sleep(test['delay'])
                    
                    except Exception as e:
                        rate_result["failure_count"] += 1
                        rate_result["errors"].append(f"Item {i}: {str(e)}")
                
                rate_result["end_time"] = time.time()
                rate_result["total_duration"] = rate_result["end_time"] - rate_result["start_time"]
                rate_result["success_rate"] = (rate_result["success_count"] / test['count']) * 100
                rate_result["avg_response_time"] = sum(rate_result["response_times"]) / len(rate_result["response_times"]) if rate_result["response_times"] else 0
                
                self.analysis_results["rate_limit_tests"].append(rate_result)
                
                # Mostrar resultado
                if rate_result["success_rate"] == 100:
                    st.success(f"✅ {test['name']}: 100% sucesso, {rate_result['avg_response_time']:.2f}s resp médio")
                else:
                    st.error(f"❌ {test['name']}: {rate_result['success_rate']:.1f}% sucesso, {len(rate_result['errors'])} erros")
                    
                    if rate_result['errors']:
                        with st.expander(f"❌ Erros {test['name']}", expanded=False):
                            for error in rate_result['errors'][:5]:  # Primeiros 5
                                st.error(error)
            
            # Análise dos resultados de rate limiting
            st.subheader("📊 ANÁLISE DE RATE LIMITING")
            
            rate_comparison = []
            for result in self.analysis_results["rate_limit_tests"]:
                rate_comparison.append({
                    "Velocidade": result["test_config"]["name"],
                    "Delay": f"{result['test_config']['delay']}s",
                    "Taxa Sucesso": f"{result['success_rate']:.1f}%",
                    "Resp Médio": f"{result['avg_response_time']:.3f}s",
                    "Total": f"{result['total_duration']:.1f}s"
                })
            
            rate_df = pd.DataFrame(rate_comparison)
            st.dataframe(rate_df)
            
            # Identificar ponto de quebra
            successful_tests = [r for r in self.analysis_results["rate_limit_tests"] if r["success_rate"] == 100]
            
            if successful_tests:
                fastest_successful = min(successful_tests, key=lambda x: x["test_config"]["delay"])
                st.success(f"🎯 **VELOCIDADE MÁXIMA SEM FALHA**: {fastest_successful['test_config']['name']}")
                st.success(f"✅ Delay seguro: {fastest_successful['test_config']['delay']}s entre uploads")
            else:
                st.error("🚨 **TODOS OS TESTES FALHARAM** - problema não é rate limiting")
                st.error("🚨 Investigar outras causas: rede, autenticação, dados")
        
        except Exception as e:
            st.error(f"🚨 Erro no teste de rate limiting: {e}")
    
    def test_memory_constraints(self):
        """Testa se problema é de memória/recursos"""
        st.header("💾 4. ANÁLISE DE MEMÓRIA E RECURSOS")
        
        try:
            import psutil
            import gc
            
            # Estado inicial da memória
            process = psutil.Process()
            initial_memory = process.memory_info()
            
            memory_analysis = {
                "initial_memory_mb": initial_memory.rss / 1024 / 1024,
                "initial_memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(interval=1)
            }
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Memória Atual", f"{memory_analysis['initial_memory_mb']:.1f} MB")
            
            with col2:
                st.metric("% Memória Sistema", f"{memory_analysis['initial_memory_percent']:.1f}%")
            
            with col3:
                st.metric("CPU %", f"{memory_analysis['cpu_percent']:.1f}%")
            
            # Teste de carga de memória
            if st.button("🧪 TESTAR IMPACTO MEMÓRIA"):
                
                st.info("🔄 Simulando carga de 198 ingredientes...")
                
                # Simular carregamento de 198 ingredientes
                large_dataset = []
                for i in range(198):
                    ingredient = {
                        "nome": f"Ingrediente_{i:03d}",
                        "categoria": f"Categoria_{i % 10}",
                        "preco": 10.0 + (i * 0.1),
                        "ativo": True,
                        "observacoes": "Teste de memória " * 20,  # String longa
                        "dados_extras": list(range(100))  # Lista para ocupar memória
                    }
                    large_dataset.append(ingredient)
                
                # Medir memória após carregamento
                after_load_memory = process.memory_info()
                memory_increase = (after_load_memory.rss - initial_memory.rss) / 1024 / 1024
                
                st.info(f"📊 Aumento de memória: {memory_increase:.1f} MB para 198 ingredientes")
                
                if memory_increase > 100:  # Mais de 100MB
                    st.warning("⚠️ Alto uso de memória detectado")
                else:
                    st.success("✅ Uso de memória normal")
                
                # Limpar dados de teste
                del large_dataset
                gc.collect()
                
                memory_analysis["memory_test"] = {
                    "memory_increase_mb": memory_increase,
                    "high_memory_usage": memory_increase > 100
                }
            
            # Teste de garbage collection
            if st.button("🗑️ TESTAR GARBAGE COLLECTION"):
                st.info("🔄 Executando garbage collection...")
                
                before_gc = process.memory_info().rss / 1024 / 1024
                
                # Forçar garbage collection
                collected = gc.collect()
                
                after_gc = process.memory_info().rss / 1024 / 1024
                memory_freed = before_gc - after_gc
                
                st.info(f"🗑️ Objetos coletados: {collected}")
                st.info(f"💾 Memória liberada: {memory_freed:.1f} MB")
                
                memory_analysis["gc_test"] = {
                    "objects_collected": collected,
                    "memory_freed_mb": memory_freed
                }
            
            self.analysis_results["memory_analysis"] = memory_analysis
        
        except ImportError:
            st.warning("⚠️ psutil não disponível - análise de memória limitada")
        except Exception as e:
            st.error(f"❌ Erro na análise de memória: {e}")
    
    def analyze_network_patterns(self):
        """Analisa padrões de rede que podem causar falhas"""
        st.header("🌐 5. ANÁLISE DE PADRÕES DE REDE")
        
        if st.button("🔍 TESTAR CONECTIVIDADE FIREBASE"):
            self._test_firebase_connectivity()
    
    def _test_firebase_connectivity(self):
        """Testa conectividade e latência com Firebase"""
        try:
            # Testar diferentes endpoints Firebase
            endpoints = [
                {"name": "Identity Toolkit", "url": "https://identitytoolkit.googleapis.com/v1/accounts:lookup"},
                {"name": "Firestore REST", "url": "https://firestore.googleapis.com/v1/projects/marmita-fit-6a3ca/databases/(default)/documents"},
                {"name": "Secure Token", "url": "https://securetoken.googleapis.com/v1/token"}
            ]
            
            st.subheader("📡 TESTE DE CONECTIVIDADE")
            
            connectivity_results = []
            
            for endpoint in endpoints:
                try:
                    st.info(f"🔄 Testando: {endpoint['name']}")
                    
                    # Teste de latência
                    start_time = time.time()
                    
                    # GET request simples para testar conectividade
                    response = requests.get(endpoint['url'], timeout=5)
                    
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000  # ms
                    
                    result = {
                        "endpoint": endpoint['name'],
                        "status_code": response.status_code,
                        "latency_ms": latency,
                        "accessible": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if latency < 500:  # Menos de 500ms
                        st.success(f"✅ {endpoint['name']}: {response.status_code} ({latency:.0f}ms)")
                    else:
                        st.warning(f"⚠️ {endpoint['name']}: {response.status_code} ({latency:.0f}ms) - Latência alta")
                    
                except requests.exceptions.Timeout:
                    result = {
                        "endpoint": endpoint['name'],
                        "error": "TIMEOUT",
                        "latency_ms": 5000,  # 5s timeout
                        "accessible": False
                    }
                    st.error(f"❌ {endpoint['name']}: TIMEOUT (>5s)")
                
                except requests.exceptions.RequestException as e:
                    result = {
                        "endpoint": endpoint['name'],
                        "error": str(e),
                        "accessible": False
                    }
                    st.error(f"❌ {endpoint['name']}: {str(e)}")
                
                connectivity_results.append(result)
            
            # Análise de conectividade
            accessible_count = sum(1 for r in connectivity_results if r.get('accessible', False))
            avg_latency = sum(r.get('latency_ms', 0) for r in connectivity_results if 'latency_ms' in r) / len(connectivity_results)
            
            st.subheader("📊 RESUMO DE CONECTIVIDADE")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Endpoints Acessíveis", f"{accessible_count}/{len(endpoints)}")
            
            with col2:
                st.metric("Latência Média", f"{avg_latency:.0f}ms")
            
            if accessible_count < len(endpoints):
                st.error("🚨 PROBLEMAS DE CONECTIVIDADE detectados")
                st.error("Causa provável: Rede, firewall ou proxy bloqueando Firebase")
            elif avg_latency > 1000:
                st.warning("⚠️ LATÊNCIA ALTA detectada")
                st.warning("Uploads podem falhar por timeout")
            else:
                st.success("✅ CONECTIVIDADE OK - problema não é de rede")
            
            self.analysis_results["connectivity_test"] = connectivity_results
        
        except Exception as e:
            st.error(f"🚨 Erro no teste de conectividade: {e}")
    
    def generate_batch_strategy(self):
        """Gera estratégia de batch baseada nas análises"""
        st.header("🎯 6. ESTRATÉGIA DE BATCH RECOMENDADA")
        
        # Compilar análises para gerar recomendação
        recommendations = {
            "recommended_batch_size": 25,
            "recommended_delay": 1.0,
            "confidence_level": "BAIXA",
            "reasoning": [],
            "alternative_strategies": []
        }
        
        # Análise baseada nos testes de batch
        if "batch_scenarios" in self.analysis_results and self.analysis_results["batch_scenarios"]:
            successful_scenarios = [s for s in self.analysis_results["batch_scenarios"] if s["success_rate"] == 100]
            
            if successful_scenarios:
                # Pegar o maior batch size que deu 100% sucesso
                best_scenario = max(successful_scenarios, key=lambda x: x["scenario"]["size"])
                
                recommendations["recommended_batch_size"] = best_scenario["scenario"]["size"]
                recommendations["recommended_delay"] = best_scenario["scenario"]["delay"] 
                recommendations["confidence_level"] = "ALTA"
                recommendations["reasoning"].append(f"Teste mostrou 100% sucesso com {best_scenario['scenario']['size']} items")
            else:
                # Nenhum cenário deu 100%, pegar o melhor
                if self.analysis_results["batch_scenarios"]:
                    best_scenario = max(self.analysis_results["batch_scenarios"], key=lambda x: x["success_rate"])
                    
                    recommendations["recommended_batch_size"] = best_scenario["scenario"]["size"]
                    recommendations["recommended_delay"] = best_scenario["scenario"]["delay"] * 2  # Dobrar delay
                    recommendations["confidence_level"] = "MÉDIA"
                    recommendations["reasoning"].append(f"Melhor cenário: {best_scenario['success_rate']:.1f}% sucesso")
        
        # Análise baseada no rate limiting
        if "rate_limit_tests" in self.analysis_results and self.analysis_results["rate_limit_tests"]:
            successful_rates = [r for r in self.analysis_results["rate_limit_tests"] if r["success_rate"] == 100]
            
            if successful_rates:
                fastest_safe = min(successful_rates, key=lambda x: x["test_config"]["delay"])
                
                if fastest_safe["test_config"]["delay"] < recommendations["recommended_delay"]:
                    recommendations["recommended_delay"] = fastest_safe["test_config"]["delay"]
                    recommendations["reasoning"].append(f"Rate limit OK com {fastest_safe['test_config']['delay']}s delay")
            else:
                # Rate limiting detectado - aumentar delay
                recommendations["recommended_delay"] = max(2.0, recommendations["recommended_delay"])
                recommendations["reasoning"].append("Rate limiting detectado - delay aumentado")
        
        # Análise de memória
        if "memory_analysis" in self.analysis_results:
            memory = self.analysis_results["memory_analysis"]
            
            if memory.get("memory_test", {}).get("high_memory_usage", False):
                recommendations["recommended_batch_size"] = min(10, recommendations["recommended_batch_size"])
                recommendations["reasoning"].append("Alto uso de memória - batch reduzido")
        
        # Análise de conectividade
        if "connectivity_test" in self.analysis_results:
            connectivity = self.analysis_results["connectivity_test"]
            accessible = sum(1 for r in connectivity in r.get('accessible', False))
            
            if accessible < len(connectivity):
                recommendations["recommended_delay"] = max(3.0, recommendations["recommended_delay"])
                recommendations["reasoning"].append("Problemas de conectividade - delay aumentado")
        
        # Estratégias alternativas
        current_state = self.analysis_results.get("current_state", {})
        missing_count = current_state.get("missing_count", 0)
        
        if missing_count > 150:
            recommendations["alternative_strategies"].append({
                "strategy": "UPLOAD INCREMENTAL",
                "description": "Fazer upload apenas dos ingredientes faltantes",
                "batch_size": 5,
                "delay": 2.0
            })
        
        if missing_count > 100:
            recommendations["alternative_strategies"].append({
                "strategy": "MANUAL CHUNKING", 
                "description": "Dividir 198 ingredientes em 4 grupos de ~50",
                "batch_size": 15,
                "delay": 1.5
            })
        
        recommendations["alternative_strategies"].append({
            "strategy": "ULTRA CONSERVADOR",
            "description": "Máxima garantia de sucesso",
            "batch_size": 1,
            "delay": 3.0
        })
        
        # Apresentar recomendações
        st.subheader(f"🎯 ESTRATÉGIA RECOMENDADA ({recommendations['confidence_level']} confiança)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Batch Size", recommendations['recommended_batch_size'])
            
        with col2:
            st.metric("Delay entre Batches", f"{recommendations['recommended_delay']}s")
        
        st.subheader("💡 RACIOCÍNIO")
        for reason in recommendations["reasoning"]:
            st.info(f"✅ {reason}")
        
        if not recommendations["reasoning"]:
            st.warning("⚠️ Análises insuficientes - usando defaults conservadores")
        
        # Estratégias alternativas
        if recommendations["alternative_strategies"]:
            st.subheader("🔄 ESTRATÉGIAS ALTERNATIVAS")
            
            for i, strategy in enumerate(recommendations["alternative_strategies"]):
                with st.expander(f"📋 {strategy['strategy']}", expanded=False):
                    st.info(strategy["description"])
                    st.info(f"Batch: {strategy['batch_size']}, Delay: {strategy['delay']}s")
        
        # Código para implementar
        st.subheader("🚀 PRÓXIMOS PASSOS")
        
        st.info("1. **Execute batch_upload_optimizer.py** com as configurações recomendadas:")
        st.code(f"""
Configurações:
- Batch Size: {recommendations['recommended_batch_size']}
- Delay entre lotes: {recommendations['recommended_delay']}s  
- Delay entre items: {recommendations['recommended_delay'] * 0.1}s
""")
        
        st.info("2. **Monitore** a taxa de sucesso durante o upload")
        st.info("3. **Se falhar**, tente estratégia ULTRA CONSERVADOR")
        st.info("4. **Se continuar falhando**, problema é arquitetural mais profundo")
        
        # Salvar recomendações
        self.analysis_results["recommendations"] = recommendations

def main():
    analyzer = Opus41BatchAnalyzer()
    analyzer.main()

if __name__ == "__main__":
    main()