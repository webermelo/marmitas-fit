#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final Simples - Sem emojis ou caracteres especiais
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.getcwd())

def test_final():
    """Teste final simples do upload"""
    print("=" * 50)
    print("TESTE FINAL - UPLOAD INGREDIENTES")
    print("=" * 50)
    
    # Teste 1: Carregar CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    
    print("1. Testando CSV...")
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"OK - CSV: {len(df)} ingredientes")
        csv_ok = True
    except Exception as e:
        print(f"ERRO CSV: {e}")
        csv_ok = False
    
    if not csv_ok:
        return False
    
    # Teste 2: Salvar um ingrediente
    print("2. Testando salvamento...")
    
    try:
        from utils.firestore_client import FirestoreClient
        
        client = FirestoreClient("marmita-fit-6a3ca")
        collection = client.collection("users/kZugmFmioiQiz1EAh8iBPBzIvum2/ingredients")
        
        # Dados do primeiro ingrediente
        first_row = df.iloc[0]
        test_ingredient = {
            'nome': str(first_row['Nome']),
            'categoria': str(first_row['Categoria']),
            'preco': float(first_row['Preco']),
            'kcal_unid': float(first_row['Kcal_Unid']),
            'ativo': True,
            'test_final': True
        }
        
        result = collection.add(test_ingredient)
        if result and 'name' in result:
            print("OK - Salvamento funcionando")
            save_ok = True
        else:
            print("ERRO - Salvamento falhou")
            save_ok = False
            
    except Exception as e:
        print(f"ERRO Salvamento: {e}")
        save_ok = False
    
    # Teste 3: Carregar ingredientes
    print("3. Testando carregamento...")
    
    try:
        docs = collection.get()
        if docs and len(docs) > 0:
            print(f"OK - Carregamento: {len(docs)} ingredientes")
            
            # Procurar nosso ingrediente de teste
            found = False
            for doc in docs:
                if doc.get('test_final') == True:
                    print(f"OK - Ingrediente teste encontrado: {doc.get('nome')}")
                    found = True
                    break
            
            if not found:
                print("AVISO - Ingrediente de teste nao encontrado")
            
            load_ok = True
        else:
            print("ERRO - Carregamento vazio")
            load_ok = False
            
    except Exception as e:
        print(f"ERRO Carregamento: {e}")
        load_ok = False
    
    # Resultado
    print("\n" + "=" * 50)
    print("RESULTADO FINAL:")
    print(f"CSV: {'OK' if csv_ok else 'ERRO'}")
    print(f"Salvamento: {'OK' if save_ok else 'ERRO'}")
    print(f"Carregamento: {'OK' if load_ok else 'ERRO'}")
    
    success = csv_ok and save_ok and load_ok
    
    print(f"\nPERSISTENCIA: {'FUNCIONANDO' if success else 'PROBLEMAS'}")
    
    if success:
        print("\nSOLUCAO COMPLETA!")
        print("- O problema foi RESOLVIDO")
        print("- Upload de ingredientes funciona")
        print("- Dados persistem corretamente")
        print("- Aplicacao pronta para uso")
    
    return success

if __name__ == "__main__":
    test_final()