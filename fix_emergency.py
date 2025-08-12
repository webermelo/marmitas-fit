#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção de Emergência - Força a correção diretamente
"""

import sys
import os

sys.path.append(os.getcwd())

def emergency_fix():
    """Aplica correção diretamente no arquivo"""
    print("CORRECAO DE EMERGENCIA")
    print("=" * 50)
    
    file_path = "utils/firestore_client.py"
    
    # Ler arquivo atual
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"1. Arquivo lido: {len(content)} caracteres")
    
    # Verificar se há problema na ordem
    lines = content.split('\n')
    
    # Encontrar a função _convert_to_firestore_value
    func_start = -1
    for i, line in enumerate(lines):
        if 'def _convert_to_firestore_value(self, value):' in line:
            func_start = i
            break
    
    if func_start == -1:
        print("Função não encontrada!")
        return False
    
    print(f"2. Função encontrada na linha {func_start}")
    
    # Verificar as linhas relevantes
    bool_line = -1
    int_line = -1
    
    for i in range(func_start, min(func_start + 20, len(lines))):
        line = lines[i]
        if 'isinstance(value, bool)' in line:
            bool_line = i
            print(f"   bool check na linha {i}: {line.strip()}")
        elif 'isinstance(value, int)' in line:
            int_line = i
            print(f"   int check na linha {i}: {line.strip()}")
    
    if bool_line != -1 and int_line != -1:
        if bool_line < int_line:
            print("3. Ordem CORRETA: bool antes de int")
        else:
            print("3. Ordem INCORRETA: int antes de bool - CORRIGINDO")
            # Aqui fariamos a correção se necessário
    
    # Criar uma versão limpa da função
    clean_function = '''    def _convert_to_firestore_value(self, value):
        """Converte valor Python para formato Firestore - VERSAO CORRIGIDA"""
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):  # CRITICAL: bool MUST come before int
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, dict):
            fields = {}
            for k, v in value.items():
                fields[k] = self._convert_to_firestore_value(v)
            return {"mapValue": {"fields": fields}}
        else:
            return {"stringValue": str(value)}'''
    
    print(f"\n4. Testando função corrigida:")
    
    # Simular a função corrigida
    def test_convert(value):
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):  # CRITICAL: bool MUST come before int
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        else:
            return {"stringValue": str(value)}
    
    # Testar
    test_true = test_convert(True)
    test_false = test_convert(False)
    test_int = test_convert(123)
    
    print(f"   True -> {test_true}")
    print(f"   False -> {test_false}")  
    print(f"   123 -> {test_int}")
    
    if test_true.get('booleanValue') and test_false.get('booleanValue') and test_int.get('integerValue'):
        print("   FUNCAO CORRIGIDA FUNCIONANDO!")
        
        # Aplicar correção no arquivo real
        # Encontrar e substituir a função
        new_content = content
        
        # Procurar pelo padrão da função e substituir
        import re
        
        pattern = r'def _convert_to_firestore_value\(self, value\):.*?(?=\n    def|\n\nclass|\nclass|\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, clean_function, content, flags=re.DOTALL)
            
            # Salvar arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("5. CORRECAO APLICADA NO ARQUIVO!")
            return True
        else:
            print("5. Padrao nao encontrado para substituicao")
            return False
    else:
        print("   Funcao ainda com problema")
        return False

if __name__ == "__main__":
    success = emergency_fix()
    if success:
        print("\nCORRECAO CONCLUIDA - Teste novamente o upload!")
    else:
        print("\nFALHA NA CORRECAO")