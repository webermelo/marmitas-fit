#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUÇÃO AUTOMÁTICA DA ANÁLISE OPUS 4.1
Script que executa automaticamente as ferramentas de análise
"""

import streamlit as st
import subprocess
import sys
import time
from datetime import datetime
import json
import os

def main():
    st.set_page_config(
        page_title="OPUS 4.1 - Auto Execute Analysis",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 OPUS 4.1 AUTO EXECUTE ANALYSIS")
    st.markdown("---")
    
    st.error("🔬 EXECUTANDO ANÁLISE PROFUNDA DO UPLOAD PARCIAL")
    
    if 'user' not in st.session_state:
        st.error("❌ Faça login primeiro")
        if st.button("🔄 IR PARA LOGIN"):
            st.switch_page("app.py")
        return
    
    st.success(f"✅ Usuário logado: {st.session_state.user.get('uid', 'Unknown')[:10]}...")
    
    # Verificar estado atual rápido
    st.header("📊 VERIFICAÇÃO INICIAL RÁPIDA")
    
    try:
        from utils.database import get_database_manager
        
        db_manager = get_database_manager()
        user_id = st.session_state.user['uid']
        current_df = db_manager.get_user_ingredients(user_id)
        
        current_count = len(current_df)
        missing_count = 198 - current_count
        success_rate = (current_count / 198) * 100 if current_count > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Ingredientes Salvos", current_count)
        
        with col2:
            st.metric("Faltando", missing_count)
            if missing_count > 0:
                st.error(f"❌ {missing_count} ingredientes não salvos")
        
        with col3:
            st.metric("Taxa Sucesso", f"{success_rate:.1f}%")
            if success_rate < 100:
                st.warning(f"⚠️ Upload {100-success_rate:.1f}% incompleto")
        
        if missing_count == 0:
            st.success("🎉 TODOS OS 198 INGREDIENTES ESTÃO SALVOS!")
            st.info("✅ O problema foi resolvido! Não há mais ingredientes faltantes.")
            return
        
        st.info(f"🎯 **PROBLEMA CONFIRMADO**: {missing_count} ingredientes faltantes de 198 esperados")
    
    except Exception as e:
        st.error(f"❌ Erro na verificação inicial: {e}")
        current_count = 0
        missing_count = 198
    
    # Executar análises automaticamente
    st.header("🔬 EXECUTANDO ANÁLISES OPUS 4.1")
    
    if st.button("🚀 EXECUTAR ANÁLISE COMPLETA", type="primary"):
        execute_comprehensive_analysis(current_count, missing_count)

def execute_comprehensive_analysis(current_count, missing_count):
    """Executa análise completa automatizada"""
    
    st.subheader("📋 1. ANÁLISE DO ESTADO ATUAL")
    
    # Análise básica do estado atual
    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "initial_state": {
            "ingredients_saved": current_count,
            "ingredients_missing": missing_count,
            "expected_total": 198,
            "success_rate": (current_count / 198) * 100
        }
    }
    
    # Categorização do problema
    if missing_count > 150:
        problem_severity = "CRÍTICO"
        problem_type = "FALHA_MASSIVA"
        st.error(f"🚨 PROBLEMA CRÍTICO: {missing_count} ingredientes faltando")
    elif missing_count > 100:
        problem_severity = "ALTO"
        problem_type = "FALHA_PARCIAL_GRANDE"
        st.error(f"❌ PROBLEMA ALTO: {missing_count} ingredientes faltando")
    elif missing_count > 50:
        problem_severity = "MÉDIO"
        problem_type = "FALHA_PARCIAL_MÉDIA"
        st.warning(f"⚠️ PROBLEMA MÉDIO: {missing_count} ingredientes faltando")
    else:
        problem_severity = "BAIXO"
        problem_type = "FALHA_PARCIAL_PEQUENA"
        st.info(f"ℹ️ PROBLEMA PEQUENO: {missing_count} ingredientes faltando")
    
    analysis_results["problem_classification"] = {
        "severity": problem_severity,
        "type": problem_type,
        "description": f"{missing_count} de 198 ingredientes não foram salvos"
    }
    
    # Análise de distribuição se há dados
    st.subheader("📊 2. ANÁLISE DE DISTRIBUIÇÃO")
    
    try:
        from utils.database import get_database_manager
        
        db_manager = get_database_manager()
        user_id = st.session_state.user['uid']
        current_df = db_manager.get_user_ingredients(user_id)
        
        if not current_df.empty and 'Categoria' in current_df.columns:
            category_dist = current_df['Categoria'].value_counts()
            
            st.bar_chart(category_dist)
            
            # Identificar possíveis padrões
            total_categories = len(category_dist)
            if total_categories > 0:
                avg_per_category = len(current_df) / total_categories
                
                underrepresented = category_dist[category_dist < avg_per_category * 0.5]
                
                if not underrepresented.empty:
                    st.warning("⚠️ CATEGORIAS SUB-REPRESENTADAS:")
                    pattern_found = True
                    for cat, count in underrepresented.items():
                        st.error(f"❌ {cat}: apenas {count} ingredientes")
                else:
                    st.success("✅ Distribuição por categoria parece uniforme")
                    pattern_found = False
                
                analysis_results["distribution_analysis"] = {
                    "categories_total": total_categories,
                    "avg_per_category": avg_per_category,
                    "underrepresented_categories": underrepresented.to_dict() if not underrepresented.empty else {},
                    "pattern_found": pattern_found
                }
        else:
            st.warning("⚠️ Sem dados suficientes para análise de distribuição")
    
    except Exception as e:
        st.error(f"❌ Erro na análise de distribuição: {e}")
    
    # Teste rápido de conectividade Firebase
    st.subheader("🔥 3. TESTE DE CONECTIVIDADE FIREBASE")
    
    firebase_test = test_firebase_connection()
    analysis_results["firebase_test"] = firebase_test
    
    # Teste de upload controlado
    st.subheader("🧪 4. TESTE DE UPLOAD CONTROLADO")
    
    upload_test = test_controlled_upload()
    analysis_results["upload_test"] = upload_test
    
    # Análise de padrões e hipóteses
    st.subheader("🎯 5. ANÁLISE DE PADRÕES E HIPÓTESES")
    
    hypotheses = generate_hypotheses(analysis_results)
    analysis_results["hypotheses"] = hypotheses
    
    # Mostrar hipóteses
    for i, hypothesis in enumerate(hypotheses):
        with st.expander(f"💡 Hipótese {i+1}: {hypothesis['name']} ({hypothesis['probability']} probabilidade)", expanded=True):
            st.info(f"**Evidência**: {hypothesis['evidence']}")
            st.info(f"**Causa**: {hypothesis['cause']}")
            st.info(f"**Solução**: {hypothesis['solution']}")
    
    # Estratégia recomendada
    st.subheader("🚀 6. ESTRATÉGIA RECOMENDADA")
    
    strategy = generate_strategy(analysis_results)
    analysis_results["recommended_strategy"] = strategy
    
    # Mostrar estratégia
    st.success(f"🎯 **ESTRATÉGIA PRINCIPAL**: {strategy['name']}")
    st.info(f"**Configuração**: {strategy['config']}")
    st.info(f"**Passos**: {strategy['steps']}")
    
    if strategy.get('alternative'):
        st.warning(f"🔄 **ALTERNATIVA**: {strategy['alternative']}")
    
    # Gerar relatório final
    st.subheader("📋 7. RELATÓRIO FINAL")
    
    # Salvar relatório
    report_filename = f"opus_41_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    json_report = json.dumps(analysis_results, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 BAIXAR RELATÓRIO COMPLETO",
        data=json_report,
        file_name=report_filename,
        mime="application/json"
    )
    
    # Próximos passos
    st.subheader("🎯 PRÓXIMOS PASSOS")
    
    next_steps = [
        f"1. **Implementar estratégia**: {strategy['name']}",
        "2. **Usar batch_upload_optimizer.py** com configurações recomendadas",
        f"3. **Monitorar upload** dos {missing_count} ingredientes faltantes",
        "4. **Validar resultado** - confirmar 198 ingredientes salvos",
        "5. **Documentar solução** para prevenção futura"
    ]
    
    for step in next_steps:
        st.markdown(step)
    
    # Status final
    st.success(f"✅ ANÁLISE OPUS 4.1 COMPLETA - {len(hypotheses)} hipóteses geradas")
    st.info("👉 Use o relatório JSON para implementar a solução recomendada")

def test_firebase_connection():
    """Teste rápido de conectividade Firebase"""
    try:
        from utils.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        
        if client:
            st.success("✅ Cliente Firebase criado com sucesso")
            
            if client.auth_token:
                st.success(f"✅ Token autenticação presente ({len(client.auth_token)} chars)")
                
                # Teste simples de conectividade
                user_id = st.session_state.user['uid']
                test_path = f"users/{user_id}/connectivity_test"
                
                try:
                    # Teste GET
                    docs = client.collection(test_path).get()
                    
                    st.success(f"✅ Operação GET funcionou (retornou {len(docs) if docs else 0} docs)")
                    
                    return {
                        "client_created": True,
                        "token_present": True,
                        "get_operation": True,
                        "status": "OK"
                    }
                    
                except Exception as op_error:
                    st.error(f"❌ Operação Firebase falhou: {op_error}")
                    
                    return {
                        "client_created": True,
                        "token_present": True,
                        "get_operation": False,
                        "error": str(op_error),
                        "status": "OPERATION_FAILED"
                    }
            else:
                st.error("❌ Cliente sem token de autenticação")
                
                return {
                    "client_created": True,
                    "token_present": False,
                    "status": "NO_TOKEN"
                }
        else:
            st.error("❌ Falha ao criar cliente Firebase")
            
            return {
                "client_created": False,
                "status": "CLIENT_FAILED"
            }
    
    except Exception as e:
        st.error(f"❌ Erro no teste Firebase: {e}")
        
        return {
            "error": str(e),
            "status": "EXCEPTION"
        }

def test_controlled_upload():
    """Teste controlado com 3 ingredientes"""
    st.info("🧪 Testando upload de 3 ingredientes...")
    
    try:
        from utils.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        if not client:
            st.error("❌ Cliente Firebase não disponível")
            return {"status": "CLIENT_FAILED"}
        
        user_id = st.session_state.user['uid']
        collection_path = f"users/{user_id}/test_upload"
        
        # 3 ingredientes de teste
        test_ingredients = [
            {
                "nome": f"TesteOpus41_1_{datetime.now().strftime('%H%M%S')}",
                "categoria": "Teste",
                "preco": 10.0,
                "ativo": True,
                "test_session": "opus_41_auto_analysis",
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            },
            {
                "nome": f"TesteOpus41_2_{datetime.now().strftime('%H%M%S')}",
                "categoria": "Teste",
                "preco": 20.0,
                "ativo": False,
                "test_session": "opus_41_auto_analysis",
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            },
            {
                "nome": f"TesteOpus41_3_{datetime.now().strftime('%H%M%S')}",
                "categoria": "Teste",
                "preco": 30.0,
                "ativo": True,
                "test_session": "opus_41_auto_analysis",
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
        ]
        
        results = {
            "total_attempts": len(test_ingredients),
            "successful": 0,
            "failed": 0,
            "attempts": []
        }
        
        for i, ingredient in enumerate(test_ingredients):
            try:
                start_time = time.time()
                result = client.collection(collection_path).add(ingredient)
                duration = time.time() - start_time
                
                if result:
                    results["successful"] += 1
                    st.success(f"✅ Item {i+1}: {ingredient['nome']} ({duration:.2f}s)")
                    
                    attempt_log = {
                        "index": i,
                        "status": "SUCCESS",
                        "duration": duration,
                        "name": ingredient['nome']
                    }
                else:
                    results["failed"] += 1
                    st.error(f"❌ Item {i+1}: {ingredient['nome']} - Sem resultado")
                    
                    attempt_log = {
                        "index": i,
                        "status": "NO_RESULT", 
                        "duration": duration,
                        "name": ingredient['nome']
                    }
                
                results["attempts"].append(attempt_log)
                
                # Pequeno delay
                time.sleep(0.5)
            
            except Exception as item_error:
                results["failed"] += 1
                st.error(f"🚨 Item {i+1}: EXCEÇÃO - {str(item_error)}")
                
                attempt_log = {
                    "index": i,
                    "status": "EXCEPTION",
                    "error": str(item_error),
                    "name": ingredient['nome']
                }
                results["attempts"].append(attempt_log)
        
        results["success_rate"] = (results["successful"] / results["total_attempts"]) * 100
        results["status"] = "COMPLETED"
        
        # Resultado final do teste
        if results["success_rate"] == 100:
            st.success(f"🎉 TESTE CONTROLADO: 100% sucesso ({results['successful']}/{results['total_attempts']})")
        elif results["success_rate"] > 0:
            st.warning(f"⚠️ TESTE CONTROLADO: {results['success_rate']:.1f}% sucesso ({results['successful']}/{results['total_attempts']})")
        else:
            st.error(f"❌ TESTE CONTROLADO: 0% sucesso - FALHA TOTAL")
        
        return results
    
    except Exception as e:
        st.error(f"🚨 Erro no teste controlado: {e}")
        return {
            "status": "EXCEPTION",
            "error": str(e)
        }

def generate_hypotheses(analysis_results):
    """Gera hipóteses baseadas nos dados coletados"""
    
    hypotheses = []
    
    # Análise do estado inicial
    missing_count = analysis_results["initial_state"]["ingredients_missing"]
    success_rate = analysis_results["initial_state"]["success_rate"]
    
    # Hipótese 1: Rate Limiting
    if missing_count > 100:
        hypotheses.append({
            "name": "RATE LIMITING FIREBASE",
            "probability": "ALTA",
            "evidence": f"{missing_count} ingredientes faltando sugere limitação de operações/segundo",
            "cause": "Firebase limitou uploads por excesso de requisições simultâneas",
            "solution": "Upload em lotes pequenos (10-25) com delays de 1-2s"
        })
    
    # Hipótese 2: Timeout/Interrupção
    if missing_count > 50:
        hypotheses.append({
            "name": "TIMEOUT APLICAÇÃO",
            "probability": "ALTA",
            "evidence": f"Upload parcial de {success_rate:.1f}% indica interrupção",
            "cause": "Streamlit ou browser interrompeu por tempo limite",
            "solution": "Upload incremental com progresso visível e checkpoints"
        })
    
    # Hipótese 3: Baseada no teste de upload
    upload_test = analysis_results.get("upload_test", {})
    
    if upload_test.get("success_rate", 0) < 100:
        hypotheses.append({
            "name": "PROBLEMA SISTÊMICO",
            "probability": "ALTA",
            "evidence": f"Teste controlado falhou {100 - upload_test.get('success_rate', 0):.1f}% das vezes",
            "cause": "Problema fundamental na implementação ou configuração",
            "solution": "Debug profundo + possível reescrita do sistema upload"
        })
    
    # Hipótese 4: Conectividade
    firebase_test = analysis_results.get("firebase_test", {})
    
    if firebase_test.get("status") != "OK":
        hypotheses.append({
            "name": "PROBLEMA CONECTIVIDADE",
            "probability": "MÉDIA",
            "evidence": f"Teste Firebase status: {firebase_test.get('status', 'Unknown')}",
            "cause": "Conectividade instável ou configuração Firebase incorreta",
            "solution": "Verificar configuração + implementar retry robusto"
        })
    
    # Hipótese 5: Dados específicos
    distribution = analysis_results.get("distribution_analysis", {})
    
    if distribution.get("pattern_found", False):
        hypotheses.append({
            "name": "DADOS PROBLEMÁTICOS",
            "probability": "MÉDIA", 
            "evidence": "Categorias sub-representadas indicam problemas específicos",
            "cause": "Alguns ingredientes têm dados que causam falha",
            "solution": "Validação prévia + sanitização de dados problemáticos"
        })
    
    # Hipótese padrão se não houver evidências específicas
    if not hypotheses:
        hypotheses.append({
            "name": "FALHA DE VOLUME",
            "probability": "MÉDIA",
            "evidence": f"{missing_count} ingredientes não processados de 198",
            "cause": "Sistema não consegue processar volume de 198 itens",
            "solution": "Upload em batches pequenos com monitoramento"
        })
    
    return hypotheses

def generate_strategy(analysis_results):
    """Gera estratégia recomendada baseada na análise"""
    
    missing_count = analysis_results["initial_state"]["ingredients_missing"]
    upload_test = analysis_results.get("upload_test", {})
    hypotheses = analysis_results.get("hypotheses", [])
    
    # Estratégia baseada na hipótese de maior probabilidade
    main_hypothesis = None
    for hyp in hypotheses:
        if hyp["probability"] == "ALTA":
            main_hypothesis = hyp
            break
    
    if not main_hypothesis and hypotheses:
        main_hypothesis = hypotheses[0]  # Primeira hipótese
    
    # Configuração baseada no número de ingredientes faltantes
    if missing_count > 150:
        # Problema crítico - estratégia ultra conservadora
        strategy = {
            "name": "ULTRA CONSERVADOR",
            "config": "Batch size: 5, Delay: 3.0s entre lotes, 0.5s entre items",
            "steps": "1. Upload em micro-lotes, 2. Validação após cada lote, 3. Retry automático",
            "batch_size": 5,
            "batch_delay": 3.0,
            "item_delay": 0.5,
            "alternative": "Upload manual 1 por vez se falhar"
        }
    elif missing_count > 100:
        # Problema alto - estratégia conservadora
        strategy = {
            "name": "CONSERVADOR",
            "config": "Batch size: 10, Delay: 2.0s entre lotes, 0.2s entre items", 
            "steps": "1. Upload em lotes pequenos, 2. Monitor progresso, 3. Retry falhas",
            "batch_size": 10,
            "batch_delay": 2.0,
            "item_delay": 0.2,
            "alternative": "Reduzir para batch size 5 se falhar"
        }
    elif missing_count > 50:
        # Problema médio - estratégia moderada
        strategy = {
            "name": "MODERADO",
            "config": "Batch size: 20, Delay: 1.0s entre lotes, 0.1s entre items",
            "steps": "1. Upload em lotes médios, 2. Monitor taxa sucesso, 3. Ajustar se necessário",
            "batch_size": 20,
            "batch_delay": 1.0,
            "item_delay": 0.1,
            "alternative": "Aumentar delay se rate limiting"
        }
    else:
        # Problema pequeno - estratégia normal
        strategy = {
            "name": "NORMAL",
            "config": "Batch size: 25, Delay: 0.5s entre lotes, 0.05s entre items",
            "steps": "1. Upload normal, 2. Monitor, 3. Completar restantes",
            "batch_size": 25,
            "batch_delay": 0.5,
            "item_delay": 0.05,
            "alternative": "Sem alternativa necessária"
        }
    
    # Ajustar baseado no teste de upload
    if upload_test.get("success_rate", 100) < 100:
        # Se teste falhou, usar estratégia mais conservadora
        strategy["batch_size"] = max(1, strategy["batch_size"] // 2)
        strategy["batch_delay"] = strategy["batch_delay"] * 2
        strategy["name"] += " (AJUSTADO POR FALHAS)"
    
    return strategy

if __name__ == "__main__":
    main()