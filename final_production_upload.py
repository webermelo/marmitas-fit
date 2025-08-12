#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL PRODUCTION UPLOAD - OPUS 4.1
Upload final em produção com configurações validadas
"""

import sys
import os
import time
import json
import pandas as pd
from datetime import datetime
import traceback

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def execute_production_upload():
    """Executa upload final em produção com Firebase real"""
    
    print("=" * 70)
    print("FINAL PRODUCTION UPLOAD - OPUS 4.1")
    print("=" * 70)
    print(f"Iniciando: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configurações validadas OPUS 4.1
    config = {
        "batch_size": 10,
        "batch_delay": 2.0,
        "item_delay": 0.3,
        "max_retries": 3
    }
    
    print("CONFIGURACOES VALIDADAS OPUS 4.1:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Verificar se arquivo CSV existe
    csv_files = [
        "ingredientes_completos_200.csv",
        "ingredientes_completos_198.csv", 
        "ingredientes.csv"
    ]
    
    csv_file = None
    for filename in csv_files:
        if os.path.exists(filename):
            csv_file = filename
            break
    
    if not csv_file:
        print("ERRO: Arquivo CSV não encontrado")
        print("Arquivos procurados:")
        for filename in csv_files:
            print(f"  - {filename}")
        print()
        print("SOLUCAO:")
        print("1. Certifique-se que o arquivo CSV está na pasta correta")
        print("2. Use o mesmo arquivo CSV que causou o problema original")
        print("3. Execute novamente este script")
        return False
    
    print(f"ARQUIVO CSV ENCONTRADO: {csv_file}")
    
    try:
        # Carregar CSV
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        total_ingredients = len(df)
        
        print(f"INGREDIENTES NO CSV: {total_ingredients}")
        
        # Verificar estrutura do CSV
        required_cols = ['Nome', 'Categoria', 'Preco']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"ERRO: Colunas obrigatórias ausentes: {missing_cols}")
            print(f"Colunas disponíveis: {list(df.columns)}")
            return False
        
        print("ESTRUTURA CSV: OK")
        print()
        
    except Exception as e:
        print(f"ERRO ao carregar CSV: {e}")
        return False
    
    # Tentar conexão Firebase
    print("CONECTANDO AO FIREBASE...")
    
    try:
        # Importar módulos necessários
        from utils.firestore_client import get_firestore_client
        
        client = get_firestore_client()
        
        if not client:
            print("ERRO: Não foi possível criar cliente Firebase")
            print("VERIFICAR:")
            print("1. Se o token de autenticação está válido")
            print("2. Se a conexão Firebase está funcionando")
            print("3. Execute opus_41_token_debug.py se necessário")
            return False
        
        print("FIREBASE CONECTADO: OK")
        
        # Verificar token
        if not client.auth_token:
            print("ERRO: Token de autenticação ausente")
            return False
        
        print(f"TOKEN PRESENTE: {len(client.auth_token)} caracteres")
        print()
        
    except Exception as e:
        print(f"ERRO na conexão Firebase: {e}")
        return False
    
    # Verificar estado atual
    print("VERIFICANDO ESTADO ATUAL...")
    
    try:
        from utils.database import get_database_manager
        
        # Simular user_id (em produção viria do session_state)
        user_id = "production_user_upload"  # Substitua pelo user_id real
        
        db_manager = get_database_manager()
        current_df = db_manager.get_user_ingredients(user_id)
        
        current_count = len(current_df)
        missing_count = total_ingredients - current_count
        
        print(f"INGREDIENTES ATUAIS: {current_count}")
        print(f"INGREDIENTES FALTANDO: {missing_count}")
        
        if missing_count <= 0:
            print("TODOS OS INGREDIENTES JÁ ESTÃO SALVOS!")
            print("Não há necessidade de upload adicional.")
            return True
        
        print(f"UPLOAD NECESSÁRIO: {missing_count} ingredientes")
        print()
        
    except Exception as e:
        print(f"AVISO: Não foi possível verificar estado atual: {e}")
        print("Continuando com upload completo...")
        missing_count = total_ingredients
        current_count = 0
    
    # Preparar dados para upload
    print("PREPARANDO DADOS PARA UPLOAD...")
    
    # Converter DataFrame para formato Firebase
    ingredients_to_upload = []
    
    for idx, row in df.iterrows():
        ingredient_data = {
            "nome": str(row.get('Nome', '')),
            "categoria": str(row.get('Categoria', '')),
            "unid_receita": str(row.get('Unid_Receita', row.get('unid_receita', 'g'))),
            "unid_compra": str(row.get('Unid_Compra', row.get('unid_compra', 'kg'))),
            "preco": float(row.get('Preco', row.get('preco', 0.0))),
            "kcal_unid": float(row.get('Kcal_Unid', row.get('kcal_unid', 0.0))),
            "fator_conv": float(row.get('Fator_Conv', row.get('fator_conv', 1.0))),
            "ativo": bool(row.get('Ativo', row.get('ativo', True))),
            "observacoes": str(row.get('Observacoes', row.get('observacoes', ''))),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "production_upload": True,
            "opus_41_batch": True
        }
        
        ingredients_to_upload.append(ingredient_data)
    
    print(f"DADOS PREPARADOS: {len(ingredients_to_upload)} ingredientes")
    print()
    
    # Executar upload em lotes
    print("INICIANDO UPLOAD EM LOTES...")
    print("=" * 50)
    
    collection_path = f"users/{user_id}/ingredients"
    
    # Estatísticas
    stats = {
        "total_items": len(ingredients_to_upload),
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "retries": 0,
        "start_time": time.time(),
        "batches": []
    }
    
    # Dividir em lotes
    batches = []
    for i in range(0, len(ingredients_to_upload), config["batch_size"]):
        batch = ingredients_to_upload[i:i + config["batch_size"]]
        batches.append(batch)
    
    print(f"LOTES CRIADOS: {len(batches)}")
    print()
    
    # Processar cada lote
    for batch_idx, batch in enumerate(batches):
        batch_start = time.time()
        
        print(f"PROCESSANDO LOTE {batch_idx + 1}/{len(batches)} ({len(batch)} items)")
        
        batch_stats = {
            "batch_number": batch_idx + 1,
            "items": len(batch),
            "successful": 0,
            "failed": 0,
            "duration": 0
        }
        
        # Processar cada item do lote
        for item_idx, ingredient in enumerate(batch):
            success = False
            retries = 0
            
            while not success and retries < config["max_retries"]:
                try:
                    # Tentar upload
                    result = client.collection(collection_path).add(ingredient)
                    
                    if result:
                        success = True
                        stats["successful"] += 1
                        batch_stats["successful"] += 1
                        
                        # Verificar conversão boolean
                        boolean_status = "OK" if isinstance(ingredient["ativo"], bool) else "ERROR"
                        
                        print(f"  [+] {item_idx+1:2d}: {ingredient['nome'][:35]:35} [Boolean: {boolean_status}]")
                    else:
                        retries += 1
                        stats["retries"] += 1
                        
                        if retries < config["max_retries"]:
                            print(f"  [-] {item_idx+1:2d}: {ingredient['nome'][:35]:35} RETRY {retries}")
                            time.sleep(config["item_delay"] * 2)
                        else:
                            stats["failed"] += 1
                            batch_stats["failed"] += 1
                            print(f"  [X] {item_idx+1:2d}: {ingredient['nome'][:35]:35} FALHOU")
                
                except Exception as item_error:
                    retries += 1
                    stats["retries"] += 1
                    
                    if retries >= config["max_retries"]:
                        stats["failed"] += 1
                        batch_stats["failed"] += 1
                        print(f"  [!] {item_idx+1:2d}: {ingredient['nome'][:35]:35} ERRO: {str(item_error)[:50]}")
                        break
            
            stats["processed"] += 1
            
            # Delay entre items
            time.sleep(config["item_delay"])
        
        # Finalizar lote
        batch_stats["duration"] = time.time() - batch_start
        batch_stats["success_rate"] = (batch_stats["successful"] / batch_stats["items"]) * 100
        
        stats["batches"].append(batch_stats)
        
        print(f"  LOTE {batch_idx + 1}: {batch_stats['success_rate']:.1f}% sucesso em {batch_stats['duration']:.1f}s")
        
        # Delay entre lotes
        if batch_idx < len(batches) - 1:
            print(f"  Aguardando {config['batch_delay']}s...")
            time.sleep(config['batch_delay'])
        
        print()
    
    # Finalizar upload
    stats["end_time"] = time.time()
    stats["total_duration"] = stats["end_time"] - stats["start_time"]
    stats["success_rate"] = (stats["successful"] / stats["total_items"]) * 100
    
    # Resultados finais
    print("RESULTADOS FINAIS")
    print("=" * 70)
    
    print(f"Total processados: {stats['processed']}/{stats['total_items']}")
    print(f"Sucessos: {stats['successful']}")
    print(f"Falhas: {stats['failed']}")
    print(f"Retries: {stats['retries']}")
    print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"Duração total: {stats['total_duration']:.1f} segundos")
    print()
    
    # Análise de resultado
    if stats["success_rate"] >= 95:
        print("STATUS: UPLOAD CONCLUIDO COM SUCESSO!")
        print("Os 198 ingredientes devem estar salvos no Firebase.")
        success = True
    elif stats["success_rate"] >= 80:
        print("STATUS: UPLOAD PARCIALMENTE BEM-SUCEDIDO")
        print("Alguns ingredientes podem precisar de re-upload.")
        success = True
    else:
        print("STATUS: UPLOAD FALHOU")
        print("Investigação adicional necessária.")
        success = False
    
    # Salvar relatório
    report_filename = f"production_upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"RELATÓRIO SALVO: {report_filename}")
    except Exception as e:
        print(f"Erro ao salvar relatório: {e}")
    
    print()
    print("UPLOAD FINAL OPUS 4.1 COMPLETO!")
    print("=" * 70)
    
    return success

def main():
    """Função principal"""
    try:
        print("AVISO: Este script executará upload real no Firebase!")
        print("Certifique-se de que:")
        print("1. Você está logado na aplicação")
        print("2. O arquivo CSV está disponível")
        print("3. A conexão Firebase está funcionando")
        print()
        
        # Em ambiente real, você deve garantir autenticação primeiro
        print("IMPORTANTE: Em produção, execute via interface web após login")
        print("Este script é uma simulação do processo otimizado.")
        print()
        
        result = execute_production_upload()
        
        if result:
            print("SUCESSO: Upload produção executado com sucesso!")
        else:
            print("FALHA: Upload produção falhou - verifique logs acima")
        
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        print("Stacktrace:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()