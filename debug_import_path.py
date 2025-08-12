#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug - Verificar qual versão do FirestoreClient está sendo usado
"""

import sys
import os
import inspect

sys.path.append(os.getcwd())

def debug_import_path():
    """Verifica qual arquivo está sendo importado"""
    print("=" * 60)
    print("DEBUG - IMPORT PATH E VERSÕES")
    print("=" * 60)
    
    # Verificar onde está o arquivo
    print("1. Localização do arquivo:")
    firestore_path = "utils/firestore_client.py"
    full_path = os.path.abspath(firestore_path)
    print(f"   Caminho: {full_path}")
    print(f"   Existe: {os.path.exists(full_path)}")
    
    if os.path.exists(full_path):
        # Ler o código atual
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n2. Análise do código atual:")
        
        # Verificar se bool vem antes de int
        bool_pos = content.find("isinstance(value, bool)")
        int_pos = content.find("isinstance(value, int)")
        
        if bool_pos != -1 and int_pos != -1:
            print(f"   isinstance(value, bool) na posição: {bool_pos}")
            print(f"   isinstance(value, int) na posição: {int_pos}")
            
            if bool_pos < int_pos:
                print(f"   ✓ bool vem ANTES de int (correção aplicada)")
            else:
                print(f"   ✗ int vem ANTES de bool (problema!)")
        
        # Verificar se há comentário da correção
        if "CORREÇÃO: bool deve vir ANTES de int" in content:
            print(f"   ✓ Comentário da correção encontrado")
        else:
            print(f"   ✗ Comentário da correção não encontrado")
    
    # Testar importação real
    print(f"\n3. Teste de importação real:")
    
    try:
        from utils.firestore_client import FirestoreClient
        
        # Verificar localização do módulo importado
        module = sys.modules.get('utils.firestore_client')
        if module:
            file_path = getattr(module, '__file__', 'Unknown')
            print(f"   Módulo importado de: {file_path}")
        
        # Verificar código da função
        client = FirestoreClient("test")
        func_source = inspect.getsource(client._convert_to_firestore_value)
        print(f"\n4. Código da função _convert_to_firestore_value:")
        
        lines = func_source.split('\n')
        for i, line in enumerate(lines):
            if 'isinstance' in line:
                print(f"   Linha {i}: {line.strip()}")
        
        # Testar conversão diretamente
        print(f"\n5. Teste direto de conversão:")
        result_true = client._convert_to_firestore_value(True)
        result_false = client._convert_to_firestore_value(False)
        
        print(f"   True -> {result_true}")
        print(f"   False -> {result_false}")
        
        if result_true.get('booleanValue') is not None:
            print(f"   ✓ Conversão boolean funcionando")
        elif result_true.get('integerValue') is not None:
            print(f"   ✗ Boolean sendo convertido para integerValue!")
            
    except Exception as e:
        print(f"   Erro na importação: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n6. Verificar se há outros arquivos com conversão:")
    
    # Procurar por outros arquivos que podem ter código similar
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and file != 'firestore_client.py':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '_convert_to_firestore_value' in content:
                            print(f"   Função encontrada em: {file_path}")
                except:
                    pass

if __name__ == "__main__":
    debug_import_path()