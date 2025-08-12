#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Crítico - Diferenças Produção vs Local
Investigação do modelo Opus 4.1
"""

import sys
import os
import hashlib

def debug_production_vs_local():
    """
    INVESTIGAÇÃO OPUS 4.1: Por que funciona local mas falha produção?
    """
    print("="*80)
    print("🔬 INVESTIGAÇÃO OPUS 4.1 - PRODUÇÃO vs LOCAL")
    print("="*80)
    
    print("\n1. 📊 ANÁLISE DO STACK TRACE:")
    print("   Path produção: /mount/src/marmitas-fit/")
    print("   Path local: C:/Users/weber/onedrive/jupyter/gemini cli/marmitas_web/")
    print("   ➜ CONFIRMADO: Ambientes diferentes")
    
    print("\n2. 🔍 VERIFICAÇÃO DO ARQUIVO LOCAL:")
    
    firestore_file = "utils/firestore_client.py"
    
    if os.path.exists(firestore_file):
        with open(firestore_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Calcular hash do arquivo
        file_hash = hashlib.md5(content.encode()).hexdigest()
        print(f"   Arquivo existe: ✅")
        print(f"   Hash MD5: {file_hash}")
        print(f"   Tamanho: {len(content)} chars")
        
        # Verificar linha específica 95 (mencionada no stack trace)
        lines = content.split('\n')
        if len(lines) > 95:
            line_95 = lines[94]  # Linha 95 (índice 94)
            print(f"   Linha 95: '{line_95.strip()}'")
        
        # Verificar função _convert_to_firestore_value
        print("\n3. 🧬 ANÁLISE DA FUNÇÃO CRÍTICA:")
        
        bool_pos = content.find("isinstance(value, bool)")
        int_pos = content.find("isinstance(value, int)")
        
        if bool_pos != -1 and int_pos != -1:
            print(f"   isinstance(value, bool) posição: {bool_pos}")
            print(f"   isinstance(value, int) posição: {int_pos}")
            
            if bool_pos < int_pos:
                print("   ✅ LOCAL: bool vem ANTES de int (correto)")
                
                # Extrair o trecho da função
                func_start = content.find("def _convert_to_firestore_value(self, value):")
                if func_start != -1:
                    # Pegar próximas linhas após a função
                    func_lines = []
                    start_line = content[:func_start].count('\n')
                    
                    for i in range(start_line, min(start_line + 15, len(lines))):
                        if i < len(lines):
                            func_lines.append(f"   L{i+1:2d}: {lines[i]}")
                    
                    print("   FUNÇÃO LOCAL:")
                    for line in func_lines:
                        if 'isinstance' in line:
                            print(f"   ➜ {line}")
                        else:
                            print(f"   {line}")
            else:
                print("   ❌ LOCAL: int vem ANTES de bool (PROBLEMA!)")
    
    print(f"\n4. 🎯 HIPÓTESES DO PROBLEMA:")
    print("   A. Deploy não sincronizado - arquivo local ≠ produção")
    print("   B. Cache do Streamlit Cloud mantendo versão antiga")
    print("   C. Import/módulo diferente sendo usado em produção")
    print("   D. Diferença Python version produção vs local")
    
    print(f"\n5. 📋 EVIDÊNCIAS COLETADAS:")
    print("   • Testes locais: PASSAM (conversão correta)")
    print("   • Produção: FALHA (conversão incorreta)")
    print("   • Stack trace: /mount/src/marmitas-fit/utils/firestore_client.py:95")
    print("   • Erro: Campos 7 e 16 → integerValue em vez de booleanValue")
    
    print(f"\n6. 🚀 SOLUÇÕES PROPOSTAS:")
    print("   1. VERIFICAR se correção foi commitada no Git")
    print("   2. FORÇAR redeploy no Streamlit Cloud") 
    print("   3. LIMPAR cache do browser (Ctrl+Shift+Del)")
    print("   4. VERIFICAR se há versão diferente do arquivo em produção")
    print("   5. ADICIONAR debug logging para confirmar qual código roda")
    
    print(f"\n7. 🔬 TESTE DEFINITIVO NECESSÁRIO:")
    print("   Adicionar logging na função _convert_to_firestore_value")
    print("   para mostrar QUAL versão está rodando em produção")

def create_debug_patch():
    """Cria patch de debug para identificar versão em produção"""
    
    print(f"\n8. 📝 CRIANDO PATCH DE DEBUG:")
    
    debug_code = '''    def _convert_to_firestore_value(self, value):
        """Converte valor Python para formato Firestore - DEBUG VERSION"""
        
        # 🚨 DEBUG: Log para identificar qual versão está rodando
        import streamlit as st
        st.error(f"🔬 DEBUG: _convert_to_firestore_value chamada com {value} ({type(value).__name__})")
        st.error(f"🔬 DEBUG: isinstance(value, bool) = {isinstance(value, bool)}")
        st.error(f"🔬 DEBUG: isinstance(value, int) = {isinstance(value, int)}")
        
        if isinstance(value, str):
            st.info("DEBUG: Retornando stringValue")
            return {"stringValue": value}
        elif isinstance(value, bool):  # CORREÇÃO: bool deve vir ANTES de int
            st.success(f"DEBUG: BOOL DETECTADO! Retornando booleanValue para {value}")
            return {"booleanValue": value}
        elif isinstance(value, int):
            st.warning(f"DEBUG: INT DETECTADO! Retornando integerValue para {value}")
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            st.info("DEBUG: Retornando doubleValue")
            return {"doubleValue": value}
        elif isinstance(value, dict):
            st.info("DEBUG: Retornando mapValue")
            fields = {}
            for k, v in value.items():
                fields[k] = self._convert_to_firestore_value(v)
            return {"mapValue": {"fields": fields}}
        else:
            st.warning(f"DEBUG: FALLBACK stringValue para {value}")
            return {"stringValue": str(value)}'''
    
    print("   Patch criado com logs extensivos")
    print("   ➜ Aplicar temporariamente para debug produção")
    
    return debug_code

if __name__ == "__main__":
    debug_production_vs_local()
    debug_patch = create_debug_patch()
    
    print(f"\n" + "="*80)
    print("🎯 CONCLUSÃO OPUS 4.1:")
    print("   PROBLEMA: Ambiente produção usa versão incorreta do código")
    print("   SOLUÇÃO: Verificar deploy + aplicar patch debug temporário")
    print("   URGÊNCIA: ALTA - Aplicação quebrada em produção")
    print("="*80)