#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples - Problemas de Boolean (sem caracteres especiais)
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.getcwd())

def test_boolean():
    """Testa conversão de booleanos"""
    print("=" * 50)
    print("TESTE - BOOLEAN CONVERSION")
    print("=" * 50)
    
    # Dados do CSV
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    df = pd.read_csv(csv_path, encoding='utf-8')
    first_row = df.iloc[0]
    
    print(f"1. CSV - Campo 'Ativo':")
    print(f"   Valor: '{first_row['Ativo']}'")
    print(f"   Tipo: {type(first_row['Ativo'])}")
    
    # Conversão como admin_safe faz
    ativo_converted = str(first_row['Ativo']).upper() == 'TRUE' if pd.notna(first_row['Ativo']) else True
    print(f"\n2. Conversao admin_safe:")
    print(f"   Resultado: {ativo_converted}")
    print(f"   Tipo: {type(ativo_converted)}")
    print(f"   isinstance(bool): {isinstance(ativo_converted, bool)}")
    print(f"   isinstance(int): {isinstance(ativo_converted, int)}")
    
    # PROBLEMA IDENTIFICADO: bool é subclasse de int
    print(f"\n3. PROBLEMA IDENTIFICADO:")
    print(f"   Em Python: isinstance(True, int) = {isinstance(True, int)}")
    print(f"   bool eh subclasse de int!")
    
    # Testar FirestoreClient
    from utils.firestore_client import FirestoreClient
    client = FirestoreClient("test")
    
    print(f"\n4. Teste FirestoreClient:")
    
    # Teste com True
    try:
        result_true = client._convert_to_firestore_value(True)
        print(f"   True convertido para: {result_true}")
    except Exception as e:
        print(f"   Erro com True: {e}")
    
    # Teste com False  
    try:
        result_false = client._convert_to_firestore_value(False)
        print(f"   False convertido para: {result_false}")
    except Exception as e:
        print(f"   Erro com False: {e}")
    
    # Testar ordem da verificação
    print(f"\n5. Testando ordem de verificacao:")
    
    value = True
    if isinstance(value, str):
        print(f"   True eh string: NAO")
    elif isinstance(value, bool):
        print(f"   True eh bool: SIM - deve usar booleanValue")
    elif isinstance(value, int):
        print(f"   True eh int: ESTE NAO DEVERIA EXECUTAR")
    
    # Verificar se nossa correção está funcionando
    print(f"\n6. Verificando corracao no FirestoreClient:")
    
    # Ler o código atual
    try:
        with open("utils/firestore_client.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Procurar pela ordem das verificações
        if "isinstance(value, bool)" in content and "isinstance(value, int)" in content:
            bool_pos = content.find("isinstance(value, bool)")
            int_pos = content.find("isinstance(value, int)")
            
            if bool_pos < int_pos:
                print(f"   OK - bool vem antes de int no codigo")
            else:
                print(f"   PROBLEMA - int vem antes de bool!")
        else:
            print(f"   Nao encontrou as verificacoes no codigo")
            
    except Exception as e:
        print(f"   Erro ao verificar codigo: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"DIAGNOSTICO:")
    print(f"  - O problema eh que bool eh subclasse de int em Python")
    print(f"  - isinstance(True, int) retorna True")
    print(f"  - Precisamos verificar bool ANTES de int")
    print(f"  - Nossa correcao ja foi aplicada no codigo")

if __name__ == "__main__":
    test_boolean()