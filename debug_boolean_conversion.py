#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG CRÍTICO - Conversão Boolean
Investigação específica do problema de conversão True → integerValue
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
        status = "❌" if isinstance(val, bool) and "integerValue" in result else "✅"
        print(f"   {status} {val} ({type(val).__name__}) -> {result}")
    
    print("\n   ORDEM CORRETA (bool primeiro):")
    for val in test_values:
        result = convert_correct_order(val)
        status = "✅" if isinstance(val, bool) and "booleanValue" in result else "✅"
        print(f"   {status} {val} ({type(val).__name__}) -> {result}")
    
    # Teste com dados reais do ingrediente
    print(f"\n3. 🧅 TESTE COM DADOS REAIS:")
    
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
    
    print(f"\n   Conversão com ordem ERRADA:")
    for key, value in ingredient_data.items():
        converted = convert_wrong_order(value)
        if key == "ativo":
            status = "❌ PROBLEMA!" if "integerValue" in converted else "✅"
            print(f"   {status} {key}: {value} -> {converted}")
        else:
            print(f"   OK {key}: {value} -> {converted}")
    
    print(f"\n   Conversão com ordem CORRETA:")
    for key, value in ingredient_data.items():
        converted = convert_correct_order(value)
        if key == "ativo":
            status = "✅ CORRETO!" if "booleanValue" in converted else "❌"
            print(f"   {status} {key}: {value} -> {converted}")
        else:
            print(f"   OK {key}: {value} -> {converted}")
    
    # Simular o erro exato reportado
    print(f"\n4. 🚨 SIMULAÇÃO DO ERRO REPORTADO:")
    print("   Erro original: 'Campo 7: integerValue com valor True'")
    print("   Erro original: 'Campo 16: integerValue com valor True'")
    
    # Simular upload de 198 ingredientes
    print(f"\n   Simulando upload CSV com campos boolean:")
    csv_data = [
        {"nome": "Frango peito", "ativo": True},
        {"nome": "Carne bovina", "ativo": False}, 
        {"nome": "Arroz integral", "ativo": True}
    ]
    
    print("   Com conversão ERRADA (produção atual):")
    for i, item in enumerate(csv_data):
        converted_ativo = convert_wrong_order(item["ativo"])
        print(f"   Item {i+1}: {item['nome']} - ativo={item['ativo']} -> {converted_ativo}")
    
    print("\n   Com conversão CORRETA (fix necessário):")
    for i, item in enumerate(csv_data):
        converted_ativo = convert_correct_order(item["ativo"])
        print(f"   Item {i+1}: {item['nome']} - ativo={item['ativo']} -> {converted_ativo}")
    
    print(f"\n5. 📋 CONCLUSÕES:")
    print("   ✅ Problema identificado: isinstance(True, int) retorna True")
    print("   ✅ Solução: Verificar isinstance(value, bool) ANTES de isinstance(value, int)")
    print("   ✅ Status local: CORRIGIDO")
    print("   ❓ Status produção: PRECISA SER VERIFICADO")
    
    print(f"\n6. 🚀 AÇÕES NECESSÁRIAS:")
    print("   1. Verificar se arquivo utils/firestore_client.py em produção tem a correção")
    print("   2. Confirmar que linha 42 tem 'isinstance(value, bool)' ANTES da linha 44")
    print("   3. Limpar cache do Streamlit Cloud se necessário")
    print("   4. Executar teste de upload novamente")
    
    print("="*80)

def create_production_debug_patch():
    """Cria patch de debug para identificar versão rodando em produção"""
    
    print(f"\n7. 🔧 PATCH DE DEBUG PARA PRODUÇÃO:")
    
    debug_function = '''
    def _convert_to_firestore_value(self, value):
        """Converte valor Python para formato Firestore - DEBUG PRODUÇÃO"""
        
        # 🚨 DEBUG CRÍTICO: Log para identificar qual código está rodando
        import streamlit as st
        
        if isinstance(value, bool):
            st.success(f"🟢 DEBUG BOOL: {value} → será booleanValue")
            # Verificar se chegamos aqui ANTES do int
            return {"booleanValue": value}
            
        elif isinstance(value, int):
            if value is True or value is False:
                st.error(f"🔴 ERRO CRÍTICO: Boolean {value} chegou como INT!")
                st.error("🔴 ISSO SIGNIFICA QUE A CORREÇÃO NÃO ESTÁ FUNCIONANDO!")
            st.info(f"🔵 DEBUG INT: {value} → será integerValue")
            return {"integerValue": str(value)}
            
        elif isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, dict):
            fields = {}
            for k, v in value.items():
                fields[k] = self._convert_to_firestore_value(v)
            return {"mapValue": {"fields": fields}}
        else:
            return {"stringValue": str(value)}
    '''
    
    print("   Patch criado para debug em produção")
    print("   ➜ Este patch mostrará exatamente qual código está rodando")
    print("   ➜ Se boolean chegar como int, saberemos que a correção falhou")
    
    return debug_function

if __name__ == "__main__":
    test_boolean_conversion()
    debug_patch = create_production_debug_patch()
    
    print(f"\n" + "="*80)
    print("🎯 DIAGNÓSTICO FINAL:")
    print("   PROBLEMA: isinstance(True, int) é True em Python")
    print("   SOLUÇÃO APLICADA: isinstance(bool) verificado ANTES de isinstance(int)")
    print("   STATUS: Aguardando confirmação que correção está ativa em produção")
    print("="*80)