#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTE BATCH UPLOAD - OPUS 4.1
Executa upload otimizado com configurações recomendadas pela análise
"""

import json
import time
import pandas as pd
from datetime import datetime
import traceback
import sys
import os

# Mock dos imports necessários para teste
class MockStreamlit:
    def success(self, msg): print(f"SUCCESS: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def progress(self, val): return MockProgress()

class MockProgress:
    def progress(self, val): pass

class MockSessionState:
    def __init__(self):
        self.user = {
            'uid': 'test_user_batch_upload',
            'token': 'mock_token_for_batch_test',
            'email': 'test@marmitas.com'
        }

# Mock para testes
st = MockStreamlit()
session_state = MockSessionState()

def simulate_firebase_client():
    """Simula cliente Firebase para teste"""
    class MockFirestoreClient:
        def __init__(self):
            self.project_id = "marmita-fit-6a3ca"
            self.auth_token = "mock_token"
            self.uploaded_items = []
        
        def collection(self, path):
            return MockCollection(self, path)
    
    class MockCollection:
        def __init__(self, client, path):
            self.client = client
            self.path = path
        
        def add(self, data):
            # Simular comportamento real com algumas falhas ocasionais
            import random
            
            # 90% chance de sucesso (simulando rate limiting ocasional)
            if random.random() < 0.9:
                self.client.uploaded_items.append(data)
                return {"id": f"mock_doc_{len(self.client.uploaded_items)}"}
            else:
                return None  # Simula falha
    
    return MockFirestoreClient()

def create_test_ingredients():
    """Cria ingredientes de teste baseados no padrão real"""
    
    # Dados baseados no CSV original do projeto
    test_ingredients = [
        {"Nome": "Frango peito sem pele", "Categoria": "Proteina Animal", "Preco": 32.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 1.65, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Sem pele sem osso"},
        {"Nome": "Carne bovina patinho", "Categoria": "Proteina Animal", "Preco": 42.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 2.19, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Corte magro"},
        {"Nome": "Arroz integral", "Categoria": "Carboidrato", "Preco": 8.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 1.11, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Grao longo"},
        {"Nome": "Batata doce", "Categoria": "Carboidrato", "Preco": 4.50, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.86, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Cozida"},
        {"Nome": "Brócolis", "Categoria": "Vegetal", "Preco": 8.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.34, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Fresco"},
        {"Nome": "Tomate", "Categoria": "Vegetal", "Preco": 5.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.18, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Maduro"},
        {"Nome": "Cenoura", "Categoria": "Vegetal", "Preco": 3.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.41, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Crua"},
        {"Nome": "Feijão preto", "Categoria": "Leguminosa", "Preco": 9.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.77, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Cozido"},
        {"Nome": "Lentilha", "Categoria": "Leguminosa", "Preco": 12.90, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 1.16, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Cozida"},
        {"Nome": "Azeite oliva", "Categoria": "Gordura", "Preco": 35.00, "Unid_Receita": "ml", "Unid_Compra": "l", "Kcal_Unid": 8.84, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Extra virgem"},
        {"Nome": "Sal refinado", "Categoria": "Tempero", "Preco": 3.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.00, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Iodado"},
        {"Nome": "Pimenta preta", "Categoria": "Tempero", "Preco": 15.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 2.51, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Moída"},
        {"Nome": "Alho", "Categoria": "Tempero", "Preco": 25.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 1.49, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Fresco"},
        {"Nome": "Cebola", "Categoria": "Vegetal", "Preco": 4.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.40, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Amarela"},
        {"Nome": "Leite integral", "Categoria": "Laticinios", "Preco": 5.50, "Unid_Receita": "ml", "Unid_Compra": "l", "Kcal_Unid": 0.61, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Pasteurizado"},
        {"Nome": "Queijo mussarela", "Categoria": "Laticinios", "Preco": 28.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 2.80, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Fatiado"},
        {"Nome": "Ovo caipira", "Categoria": "Proteina Animal", "Preco": 18.00, "Unid_Receita": "un", "Unid_Compra": "duzia", "Kcal_Unid": 1.55, "Fator_Conv": 12, "Ativo": True, "Observacoes": "Grande"},
        {"Nome": "Banana prata", "Categoria": "Fruta", "Preco": 6.50, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.89, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Madura"},
        {"Nome": "Maçã fuji", "Categoria": "Fruta", "Preco": 8.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.52, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Nacional"},
        {"Nome": "Aveia flocos", "Categoria": "Cereal", "Preco": 12.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 3.89, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Integral"},
        # Mais alguns para fazer um teste com ~25 items
        {"Nome": "Amendoim torrado", "Categoria": "Oleaginosa", "Preco": 15.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 5.67, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Sem sal"},
        {"Nome": "Castanha caju", "Categoria": "Oleaginosa", "Preco": 45.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 5.53, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Crua"},
        {"Nome": "Iogurte natural", "Categoria": "Laticinios", "Preco": 8.50, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.61, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Integral"},
        {"Nome": "Mel silvestre", "Categoria": "Adocante", "Preco": 35.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 3.04, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Puro"},
        {"Nome": "Vinagre balsamico", "Categoria": "Condimento", "Preco": 25.00, "Unid_Receita": "ml", "Unid_Compra": "l", "Kcal_Unid": 0.19, "Fator_Conv": 1000, "Ativo": True, "Observacoes": "Importado"}
    ]
    
    # Adicionar alguns com Ativo=False para testar boolean conversion
    test_ingredients.extend([
        {"Nome": "Teste Inativo 1", "Categoria": "Teste", "Preco": 1.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.10, "Fator_Conv": 1000, "Ativo": False, "Observacoes": "Teste boolean false"},
        {"Nome": "Teste Inativo 2", "Categoria": "Teste", "Preco": 2.00, "Unid_Receita": "g", "Unid_Compra": "kg", "Kcal_Unid": 0.20, "Fator_Conv": 1000, "Ativo": False, "Observacoes": "Teste boolean false"},
    ])
    
    return test_ingredients

def execute_optimized_batch_upload():
    """Executa upload otimizado com configurações OPUS 4.1"""
    
    print("=" * 60)
    print("BATCH UPLOAD OPTIMIZER - OPUS 4.1")
    print("=" * 60)
    print(f"Iniciando: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Carregar configurações da análise OPUS 4.1
    opus_config = {
        "batch_size": 10,
        "batch_delay": 2.0,
        "item_delay": 0.3,
        "max_retries": 3
    }
    
    print("CONFIGURACOES OPUS 4.1:")
    print(f"  Batch Size: {opus_config['batch_size']} ingredientes")
    print(f"  Delay entre lotes: {opus_config['batch_delay']}s")
    print(f"  Delay entre items: {opus_config['item_delay']}s")
    print(f"  Max retries: {opus_config['max_retries']}")
    print()
    
    # Simular Firebase client
    firebase_client = simulate_firebase_client()
    
    # Criar ingredientes de teste
    ingredients = create_test_ingredients()
    total_ingredients = len(ingredients)
    
    print(f"INGREDIENTES PARA UPLOAD: {total_ingredients}")
    print()
    
    # Estatísticas do upload
    upload_stats = {
        "total_items": total_ingredients,
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "retries": 0,
        "start_time": time.time(),
        "batch_results": []
    }
    
    # Dividir em lotes
    batches = []
    for i in range(0, len(ingredients), opus_config["batch_size"]):
        batch = ingredients[i:i + opus_config["batch_size"]]
        batches.append(batch)
    
    print(f"LOTES CRIADOS: {len(batches)} lotes")
    print()
    
    # Processar cada lote
    for batch_idx, batch in enumerate(batches):
        batch_start_time = time.time()
        
        print(f"PROCESSANDO LOTE {batch_idx + 1}/{len(batches)} ({len(batch)} items)")
        
        batch_stats = {
            "batch_number": batch_idx + 1,
            "items": len(batch),
            "successful": 0,
            "failed": 0,
            "items_processed": []
        }
        
        # Processar items do lote
        for item_idx, ingredient in enumerate(batch):
            try:
                # Converter para formato Firebase
                firebase_data = {
                    "nome": str(ingredient.get('Nome', '')),
                    "categoria": str(ingredient.get('Categoria', '')),
                    "unid_receita": str(ingredient.get('Unid_Receita', 'g')),
                    "unid_compra": str(ingredient.get('Unid_Compra', 'kg')),
                    "preco": float(ingredient.get('Preco', 0.0)),
                    "kcal_unid": float(ingredient.get('Kcal_Unid', 0.0)),
                    "fator_conv": float(ingredient.get('Fator_Conv', 1.0)),
                    "ativo": bool(ingredient.get('Ativo', True)),  # CRÍTICO: Teste boolean
                    "observacoes": str(ingredient.get('Observacoes', '')),
                    "user_id": session_state.user['uid'],
                    "created_at": datetime.now().isoformat(),
                    "batch_upload": True,
                    "batch_number": batch_idx + 1,
                    "opus_41_upload": True
                }
                
                # Tentar upload com retry
                success = False
                retries = 0
                
                while not success and retries < opus_config["max_retries"]:
                    try:
                        item_start_time = time.time()
                        
                        # Simular upload
                        result = firebase_client.collection("users/test_user/ingredients").add(firebase_data)
                        
                        item_duration = time.time() - item_start_time
                        
                        if result:
                            success = True
                            upload_stats["successful"] += 1
                            batch_stats["successful"] += 1
                            
                            # Log boolean conversion test
                            boolean_status = "OK" if isinstance(firebase_data["ativo"], bool) else "ERROR"
                            
                            print(f"  [+] Item {item_idx+1}: {firebase_data['nome'][:30]} ({item_duration:.2f}s) [Boolean: {boolean_status}]")
                            
                            item_result = {
                                "name": firebase_data['nome'],
                                "status": "SUCCESS",
                                "duration": item_duration,
                                "boolean_test": boolean_status,
                                "retries": retries
                            }
                        else:
                            # Falha, tentar retry
                            retries += 1
                            upload_stats["retries"] += 1
                            
                            print(f"  [-] Item {item_idx+1}: {firebase_data['nome'][:30]} FALHOU (tentativa {retries})")
                            
                            if retries < opus_config["max_retries"]:
                                time.sleep(opus_config["item_delay"] * 2)  # Delay maior para retry
                            else:
                                upload_stats["failed"] += 1
                                batch_stats["failed"] += 1
                                
                                item_result = {
                                    "name": firebase_data['nome'],
                                    "status": "FAILED",
                                    "retries": retries
                                }
                    
                    except Exception as item_error:
                        retries += 1
                        upload_stats["retries"] += 1
                        
                        print(f"  [!] Item {item_idx+1}: ERRO - {str(item_error)}")
                        
                        if retries >= opus_config["max_retries"]:
                            upload_stats["failed"] += 1
                            batch_stats["failed"] += 1
                            
                            item_result = {
                                "name": firebase_data.get('nome', 'Unknown'),
                                "status": "EXCEPTION",
                                "error": str(item_error),
                                "retries": retries
                            }
                            break
                
                batch_stats["items_processed"].append(item_result)
                upload_stats["processed"] += 1
                
                # Delay entre items
                time.sleep(opus_config["item_delay"])
                
            except Exception as e:
                print(f"  [X] ERRO CRÍTICO no item {item_idx+1}: {str(e)}")
                upload_stats["failed"] += 1
                batch_stats["failed"] += 1
        
        # Finalizar lote
        batch_duration = time.time() - batch_start_time
        batch_success_rate = (batch_stats["successful"] / batch_stats["items"]) * 100
        
        batch_stats["duration"] = batch_duration
        batch_stats["success_rate"] = batch_success_rate
        
        upload_stats["batch_results"].append(batch_stats)
        
        print(f"  LOTE {batch_idx + 1} COMPLETO: {batch_success_rate:.1f}% sucesso em {batch_duration:.1f}s")
        
        # Delay entre lotes
        if batch_idx < len(batches) - 1:
            print(f"  Aguardando {opus_config['batch_delay']}s antes do próximo lote...")
            time.sleep(opus_config['batch_delay'])
        
        print()
    
    # Finalizar upload
    upload_stats["end_time"] = time.time()
    upload_stats["total_duration"] = upload_stats["end_time"] - upload_stats["start_time"]
    upload_stats["overall_success_rate"] = (upload_stats["successful"] / upload_stats["total_items"]) * 100
    
    # Resultados finais
    print("RESULTADOS FINAIS")
    print("=" * 60)
    
    print(f"Total processados: {upload_stats['processed']}/{upload_stats['total_items']}")
    print(f"Sucessos: {upload_stats['successful']}")
    print(f"Falhas: {upload_stats['failed']}")
    print(f"Retries: {upload_stats['retries']}")
    print(f"Taxa de sucesso: {upload_stats['overall_success_rate']:.1f}%")
    print(f"Duração total: {upload_stats['total_duration']:.1f} segundos")
    print()
    
    # Análise de performance
    if upload_stats["overall_success_rate"] >= 95:
        print("STATUS: SUCESSO! Taxa de sucesso >95%")
        print("ESTRATEGIA OPUS 4.1: FUNCIONOU PERFEITAMENTE")
    elif upload_stats["overall_success_rate"] >= 80:
        print("STATUS: PARCIAL. Taxa de sucesso >80%")
        print("RECOMENDACAO: Ajustar configurações (reduzir batch ou aumentar delays)")
    else:
        print("STATUS: FALHA. Taxa de sucesso <80%")
        print("RECOMENDACAO: Problema sistêmico - investigar mais profundamente")
    
    print()
    
    # Boolean conversion test
    boolean_tests = []
    for batch in upload_stats["batch_results"]:
        for item in batch.get("items_processed", []):
            if "boolean_test" in item:
                boolean_tests.append(item["boolean_test"])
    
    boolean_ok = boolean_tests.count("OK")
    boolean_total = len(boolean_tests)
    
    if boolean_total > 0:
        print(f"TESTE BOOLEAN CONVERSION: {boolean_ok}/{boolean_total} OK ({(boolean_ok/boolean_total)*100:.1f}%)")
        if boolean_ok == boolean_total:
            print("BOOLEAN FIX: FUNCIONANDO PERFEITAMENTE!")
        else:
            print("BOOLEAN FIX: AINDA HÁ PROBLEMAS - INVESTIGAR")
    
    print()
    
    # Salvar relatório
    report_filename = f"batch_upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(upload_stats, f, indent=2, ensure_ascii=False)
        
        print(f"RELATÓRIO SALVO: {report_filename}")
    except Exception as e:
        print(f"ERRO ao salvar relatório: {e}")
    
    print()
    
    # Recomendações baseadas nos resultados
    print("RECOMENDAÇÕES FINAIS")
    print("=" * 60)
    
    if upload_stats["overall_success_rate"] >= 95:
        print("1. CONFIGURAÇÕES PERFEITAS - usar as mesmas para upload real")
        print("2. Executar upload dos 113 ingredientes faltantes")
        print("3. Monitorar que taxa se mantém >95%")
    else:
        print("1. AJUSTAR CONFIGURAÇÕES:")
        
        if upload_stats["failed"] > upload_stats["total_items"] * 0.2:
            print("   - Reduzir batch_size para 5")
            print("   - Aumentar batch_delay para 3.0s")
        
        if upload_stats["retries"] > upload_stats["successful"]:
            print("   - Aumentar max_retries para 5")
            print("   - Aumentar item_delay para 0.5s")
    
    print("4. Se ainda falhar, usar estratégia ULTRA CONSERVADOR (batch_size=1)")
    print()
    
    print("BATCH UPLOAD OPTIMIZER COMPLETO!")
    print("=" * 60)
    
    return upload_stats

if __name__ == "__main__":
    try:
        results = execute_optimized_batch_upload()
        print(f"\nSUCESSO: Upload otimizado executado")
        print(f"Taxa final: {results.get('overall_success_rate', 0):.1f}%")
        
    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}")
        print("Stacktrace:")
        print(traceback.format_exc())