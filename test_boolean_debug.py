# -*- coding: utf-8 -*-
"""
Teste específico para debug do problema de conversão de booleanos
"""

import pandas as pd
from datetime import datetime

def test_boolean_conversion():
    """Testa se booleanos estão sendo convertidos corretamente"""
    
    print("TESTE DE CONVERSAO DE BOOLEANOS")
    print("=" * 50)
    
    # Simular dados CSV como seriam processados
    csv_data = """Nome,Categoria,Preco,Unid_Receita,Unid_Compra,Kcal_Unid,Fator_Conv,Ativo,Observacoes
Frango peito,Proteina Animal,18.90,g,kg,1.65,1000,TRUE,Sem pele congelado
Arroz integral,Carboidrato,8.90,g,kg,1.11,1000,FALSE,Grao longo tipo 1"""
    
    # Processar dados como pandas faria
    from io import StringIO
    df = pd.read_csv(StringIO(csv_data))
    
    print("DataFrame carregado:")
    print(df.dtypes)
    print("\n")
    
    for idx, row in df.iterrows():
        print(f"LINHA {idx + 1}:")
        
        # Processar como o código atual faz
        nome = str(row['Nome']).strip() if pd.notna(row['Nome']) else ''
        categoria = str(row['Categoria']).strip() if pd.notna(row['Categoria']) else ''
        
        # Conversões numéricas
        try:
            preco = float(row['Preco']) if pd.notna(row['Preco']) else 0.0
        except:
            preco = 0.0
        
        try:
            kcal_unid = float(row['Kcal_Unid']) if pd.notna(row['Kcal_Unid']) else 0.0
        except:
            kcal_unid = 0.0
        
        try:
            fator_conv = float(row['Fator_Conv']) if pd.notna(row['Fator_Conv']) else 1.0
        except:
            fator_conv = 1.0
        
        # A CONVERSÃO CRÍTICA DO BOOLEANO
        ativo_raw = row['Ativo']
        print(f"   ativo_raw = {repr(ativo_raw)} (tipo: {type(ativo_raw).__name__})")
        
        ativo_str = str(row['Ativo']).upper()
        print(f"   ativo_str = {repr(ativo_str)} (tipo: {type(ativo_str).__name__})")
        
        ativo_bool = str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True
        print(f"   ativo_bool = {repr(ativo_bool)} (tipo: {type(ativo_bool).__name__})")
        print(f"   isinstance(ativo_bool, bool) = {isinstance(ativo_bool, bool)}")
        
        # Estrutura final que seria enviada
        ingredient_data = {
            'Nome': nome,
            'Categoria': categoria,
            'Unidade_Receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
            'Unidade_Compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
            'Preco_Padrao': preco,
            'Kcal_Por_Unidade_Receita': kcal_unid,
            'Fator_Conversao': fator_conv,
            'Ativo': ativo_bool,  # CAMPO CRÍTICO 1
            'Observacoes': str(row.get('Observacoes', '')).strip() if pd.notna(row.get('Observacoes', '')) else '',
            
            # Estrutura duplicada (como no código atual)
            'nome': nome,
            'categoria': categoria,
            'unid_receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
            'unid_compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
            'preco': preco,
            'kcal_unid': kcal_unid,
            'fator_conv': fator_conv,
            'ativo': ativo_bool,  # CAMPO CRÍTICO 2
            'observacoes': str(row.get('Observacoes', '')).strip() if pd.notna(row.get('Observacoes', '')) else ''
        }
        
        # Adicionar campos de sistema
        ingredient_data['user_id'] = "test_user_123"
        ingredient_data['created_at'] = datetime.now().isoformat()
        
        print(f"\n📦 DADOS FINAIS:")
        for key, value in ingredient_data.items():
            if isinstance(value, bool):
                print(f"   ✅ {key}: {repr(value)} (bool)")
            else:
                print(f"   📄 {key}: {repr(value)} ({type(value).__name__})")
        
        print(f"\n🔥 TESTE DE CONVERSÃO FIRESTORE:")
        test_firestore_conversion(ingredient_data)
        
        print("\n" + "-" * 50 + "\n")

def test_firestore_conversion(data):
    """Testa a conversão Firestore sem fazer requisição real"""
    
    # Simular conversão como no firestore_client.py
    fields = {}
    field_count = 0
    
    for key, value in data.items():
        field_count += 1
        
        print(f"   Campo {field_count:2d}: {key} = {repr(value)} ({type(value).__name__})")
        
        if isinstance(value, str):
            result = {"stringValue": value}
            print(f"           -> stringValue: {value}")
        elif isinstance(value, bool):  # DEVE VIR ANTES de int
            result = {"booleanValue": value}
            print(f"           -> ✅ booleanValue: {value}")
        elif isinstance(value, int):
            result = {"integerValue": str(value)}
            print(f"           -> integerValue: {str(value)}")
            if key in ['ativo', 'Ativo'] and value in [0, 1]:
                print(f"           -> 🚨 SUSPEITO! Campo boolean como int!")
        elif isinstance(value, float):
            result = {"doubleValue": value}
            print(f"           -> doubleValue: {value}")
        else:
            result = {"stringValue": str(value)}
            print(f"           -> stringValue (fallback): {str(value)}")
        
        fields[key] = result
        
        # Verificar se este é um dos campos problemáticos mencionados no erro
        if field_count in [7, 16]:
            print(f"           -> 🎯 CAMPO {field_count} (mencionado no erro!)")
            if key in ['ativo', 'Ativo']:
                if not isinstance(value, bool):
                    print(f"           -> 🚨 PROBLEMA ENCONTRADO! Campo boolean como {type(value).__name__}!")

if __name__ == "__main__":
    test_boolean_conversion()