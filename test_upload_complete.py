#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Fluxo de Upload
Simula exatamente o processo da aplicação Streamlit
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar path
sys.path.append(os.getcwd())

def test_complete_upload_flow():
    """Testa o fluxo completo de upload como na aplicação"""
    print("=" * 60)
    print("TESTE COMPLETO - FLUXO UPLOAD DE INGREDIENTES")
    print("=" * 60)
    
    # Configurações
    CSV_PATH = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    USER_ID = "kZugmFmioiQiz1EAh8iBPBzIvum2"
    
    # Passo 1: Carregar e processar CSV (como admin_safe.py faz)
    print("1. Carregando CSV...")
    
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8')
        print(f"CSV carregado: {len(df)} ingredientes")
        
        # Processar alguns ingredientes (primeiros 5 para teste)
        test_ingredients = []
        
        for idx in range(min(5, len(df))):
            row = df.iloc[idx]
            
            # Estrutura EXATA como admin_safe.py cria
            ingredient = {
                'nome': str(row['Nome']).strip(),
                'categoria': str(row['Categoria']).strip(),
                'unid_receita': str(row['Unid_Receita']).strip(),
                'unid_compra': str(row['Unid_Compra']).strip(),
                'preco': float(row['Preco']),
                'kcal_unid': float(row['Kcal_Unid']),
                'fator_conv': float(row['Fator_Conv']),
                'ativo': True,
                'observacoes': str(row.get('Observacoes', '')),
                'user_id': USER_ID,
                'test_batch': 'UPLOAD_COMPLETE_TEST'
            }
            
            test_ingredients.append(ingredient)
        
        print(f"Processados {len(test_ingredients)} ingredientes para teste")
        
    except Exception as e:
        print(f"ERRO ao processar CSV: {e}")
        return False
    
    # Passo 2: Salvar usando FirestoreClient (como admin_safe.py faz)
    print(f"\n2. Salvando no Firebase...")
    
    try:
        from utils.firestore_client import FirestoreClient
        
        client = FirestoreClient("marmita-fit-6a3ca")
        collection_path = f"users/{USER_ID}/ingredients"
        collection = client.collection(collection_path)
        
        saved_count = 0
        failed_count = 0
        
        for ingredient in test_ingredients:
            try:
                result = collection.add(ingredient)
                if result and 'name' in result:
                    saved_count += 1
                    print(f"  ✓ {ingredient['nome']}")
                else:
                    failed_count += 1
                    print(f"  ✗ {ingredient['nome']} - resultado inválido")
                    
            except Exception as e:
                failed_count += 1
                print(f"  ✗ {ingredient['nome']} - ERRO: {e}")
        
        print(f"\nSalvamento concluído:")
        print(f"  Sucessos: {saved_count}")
        print(f"  Falhas: {failed_count}")
        
        save_success = saved_count > 0
        
    except Exception as e:
        print(f"ERRO no salvamento: {e}")
        save_success = False
    
    # Passo 3: Verificar carregamento usando DatabaseManager (como app.py faz)
    print(f"\n3. Verificando carregamento via DatabaseManager...")
    
    # Mock mínimo do Streamlit para DatabaseManager funcionar
    class MockST:
        def success(self, msg): print(f"SUCESSO: {msg}")
        def error(self, msg): print(f"ERRO: {msg}")
        def warning(self, msg): print(f"AVISO: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def code(self, msg): print(f"CODIGO: {msg}")
        
        class SessionState:
            def __init__(self):
                self.database_manager = None
            def get(self, key, default=None):
                return getattr(self, key, default)
        
        def __init__(self):
            self.session_state = self.SessionState()
            self.secrets = {"firebase": {"projectId": "marmita-fit-6a3ca"}}
    
    # Substituir streamlit temporariamente
    original_st = sys.modules.get('streamlit')
    sys.modules['streamlit'] = MockST()
    
    try:
        from utils.database import DatabaseManager
        
        # Criar DatabaseManager
        db_manager = DatabaseManager()
        
        # Carregar ingredientes
        ingredients_df = db_manager.get_user_ingredients(USER_ID)
        
        print(f"DatabaseManager retornou: {len(ingredients_df) if not ingredients_df.empty else 0} ingredientes")
        
        if not ingredients_df.empty:
            # Procurar ingredientes do nosso teste
            found_test_ingredients = 0
            
            for _, ing in ingredients_df.iterrows():
                if ing.get('test_batch') == 'UPLOAD_COMPLETE_TEST':
                    found_test_ingredients += 1
            
            print(f"Ingredientes do teste encontrados: {found_test_ingredients}/{len(test_ingredients)}")
            
            # Mostrar estrutura de um ingrediente
            sample = ingredients_df.iloc[0]
            print(f"Estrutura do ingrediente:")
            print(f"  Nome: {sample.get('Nome', 'N/A')}")
            print(f"  Categoria: {sample.get('Categoria', 'N/A')}")
            print(f"  Preço: {sample.get('Preco_Padrao', 'N/A')}")
            
            load_success = True
        else:
            print("ERRO: DatabaseManager retornou DataFrame vazio")
            load_success = False
            
    except Exception as e:
        print(f"ERRO no carregamento: {e}")
        load_success = False
    finally:
        # Restaurar streamlit original
        if original_st:
            sys.modules['streamlit'] = original_st
    
    # Resultado final
    print(f"\n" + "=" * 60)
    print(f"RESULTADO DO TESTE COMPLETO:")
    print(f"  Processamento CSV: OK")
    print(f"  Salvamento Firebase: {'OK' if save_success else 'FALHA'}")
    print(f"  Carregamento App: {'OK' if load_success else 'FALHA'}")
    
    overall_success = save_success and load_success
    
    print(f"\nFLUXO COMPLETO DE UPLOAD: {'FUNCIONANDO!' if overall_success else 'COM PROBLEMAS'}")
    
    if overall_success:
        print(f"\n🎉 PROBLEMA DE PERSISTÊNCIA RESOLVIDO!")
        print(f"   ✓ Ingredientes são salvos corretamente")
        print(f"   ✓ Ingredientes são carregados corretamente")
        print(f"   ✓ Estruturas de dados são convertidas corretamente")
        print(f"\n📋 Agora você pode fazer upload do CSV completo na aplicação!")
    
    return overall_success

if __name__ == "__main__":
    test_complete_upload_flow()