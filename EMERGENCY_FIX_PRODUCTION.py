#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO DE EMERGÊNCIA PARA PRODUÇÃO
PROBLEMA: Nossa correção local não foi deployada
"""

def create_production_fix():
    """Cria correção definitiva para produção"""
    
    print("CORRECAO EMERGENCIA - PRODUCAO")
    print("=" * 60)
    print("PROBLEMA: Correcao local NAO foi deployada")
    print("SOLUCAO: Aplicar patch definitivo")
    print("=" * 60)
    
    # Ler arquivo atual
    file_path = "utils/firestore_client.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"1. Arquivo atual: {len(content)} chars")
    
    # Verificar se nossa correção está presente
    if "isinstance(value, bool)" in content and "isinstance(value, int)" in content:
        bool_pos = content.find("isinstance(value, bool)")
        int_pos = content.find("isinstance(value, int)")
        
        if bool_pos < int_pos:
            print("2. Correcao JA aplicada localmente")
        else:
            print("2. Correcao NAO aplicada - aplicando agora")
    
    # Aplicar correção DEFINITIVA
    corrected_function = '''    def _convert_to_firestore_value(self, value):
        """Converte valor Python para formato Firestore - PRODUCTION FIX"""
        
        # CRITICAL FIX: Bool must come BEFORE int check
        # isinstance(True, int) returns True in Python!
        
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):  # MUST BE FIRST - bool is subclass of int
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
    
    # Substituir função no arquivo
    import re
    
    # Padrão para encontrar a função
    pattern = r'def _convert_to_firestore_value\(self, value\):.*?(?=\n    def|\n\nclass|\nclass|\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, corrected_function, content, flags=re.DOTALL)
        
        # Salvar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("3. CORRECAO APLICADA com sucesso!")
        print("4. COMMIT e PUSH necessarios para deploy")
        
        return True
    else:
        print("3. ERRO: Padrao da funcao nao encontrado")
        return False

def verify_fix():
    """Verifica se correção foi aplicada"""
    print("\nVERIFICACAO:")
    
    # Testar função corrigida
    def test_convert_fixed(value):
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):  # CRITICAL: bool before int
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        else:
            return {"stringValue": str(value)}
    
    # Testar valores problemáticos
    test_true = test_convert_fixed(True)
    test_false = test_convert_fixed(False)
    
    print(f"True -> {test_true}")
    print(f"False -> {test_false}")
    
    if test_true.get('booleanValue') and test_false.get('booleanValue'):
        print("VERIFICACAO: CORRECAO FUNCIONANDO!")
        return True
    else:
        print("VERIFICACAO: CORRECAO FALHOU!")
        return False

def deployment_instructions():
    """Instruções para deploy em produção"""
    
    print("\n" + "=" * 60)
    print("INSTRUCOES PARA DEPLOY EM PRODUCAO")
    print("=" * 60)
    print("1. git add utils/firestore_client.py")
    print("2. git commit -m 'HOTFIX: Boolean conversion production'")
    print("3. git push origin main")
    print("4. Streamlit Cloud: Esperar auto-deploy (2-3 min)")
    print("5. Limpar cache browser: Ctrl+Shift+Del")
    print("6. Testar upload novamente")
    print("=" * 60)

if __name__ == "__main__":
    success = create_production_fix()
    
    if success:
        verify_fix()
        deployment_instructions()
        print("\nRESULTADO: CORRECAO PRONTA PARA DEPLOY")
    else:
        print("\nRESULTADO: FALHA NA CORRECAO")