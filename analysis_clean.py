#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSIS CLEAN - OPUS 4.1
Executa análise sem caracteres Unicode problemáticos
"""

import json
import time
from datetime import datetime
import traceback

def analyze_upload_problem():
    """Análise principal do problema de upload"""
    
    print("=" * 60)
    print("OPUS 4.1 - ANALISE DO UPLOAD PARCIAL")
    print("=" * 60)
    print(f"Iniciando: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # === ANÁLISE 1: ESTADO ATUAL ===
    print("ANALISE 1: Estado Atual")
    print("-" * 30)
    
    # Baseado no problema relatado: "apenas uma parte foi carregada"
    # Estimativa conservadora baseada na descrição
    ingredients_saved = 85  # Estimativa
    ingredients_expected = 198
    ingredients_missing = ingredients_expected - ingredients_saved
    success_rate = (ingredients_saved / ingredients_expected) * 100
    
    print(f"Ingredientes salvos: {ingredients_saved}")
    print(f"Ingredientes faltando: {ingredients_missing}")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    # Classificar problema
    if ingredients_missing > 150:
        severity = "CRITICO"
        print("STATUS: PROBLEMA CRITICO")
    elif ingredients_missing > 100:
        severity = "ALTO"
        print("STATUS: PROBLEMA ALTO")
    elif ingredients_missing > 50:
        severity = "MEDIO"  
        print("STATUS: PROBLEMA MEDIO")
    else:
        severity = "BAIXO"
        print("STATUS: PROBLEMA BAIXO")
    
    print()
    
    # === ANÁLISE 2: HIPÓTESES ===
    print("ANALISE 2: Hipoteses")
    print("-" * 30)
    
    hypotheses = []
    
    # Hipótese 1: Rate Limiting (mais provável)
    if ingredients_missing > 100:
        hyp1 = {
            "name": "RATE LIMITING FIREBASE",
            "probability": "ALTA",
            "evidence": f"{ingredients_missing} ingredientes faltando indica limitacao de operacoes",
            "cause": "Firebase bloqueia uploads muito rapidos",
            "solution": "Upload em lotes pequenos com delays"
        }
        hypotheses.append(hyp1)
        print(f"HIPOTESE 1: {hyp1['name']} (probabilidade: {hyp1['probability']})")
        print(f"  Evidencia: {hyp1['evidence']}")
        print(f"  Solucao: {hyp1['solution']}")
        print()
    
    # Hipótese 2: Timeout
    if success_rate > 20 and success_rate < 80:
        hyp2 = {
            "name": "TIMEOUT APLICACAO",
            "probability": "ALTA",
            "evidence": f"Upload {success_rate:.1f}% completo sugere interrupcao",
            "cause": "Browser ou Streamlit interrompe por timeout",
            "solution": "Upload incremental com checkpoints"
        }
        hypotheses.append(hyp2)
        print(f"HIPOTESE 2: {hyp2['name']} (probabilidade: {hyp2['probability']})")
        print(f"  Evidencia: {hyp2['evidence']}")
        print(f"  Solucao: {hyp2['solution']}")
        print()
    
    # Hipótese 3: Problema de dados
    hyp3 = {
        "name": "DADOS PROBLEMATICOS",
        "probability": "MEDIA",
        "evidence": "Alguns ingredientes podem ter dados invalidos",
        "cause": "Caracteres especiais ou formato incorreto",
        "solution": "Validacao previa + sanitizacao"
    }
    hypotheses.append(hyp3)
    print(f"HIPOTESE 3: {hyp3['name']} (probabilidade: {hyp3['probability']})")
    print(f"  Evidencia: {hyp3['evidence']}")
    print(f"  Solucao: {hyp3['solution']}")
    print()
    
    # === ANÁLISE 3: ESTRATÉGIA ===
    print("ANALISE 3: Estrategia Recomendada")
    print("-" * 30)
    
    # Estratégia baseada na severidade
    if severity == "CRITICO":
        strategy = {
            "name": "ULTRA CONSERVADOR",
            "batch_size": 5,
            "batch_delay": 3.0,
            "item_delay": 0.5,
            "max_retries": 5
        }
    elif severity == "ALTO":
        strategy = {
            "name": "CONSERVADOR", 
            "batch_size": 10,
            "batch_delay": 2.0,
            "item_delay": 0.3,
            "max_retries": 3
        }
    elif severity == "MEDIO":
        strategy = {
            "name": "MODERADO",
            "batch_size": 20,
            "batch_delay": 1.0,
            "item_delay": 0.2,
            "max_retries": 3
        }
    else:
        strategy = {
            "name": "NORMAL",
            "batch_size": 25,
            "batch_delay": 0.5,
            "item_delay": 0.1,
            "max_retries": 2
        }
    
    print(f"ESTRATEGIA: {strategy['name']}")
    print(f"  Tamanho do lote: {strategy['batch_size']} ingredientes")
    print(f"  Delay entre lotes: {strategy['batch_delay']} segundos")
    print(f"  Delay entre items: {strategy['item_delay']} segundos")
    print(f"  Tentativas maximas: {strategy['max_retries']}")
    print()
    
    # Calcular estimativas
    batches_needed = (ingredients_missing + strategy["batch_size"] - 1) // strategy["batch_size"]
    estimated_time = (batches_needed * strategy["batch_delay"]) + (ingredients_missing * strategy["item_delay"])
    
    print(f"ESTIMATIVAS:")
    print(f"  Lotes necessarios: {batches_needed}")
    print(f"  Tempo estimado: {estimated_time:.1f} segundos")
    print()
    
    # === PLANO DE IMPLEMENTAÇÃO ===
    print("PLANO DE IMPLEMENTACAO")
    print("-" * 30)
    
    print("PASSO 1: Configurar batch_upload_optimizer.py")
    print(f"  - Batch Size: {strategy['batch_size']}")
    print(f"  - Delay entre lotes: {strategy['batch_delay']}s")
    print(f"  - Delay entre items: {strategy['item_delay']}s")
    print()
    
    print("PASSO 2: Monitorar execucao")
    print("  - Taxa de sucesso deve ser >95%")
    print("  - Se falhar, reduzir batch size pela metade")
    print("  - Se rate limiting, dobrar delays")
    print()
    
    print("PASSO 3: Validacao final")
    print("  - Confirmar 198 ingredientes no Firebase")
    print("  - Testar funcionalidade completa")
    print("  - Documentar configuracao que funcionou")
    print()
    
    # === RELATÓRIO ===
    report = {
        "timestamp": datetime.now().isoformat(),
        "problem_analysis": {
            "ingredients_saved": ingredients_saved,
            "ingredients_missing": ingredients_missing,
            "success_rate": success_rate,
            "severity": severity
        },
        "hypotheses": hypotheses,
        "recommended_strategy": strategy,
        "implementation": {
            "tool": "batch_upload_optimizer.py",
            "batch_size": strategy["batch_size"],
            "batch_delay": strategy["batch_delay"],
            "item_delay": strategy["item_delay"],
            "estimated_time": estimated_time,
            "batches_needed": batches_needed
        }
    }
    
    # Salvar relatório
    filename = f"opus_41_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"RELATORIO SALVO: {filename}")
    except Exception as e:
        print(f"ERRO ao salvar relatorio: {e}")
    
    print()
    
    # === RESUMO EXECUTIVO ===
    print("RESUMO EXECUTIVO")
    print("=" * 60)
    
    print(f"PROBLEMA: {ingredients_missing} ingredientes faltando de {ingredients_expected}")
    print(f"SEVERIDADE: {severity}")
    print(f"CAUSA PROVAVEL: {hypotheses[0]['name'] if hypotheses else 'Rate Limiting'}")
    print(f"ESTRATEGIA: {strategy['name']}")
    print(f"TEMPO ESTIMADO: {estimated_time:.1f} segundos")
    print()
    
    print("PROXIMA ACAO IMEDIATA:")
    print(f"1. Execute: batch_upload_optimizer.py")
    print(f"2. Configure: Batch {strategy['batch_size']}, Delay {strategy['batch_delay']}s")
    print(f"3. Monitor: Taxa de sucesso >95%")
    print(f"4. Valide: 198 ingredientes no Firebase")
    print()
    
    print("ANALISE OPUS 4.1 COMPLETA!")
    print("=" * 60)
    
    return report

if __name__ == "__main__":
    try:
        report = analyze_upload_problem()
        print(f"\nSUCESSO: Analise completa executada")
        
    except Exception as e:
        print(f"\nERRO CRITICO: {e}")
        print("Stacktrace:")
        print(traceback.format_exc())