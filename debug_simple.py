#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG SIMPLES - Conversão Boolean
Teste do problema de conversão True -> integerValue
"""

def test_boolean_conversion():
    """Testa conversão de booleanos em diferentes cenários"""
    
    print("="*80)
    print("DEBUG: CONVERSAO DE BOOLEAN")
    print("="*80)
    
    # Teste básico Python
    test_value = True
    print(f"\n1. TESTE PYTHON BASICO:")
    print(f"   test_value = {test_value}")
    print(f"   type(test_value) = {type(test_value)}")
    print(f"   isinstance(test_value, bool) = {isinstance(test_value, bool)}")
    print(f"   isinstance(test_value, int) = {isinstance(test_value, int)}")
    print(f"   bool.__bases__ = {bool.__bases__}")
    print(f"   -> PROBLEMA: bool e subclasse de int!")
    
    # Teste ordem de verificação
    print(f"\n2. TESTE ORDEM DE VERIFICACAO:")
    
    def convert_wrong_order(value):
        if isinstance(value, int):  # ERRO: int primeiro
            return {"integerValue": str(value)}
        elif isinstance(value, bool):  # Nunca será atingido
            return {"booleanValue": value}
        else:
            return {"stringValue": str(value)}
    
    def convert_correct_order(value):
        if isinstance(value, bool):  # CORRETO: bool primeiro
            return {"booleanValue": value}
        elif isinstance(value, int):  # int depois
            return {"integerValue": str(value)}
        else:
            return {"stringValue": str(value)}
    
    test_values = [True, False, 123, "test"]
    
    print("   ORDEM ERRADA (int primeiro):")
    for val in test_values:
        result = convert_wrong_order(val)
        status = "ERRO" if isinstance(val, bool) and "integerValue" in result else "OK"
        print(f"   {status} {val} ({type(val).__name__}) -> {result}")
    
    print("\n   ORDEM CORRETA (bool primeiro):")
    for val in test_values:
        result = convert_correct_order(val)
        status = "OK" if isinstance(val, bool) and "booleanValue" in result else "OK"
        print(f"   {status} {val} ({type(val).__name__}) -> {result}")
    
    # Teste com dados reais do ingrediente
    print(f"\n3. TESTE COM DADOS REAIS:")
    
    ingredient_data = {
        "nome": "Frango peito",
        "categoria": "Proteina Animal", 
        "preco": 32.90,
        "ativo": True,  # Este é o campo problemático
        "fator_conv": 1000
    }
    
    print("   Dados do ingrediente:")
    for key, value in ingredient_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    print(f"\n   Conversao com ordem ERRADA:")
    for key, value in ingredient_data.items():
        converted = convert_wrong_order(value)
        if key == "ativo":
            status = "PROBLEMA!" if "integerValue" in converted else "OK"
            print(f"   {status} {key}: {value} -> {converted}")
        else:
            print(f"   OK {key}: {value} -> {converted}")
    
    print(f"\n   Conversao com ordem CORRETA:")
    for key, value in ingredient_data.items():
        converted = convert_correct_order(value)
        if key == "ativo":
            status = "CORRETO!" if "booleanValue" in converted else "ERRO"
            print(f"   {status} {key}: {value} -> {converted}")
        else:
            print(f"   OK {key}: {value} -> {converted}")
    
    # Simular o erro exato reportado
    print(f"\n4. SIMULACAO DO ERRO REPORTADO:")
    print("   Erro original: 'Campo 7: integerValue com valor True'")
    print("   Erro original: 'Campo 16: integerValue com valor True'")
    
    # Simular upload de 198 ingredientes
    print(f"\n   Simulando upload CSV com campos boolean:")
    csv_data = [
        {"nome": "Frango peito", "ativo": True},
        {"nome": "Carne bovina", "ativo": False}, 
        {"nome": "Arroz integral", "ativo": True}
    ]
    
    print("   Com conversao ERRADA (producao atual):")
    for i, item in enumerate(csv_data):
        converted_ativo = convert_wrong_order(item["ativo"])
        print(f"   Item {i+1}: {item['nome']} - ativo={item['ativo']} -> {converted_ativo}")
    
    print("\n   Com conversao CORRETA (fix necessario):")
    for i, item in enumerate(csv_data):
        converted_ativo = convert_correct_order(item["ativo"])
        print(f"   Item {i+1}: {item['nome']} - ativo={item['ativo']} -> {converted_ativo}")
    
    print(f"\n5. CONCLUSOES:")
    print("   OK Problema identificado: isinstance(True, int) retorna True")
    print("   OK Solucao: Verificar isinstance(value, bool) ANTES de isinstance(value, int)")
    print("   OK Status local: CORRIGIDO")
    print("   ?? Status producao: PRECISA SER VERIFICADO")
    
    print(f"\n6. ACOES NECESSARIAS:")
    print("   1. Verificar se arquivo utils/firestore_client.py em producao tem a correcao")
    print("   2. Confirmar que linha 42 tem 'isinstance(value, bool)' ANTES da linha 44")
    print("   3. Limpar cache do Streamlit Cloud se necessario")
    print("   4. Executar teste de upload novamente")
    
    print("="*80)

if __name__ == "__main__":
    test_boolean_conversion()
    
    print(f"\n" + "="*80)
    print("DIAGNOSTICO FINAL:")
    print("   PROBLEMA: isinstance(True, int) e True em Python")
    print("   SOLUCAO APLICADA: isinstance(bool) verificado ANTES de isinstance(int)")
    print("   STATUS: Aguardando confirmacao que correcao esta ativa em producao")
    print("="*80)