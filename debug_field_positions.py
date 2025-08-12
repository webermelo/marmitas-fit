#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Específico - Identificar campos 7 e 16 que estão causando erro
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.getcwd())

def debug_field_positions():
    """Debug para identificar exatamente quais campos são 7 e 16"""
    print("=" * 60)
    print("DEBUG - IDENTIFICAR CAMPOS 7 E 16")
    print("=" * 60)
    
    # Carregar CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    first_row = df.iloc[0]
    
    print(f"1. Dados originais do CSV:")
    for i, (key, value) in enumerate(first_row.items()):
        print(f"   Campo {i}: {key} = '{value}' ({type(value).__name__})")
    
    # Simular EXATAMENTE como admin_safe.py processa (linhas 582-632)
    print(f"\n2. Processamento admin_safe.py:")
    
    nome = str(first_row['Nome']).strip() if pd.notna(first_row['Nome']) else ''
    categoria = str(first_row['Categoria']).strip() if pd.notna(first_row['Categoria']) else ''
    
    try:
        preco = float(first_row['Preco']) if pd.notna(first_row['Preco']) else 0.0
    except:
        preco = 0.0
    
    try:
        kcal_unid = float(first_row['Kcal_Unid']) if pd.notna(first_row['Kcal_Unid']) else 0.0
    except:
        kcal_unid = 0.0
    
    try:
        fator_conv = float(first_row['Fator_Conv']) if pd.notna(first_row['Fator_Conv']) else 1.0
    except:
        fator_conv = 1.0
    
    # ESTRUTURA EXATA como admin_safe cria (linhas 611-632)
    ingredient_data_compatible = {
        # Estrutura ANTIGA que o app espera
        'Nome': nome,
        'Categoria': categoria,
        'Unidade_Receita': str(first_row['Unid_Receita']).strip() if pd.notna(first_row['Unid_Receita']) else 'g',
        'Unidade_Compra': str(first_row['Unid_Compra']).strip() if pd.notna(first_row['Unid_Compra']) else 'kg',
        'Preco_Padrao': preco,
        'Kcal_Por_Unidade_Receita': kcal_unid,
        'Fator_Conversao': fator_conv,
        'Ativo': str(first_row['Ativo']).upper() == 'TRUE' if pd.notna(first_row['Ativo']) else True,
        'Observacoes': str(first_row.get('Observacoes', '')),
        
        # Estrutura NOVA para Firebase (minúscula)
        'nome': nome,
        'categoria': categoria,
        'unid_receita': str(first_row['Unid_Receita']).strip() if pd.notna(first_row['Unid_Receita']) else 'g',
        'unid_compra': str(first_row['Unid_Compra']).strip() if pd.notna(first_row['Unid_Compra']) else 'kg',
        'preco': preco,
        'kcal_unid': kcal_unid,
        'fator_conv': fator_conv,
        'ativo': str(first_row['Ativo']).upper() == 'TRUE' if pd.notna(first_row['Ativo']) else True,
        'observacoes': str(first_row.get('Observacoes', '')),
        'user_id': 'test_user'
    }
    
    print(f"\n3. Estrutura final (como enviada para Firebase):")
    for i, (key, value) in enumerate(ingredient_data_compatible.items()):
        tipo = type(value).__name__
        print(f"   Campo {i}: '{key}' = {value} ({tipo})")
        
        # Identificar campos problemáticos
        if i in [7, 16]:
            print(f"      ^^^ ESTE É O CAMPO {i} DO ERRO! ^^^")
            if isinstance(value, bool):
                print(f"      Tipo bool correto, mas pode estar sendo convertido errado")
    
    print(f"\n4. Análise dos campos problemáticos:")
    
    # Campo 7 (contando do 0)
    field_7_key = list(ingredient_data_compatible.keys())[7]
    field_7_value = ingredient_data_compatible[field_7_key]
    print(f"   Campo 7: '{field_7_key}' = {field_7_value} ({type(field_7_value).__name__})")
    
    # Campo 16 (contando do 0)  
    field_16_key = list(ingredient_data_compatible.keys())[16]
    field_16_value = ingredient_data_compatible[field_16_key]
    print(f"   Campo 16: '{field_16_key}' = {field_16_value} ({type(field_16_value).__name__})")
    
    # Verificar se ambos são booleanos
    if isinstance(field_7_value, bool) and isinstance(field_16_value, bool):
        print(f"\n   CONFIRMADO: Ambos os campos são booleanos!")
        print(f"   - Campo 7 ('{field_7_key}'): {field_7_value}")
        print(f"   - Campo 16 ('{field_16_key}'): {field_16_value}")
        print(f"   - Erro indica que estão sendo convertidos para integerValue")
        print(f"   - Nossa correção no FirestoreClient deveria resolver isso")
    
    print(f"\n5. Teste da conversão com nossa correção:")
    
    from utils.firestore_client import FirestoreClient
    client = FirestoreClient("test")
    
    print(f"   Testando campo 7 ('{field_7_key}'):")
    result_7 = client._convert_to_firestore_value(field_7_value)
    print(f"     {field_7_value} -> {result_7}")
    
    print(f"   Testando campo 16 ('{field_16_key}'):")
    result_16 = client._convert_to_firestore_value(field_16_value)
    print(f"     {field_16_value} -> {result_16}")
    
    # Verificar se a conversão está correta
    if result_7.get('booleanValue') is not None and result_16.get('booleanValue') is not None:
        print(f"\n   CORREÇÃO FUNCIONANDO: Ambos convertidos para booleanValue")
    else:
        print(f"\n   PROBLEMA: Conversão ainda incorreta")
        if 'integerValue' in result_7:
            print(f"     Campo 7 ainda vira integerValue!")
        if 'integerValue' in result_16:
            print(f"     Campo 16 ainda vira integerValue!")

if __name__ == "__main__":
    debug_field_positions()