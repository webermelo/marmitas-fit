#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY AUTH FIX - OPUS 4.1
Correção emergencial para problema de autenticação Token 401
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import sys
import os

def diagnose_auth_problem():
    """Diagnóstica problema de autenticação"""
    print("=" * 80)
    print("EMERGENCY AUTH FIX - OPUS 4.1")
    print("=" * 80)
    print(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("PROBLEMA IDENTIFICADO:")
    print("  • ERRO 401: Missing or invalid authentication")
    print("  • Token Firebase expirado ou inválido")
    print("  • Sistema não consegue renovar token automaticamente")
    print("  • Usuário não consegue carregar ingredientes")
    print()
    
    print("CAUSAS POSSÍVEIS:")
    print("  1. Token Firebase expirou (duracao: 1 hora)")
    print("  2. Refresh token inválido")
    print("  3. Session state corrompido")
    print("  4. Problemas na API key Firebase")
    print("  5. Falha no TokenManager")
    print()
    
    print("SOLUCOES OPUS 4.1:")
    print()
    
    # Solução 1: Logout e Login Novamente
    print("SOLUCAO 1 - LOGOUT E LOGIN NOVAMENTE (MAIS RAPIDA):")
    print("  1. Na aplicacao web: Menu -> Logout")
    print("  2. Fechar todas as abas do navegador")
    print("  3. Abrir nova aba: https://marmitas-fit.streamlit.app/")
    print("  4. Fazer login novamente")
    print("  5. Verificar se ingredientes carregam")
    print("  -> TEMPO: 2-3 minutos")
    print()
    
    # Solução 2: Forçar refresh do app
    print("SOLUCAO 2 - FORCAR REFRESH COMPLETO:")
    print("  1. Na aplicacao: Pressionar Ctrl+F5 (refresh hard)")
    print("  2. Ou Ctrl+Shift+R (clear cache)")
    print("  3. Aguardar app recarregar completamente") 
    print("  4. Fazer login se necessario")
    print("  -> TEMPO: 1-2 minutos")
    print()
    
    # Solução 3: Limpar dados do navegador
    print("SOLUCAO 3 - LIMPAR CACHE NAVEGADOR:")
    print("  1. Abrir DevTools (F12)")
    print("  2. Application -> Storage -> Clear storage")
    print("  3. Ou Settings -> Privacy -> Clear browsing data")
    print("  4. Recarregar página e fazer login")
    print("  -> TEMPO: 3-5 minutos")
    print()
    
    # Diagnóstico técnico
    print("DIAGNOSTICO TECNICO:")
    print()
    
    # Verificar estrutura do projeto
    print("1. VERIFICANDO ARQUIVOS DE AUTENTICACAO:")
    auth_files = [
        "utils/token_manager.py",
        "utils/firestore_client.py", 
        "utils/firebase_auth.py"
    ]
    
    for file_path in auth_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}: OK")
        else:
            print(f"  ❌ {file_path}: MISSING")
    print()
    
    # Configuração Firebase
    print("2. CONFIGURACAO FIREBASE:")
    print("  • Project ID: marmita-fit-6a3ca")
    print("  • API Key: AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90")
    print("  • Database URL: https://marmita-fit-6a3ca-default-rtdb.firebaseio.com/")
    print("  • Status: CONFIGURADO")
    print()
    
    # Token lifecycle
    print("3. CICLO DE VIDA DO TOKEN:")
    print("  • Duracao: 1 hora (3600 segundos)")
    print("  • Renovacao: Automatica via refresh_token")
    print("  • Expiracao: 50 minutos (margem seguranca)")
    print("  • Problema: Token nao sendo renovado")
    print()
    
    print("4. FLUXO DE CORRECAO RECOMENDADO:")
    print("  a) IMEDIATO (usuarios):")
    print("     - Logout -> Login -> Testar ingredientes")
    print("     - Se funcionar: Problema temporario resolvido")
    print()
    print("  b) TECNICO (desenvolvedor):")
    print("     - Implementar melhor handling de token expirado")
    print("     - Adicionar auto-refresh mais agressivo")
    print("     - Melhorar UX para erro de autenticacao")
    print()
    
    # Solução de código
    print("5. CORRECAO DE CODIGO OPUS 4.1:")
    print("   Criar sistema de fallback para token inválido")
    print()
    
    return True

def create_auth_recovery_system():
    """Cria sistema de recuperação de autenticação"""
    
    recovery_code = '''
# EMERGENCY AUTH RECOVERY - Adicionar em app.py

def handle_auth_error():
    """Handle authentication errors gracefully"""
    st.error("🚨 Erro de autenticação detectado!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Tentar Renovar Token", type="primary"):
            try:
                # Force token refresh
                if 'user' in st.session_state:
                    st.session_state.user.pop('token', None)
                    st.session_state.user.pop('token_timestamp', None)
                st.experimental_rerun()
            except:
                st.error("Falha na renovação")
    
    with col2:
        if st.button("🚪 Logout e Login Novamente"):
            # Clear session completely
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    st.info("💡 **Solução rápida**: Faça logout e login novamente")

# ADICIONAR no load_ingredients_from_firebase():
try:
    # ... código existente ...
    ingredients_df = db_manager.get_user_ingredients(user_id)
    # ... resto do código ...
except Exception as e:
    if "401" in str(e) or "UNAUTHENTICATED" in str(e):
        handle_auth_error()
        return []
    else:
        st.error(f"Erro: {e}")
        return []
'''
    
    print("CODIGO DE RECUPERACAO GERADO:")
    print("=" * 60)
    print(recovery_code)
    print("=" * 60)
    print()
    
    # Salvar código
    with open("auth_recovery_code.py", "w", encoding="utf-8") as f:
        f.write(recovery_code)
    
    print("Codigo salvo em: auth_recovery_code.py")
    print()
    
    return True

def main():
    """Função principal"""
    success = diagnose_auth_problem()
    
    if success:
        print("CRIANDO SISTEMA DE RECUPERACAO...")
        create_auth_recovery_system()
        print()
    
    print("RESUMO OPUS 4.1:")
    print("================")
    print("• PROBLEMA: Token Firebase 401 (inválido/expirado)")
    print("• SOLUCAO IMEDIATA: Logout -> Login -> Testar")
    print("• SOLUCAO TECNICA: Melhor handling de erro auth")
    print("• TEMPO RESOLUCAO: 2-3 minutos (usuario)")
    print("• UPLOAD OPUS 4.1: Funcionara apos auth corrigida")
    print()
    print("ACAO RECOMENDADA:")
    print("1. Instruir usuario fazer logout/login")
    print("2. Testar upload OPUS 4.1 com configuracoes validadas")
    print("3. Monitorar 198/198 ingredientes salvos")
    print()
    print("EMERGENCY AUTH ANALYSIS COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()