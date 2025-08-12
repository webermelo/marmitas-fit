#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Específico - Conversão de Booleanos
Identifica EXATAMENTE onde está o problema
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.getcwd())

def test_boolean_conversion():
    """Testa especificamente a conversão de booleanos"""
    print("=" * 60)
    print("DEBUG - CONVERSÃO DE BOOLEANOS")
    print("=" * 60)
    
    # Carregar CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    first_row = df.iloc[0]
    
    print(f"1. Dados do CSV (primeira linha):")
    print(f"   Nome: {first_row['Nome']}")
    print(f"   Ativo: '{first_row['Ativo']}' (tipo: {type(first_row['Ativo'])})")
    
    # Testar conversão como admin_safe.py faz
    print(f"\n2. Conversão atual (admin_safe.py linha 631):")
    ativo_converted = str(first_row['Ativo']).upper() == 'TRUE' if pd.notna(first_row['Ativo']) else True
    print(f"   str(row['Ativo']).upper() == 'TRUE': {ativo_converted}")
    print(f"   Tipo final: {type(ativo_converted)}")
    print(f"   isinstance(value, bool): {isinstance(ativo_converted, bool)}")
    print(f"   isinstance(value, int): {isinstance(ativo_converted, int)}")
    
    # Testar com FirestoreClient
    print(f"\n3. Testando FirestoreClient._convert_to_firestore_value:")
    
    from utils.firestore_client import FirestoreClient
    client = FirestoreClient("test")
    
    # Testar diferentes tipos de valores
    test_values = [
        ("string", "teste"),
        ("int", 123),
        ("float", 45.67),
        ("bool_true", True),
        ("bool_false", False),
        ("bool_converted", ativo_converted)
    ]
    
    for name, value in test_values:
        try:
            result = client._convert_to_firestore_value(value)
            print(f"   {name}: {value} ({type(value).__name__}) → {result}")
        except Exception as e:
            print(f"   {name}: ERRO - {e}")
    
    # Testar dados completos como enviados
    print(f"\n4. Testando estrutura completa de dados:")
    
    ingredient_data = {
        'nome': str(first_row['Nome']).strip(),
        'categoria': str(first_row['Categoria']).strip(),
        'preco': float(first_row['Preco']),
        'kcal_unid': float(first_row['Kcal_Unid']),
        'ativo': ativo_converted,  # Boolean convertido
        'user_id': 'test_user',
        'created_at': datetime.now().isoformat()
    }
    
    print(f"   Dados a converter:")
    for key, value in ingredient_data.items():
        print(f"     {key}: {value} ({type(value).__name__})")
    
    # Tentar converter todos os campos
    print(f"\n5. Conversão campo por campo:")
    
    converted_fields = {}
    problematic_fields = []
    
    for key, value in ingredient_data.items():
        try:
            converted = client._convert_to_firestore_value(value)
            converted_fields[key] = converted
            print(f"   ✓ {key}: {converted}")
        except Exception as e:
            problematic_fields.append((key, value, str(e)))
            print(f"   ✗ {key}: ERRO - {e}")
    
    # Resultado
    print(f"\n" + "=" * 60)
    print(f"RESULTADO:")
    print(f"  Campos convertidos com sucesso: {len(converted_fields)}")
    print(f"  Campos problemáticos: {len(problematic_fields)}")
    
    if problematic_fields:
        print(f"\n  PROBLEMAS IDENTIFICADOS:")
        for key, value, error in problematic_fields:
            print(f"    - {key}: valor={value}, tipo={type(value).__name__}, erro={error}")
    
    # Diagnóstico final
    has_bool_problem = any('bool' in str(type(value).__name__).lower() and 'integer' in error 
                          for key, value, error in problematic_fields)
    
    print(f"\n  DIAGNÓSTICO:")
    if has_bool_problem:
        print(f"    ✗ PROBLEMA DE CONVERSÃO BOOLEAN CONFIRMADO")
        print(f"    ✗ Booleanos sendo convertidos para integerValue incorretamente")
    else:
        print(f"    ✓ Conversão de booleanos funcionando corretamente")
    
    return len(problematic_fields) == 0

if __name__ == "__main__":
    test_boolean_conversion()