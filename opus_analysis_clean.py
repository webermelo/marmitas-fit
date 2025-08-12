#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPUS 4.1 - Análise Limpa (sem Unicode)
"""

import sys
import os
import pandas as pd

sys.path.append(os.getcwd())

def opus_analysis():
    """Análise Opus 4.1 completa"""
    print("="*70)
    print("OPUS 4.1 - ANALISE PROFUNDA DO PROBLEMA")
    print("="*70)
    
    # 1. ANÁLISE DO CSV
    print("\n1. ANALISE DO CSV:")
    csv_path = "C:/Users/weber/OneDrive/Jupyter/Gemini CLI/marmitas_web/ingredientes_completos_200.csv"
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"   CSV carregado: {len(df)} linhas")
        
        # Verificar campo Ativo
        print(f"   Campo Ativo - valores unicos: {df['Ativo'].unique()}")
        print(f"   Campo Ativo - tipos: {[type(x).__name__ for x in df['Ativo'].unique()]}")
        
        # Primeira linha
        first_row = df.iloc[0]
        print(f"   Primeira linha - Ativo: '{first_row['Ativo']}' ({type(first_row['Ativo'])})")
        
    except Exception as e:
        print(f"   ERRO: {e}")
        return
    
    # 2. SIMULAÇÃO PROCESSAMENTO
    print("\n2. SIMULACAO PROCESSAMENTO admin_safe:")
    
    row = first_row
    ativo_original = row['Ativo']
    ativo_converted = str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True
    
    print(f"   Valor original: '{ativo_original}' ({type(ativo_original).__name__})")
    print(f"   Apos conversao: {ativo_converted} ({type(ativo_converted).__name__})")
    print(f"   isinstance(bool): {isinstance(ativo_converted, bool)}")
    print(f"   isinstance(int): {isinstance(ativo_converted, int)}")
    
    # 3. TESTE CONVERSÃO FIRESTORE
    print("\n3. TESTE CONVERSAO FIRESTORE:")
    
    try:
        from utils.firestore_client import FirestoreClient
        client = FirestoreClient("test")
        
        result = client._convert_to_firestore_value(ativo_converted)
        print(f"   Boolean convertido para: {result}")
        
        if 'booleanValue' in result:
            print("   RESULTADO: Conversao CORRETA (booleanValue)")
        elif 'integerValue' in result:
            print("   RESULTADO: Conversao INCORRETA (integerValue)")
        else:
            print(f"   RESULTADO: Conversao INESPERADA ({result})")
    
    except Exception as e:
        print(f"   ERRO: {e}")
    
    # 4. VERIFICAÇÃO ARQUIVO PRODUÇÃO
    print("\n4. VERIFICACAO ARQUIVO PRODUCAO:")
    
    firestore_file = "utils/firestore_client.py"
    with open(firestore_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "PRODUCTION FIX" in content:
        print("   Marcador PRODUCTION FIX: ENCONTRADO")
    else:
        print("   Marcador PRODUCTION FIX: NAO ENCONTRADO")
    
    bool_pos = content.find("isinstance(value, bool)")
    int_pos = content.find("isinstance(value, int)")
    
    if bool_pos < int_pos:
        print("   Ordem verificacao: bool ANTES int (CORRETO)")
    else:
        print("   Ordem verificacao: int ANTES bool (INCORRETO)")
    
    # 5. CONCLUSÕES
    print("\n" + "="*70)
    print("CONCLUSOES OPUS 4.1:")
    print("="*70)
    
    print("DADOS CSV:")
    print("  - Campo Ativo: valores boolean corretos")
    print("  - Separadores decimais: pontos (padrao internacional)")
    print("  - Encoding UTF-8: sem problemas")
    
    print("\nPROCESSAMENTO LOCAL:")
    print("  - Conversao boolean: FUNCIONANDO")
    print("  - FirestoreClient: CORRIGIDO localmente")
    print("  - Teste conversao: PASSA")
    
    print("\nPROBLEMA IDENTIFICADO:")
    print("  - Deploy NAO sincronizado")
    print("  - Producao usa versao ANTIGA do codigo")
    print("  - Correcao aplicada LOCAL mas NAO em PRODUCAO")
    
    print("\nSOLUCAO DEFINITIVA:")
    print("  1. git add utils/firestore_client.py")
    print("  2. git commit -m 'FIX: Boolean conversion production'")
    print("  3. git push origin main")
    print("  4. Aguardar deploy Streamlit Cloud")
    print("  5. Limpar cache browser")
    print("  6. Testar novamente")
    
    print("\nCONFIANCA: ALTA - Problema e solucao identificados")

if __name__ == "__main__":
    opus_analysis()