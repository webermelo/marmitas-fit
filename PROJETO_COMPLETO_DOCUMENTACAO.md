# 🥗 MARMITAS FIT - DOCUMENTAÇÃO COMPLETA DO PROJETO

## 📋 SUMÁRIO EXECUTIVO

**Projeto**: Sistema Web Multi-usuário para Gestão de Marmitas Fit
**Objetivo**: Transformar aplicação desktop Python em SaaS web para empreendedores de marmitas
**Status Atual**: 90% funcional, com problema crítico de persistência de dados Firebase
**Usuário Principal**: weber.melo@gmail.com (Super Admin)

---

## 🏗️ ARQUITETURA GERAL

### Stack Tecnológico
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.x com Streamlit
- **Database**: Firebase Firestore (NoSQL)
- **Authentication**: Firebase Auth via REST API
- **Deployment**: Streamlit Cloud
- **Repository**: GitHub (https://github.com/webermelo/marmitas-fit.git)

### Estrutura de Diretórios
```
marmitas_web/
├── app.py                          # Aplicação principal
├── pages/
│   ├── admin_safe.py              # Painel administrativo (CSV uploads)
│   ├── admin.py                   # Painel antigo (problemas openpyxl)
│   ├── debug.py                   # Ferramentas de debug
│   └── cleanup.py                 # Limpeza de dados duplicados
├── utils/
│   ├── firebase_auth.py           # Autenticação Firebase REST API
│   ├── firestore_client.py        # Cliente Firestore REST API
│   └── logger.py                  # Sistema de logging
├── .streamlit/
│   └── secrets.toml              # Credenciais Firebase
└── requirements.txt              # Dependências Python
```

---

## 🔐 CONFIGURAÇÃO FIREBASE

### Credenciais (.streamlit/secrets.toml)
```toml
[firebase]
apiKey = "AIzaSyAqT9_WZpr5vHYI27YNL9SY0mjmm376f90"
authDomain = "marmita-fit-6a3ca.firebaseapp.com"
projectId = "marmita-fit-6a3ca"
storageBucket = "marmita-fit-6a3ca.firebasestorage.app"
messagingSenderId = "183148230819"
appId = "1:183148230819:web:c72f2a2c545ea0f443a716"
```

### Estrutura do Firestore
```
/users/{user_uid}/
├── ingredients/          # Ingredientes do usuário
│   ├── {doc_id}
│   │   ├── nome: string
│   │   ├── categoria: string
│   │   ├── preco: number
│   │   ├── unid_receita: string
│   │   ├── unid_compra: string
│   │   ├── kcal_unid: number
│   │   ├── fator_conv: number
│   │   ├── ativo: boolean
│   │   └── observacoes: string
├── recipes/             # Receitas do usuário
└── production/          # Histórico de produções
```

### Implementação REST API
- **Motivo**: pyrebase4 incompatível com urllib3 no Streamlit Cloud
- **Solução**: Cliente REST API customizado
- **Classes**: `FirebaseAuth` e `FirestoreClient`

---

## 👥 SISTEMA DE AUTENTICAÇÃO

### Funcionalidades
- ✅ Registro de novos usuários
- ✅ Login com email/senha
- ✅ Persistência de login via query parameters
- ✅ Modo demo (sem Firebase)
- ✅ Isolamento de dados por usuário

### Usuários Administrativos
- **Super Admin**: weber.melo@gmail.com
- **Privilégios**: Acesso completo, templates, uploads, debug

### Persistência de Login
```python
# Salvar sessão
st.query_params["logged_in"] = "true"
st.query_params["user_email"] = user_email
st.query_params["user_uid"] = user_uid
st.query_params["user_token"] = user_token

# Restaurar sessão
if st.query_params.get("logged_in") == "true":
    # Restaurar dados do usuário
```

---

## 🥕 FUNCIONALIDADES PRINCIPAIS

### 1. Gestão de Ingredientes
- **Cadastro manual**: Nome, categoria, preços, calorias, conversões
- **Upload CSV**: Importação em massa de ingredientes
- **Estruturas de dados**: Compatibilidade entre versões antigas/novas
- **Persistência**: Firebase Firestore + Session State

### 2. Criação de Receitas
- **Ingredientes**: Seleção de ingredientes cadastrados
- **Cálculos**: Custo total, calorias, conversões automáticas
- **Persistência**: Firebase + Session State

### 3. Planejamento de Produção
- **Seleção**: Receitas e quantidades de marmitas
- **Lista de Compras**: Consolidação automática de ingredientes
- **PDF**: Download de listas formatadas
- **Histórico**: Salvamento de produções anteriores

### 4. Painel Administrativo
- **Templates CSV**: Download de modelos para ingredientes, embalagens, custos fixos
- **Upload**: Importação em massa via CSV
- **Limpeza**: Remoção de duplicatas
- **Debug**: Ferramentas de diagnóstico

---

## 💰 MODELO DE NEGÓCIO

### Pricing
- **Valor**: R$ 29,90/ano por usuário
- **Margem**: 40% de lucro sobre custos
- **Meta**: 200.000 usuários
- **Preço Sugerido**: Calculado automaticamente com margem

### Features Premium
- ✅ Dados persistentes no Firebase
- ✅ Múltiplos usuários isolados
- ✅ Templates profissionais
- ✅ Relatórios em PDF
- ✅ Histórico completo

---

## 🔧 PROBLEMAS TÉCNICOS RESOLVIDOS

### 1. PyInstaller Desktop (RESOLVIDO)
**Problema**: Lista de compras não gerava no executável
**Causa**: Caminhos relativos vs absolutos
**Solução**: Detecção automática de execução (script vs executável)

### 2. Streamlit Cache (RESOLVIDO)
**Problema**: Receitas não salvavam (@st.cache_resource)
**Causa**: Cache impedia updates no session state
**Solução**: Remoção de decorators problemáticos

### 3. Firebase pyrebase4 (RESOLVIDO)
**Problema**: INVALID_LOGIN_CREDENTIALS, incompatibilidade urllib3
**Causa**: pyrebase4 desatualizado
**Solução**: Cliente REST API customizado

### 4. OpenPyXL Excel (RESOLVIDO)
**Problema**: 'MergedCell' object has no attribute 'column_letter'
**Causa**: Conflitos openpyxl no Streamlit Cloud
**Solução**: Migração para CSV (admin_safe.py)

### 5. Encoding Português (RESOLVIDO)
**Problema**: Caracteres acentuados corrompidos
**Causa**: Encoding padrão UTF-8
**Solução**: UTF-8-sig + remoção de acentos

### 6. Imports Circulares (RESOLVIDO)
**Problema**: Firebase não salvava ingredientes (linha 638 admin_safe.py)
**Causa**: `from app import save_ingredient_to_firebase`
**Solução**: Função local `save_ingredient_to_firebase_direct()`

---

## 🚨 PROBLEMA CRÍTICO ATUAL

### Sintomas
```
DEBUG: st.session_state.demo_ingredients tem 0 itens
❌ st.session_state.demo_ingredients está vazio ou None
🔄 Tentando carregar do Firebase...
❌ Nenhum ingrediente encontrado no Firebase
```

### Análise Detalhada
1. **Upload Aparentemente Bem-sucedido**: Mostra "198 ingredientes salvos com sucesso"
2. **Firebase Vazio**: `load_ingredients_from_firebase()` retorna lista vazia
3. **Possíveis Causas**:
   - Token de autenticação inválido/expirado
   - Dados salvos em coleção incorreta
   - Problema de permissões Firestore
   - Erro silencioso na função de save

### Estruturas de Dados Conflitantes
```python
# Estrutura UPLOAD (CSV)
{
    "nome": "Frango",
    "categoria": "Proteína",
    "preco": 15.90
}

# Estrutura APP (compatibilidade)
{
    "Nome": "Frango",           # Maiúsculo
    "Categoria": "Proteína", 
    "Preco_Padrao": 15.90      # Underscore
}
```

### Debug Implementado
- **Logging detalhado**: Cada passo do upload/save
- **Debug interface**: Visualização de estruturas de dados
- **Error tracking**: Stack traces completos
- **Token verification**: Validação de autenticação

---

## 🔍 FUNÇÕES CRÍTICAS PARA INVESTIGAÇÃO

### 1. save_ingredient_to_firebase_direct() (admin_safe.py:714-750)
```python
def save_ingredient_to_firebase_direct(ingredient):
    """Salva ingrediente diretamente no Firebase SEM import circular"""
    # CRÍTICO: Esta função deve funcionar
    # Local: pages/admin_safe.py linha ~714
```

### 2. load_ingredients_from_firebase() (app.py:376-420)
```python
def load_ingredients_from_firebase():
    """Carrega ingredientes do Firebase com conversão de estrutura"""
    # CRÍTICO: Retorna lista vazia quando deveria ter 198 itens
    # Local: app.py linha ~376
```

### 3. Token Authentication
```python
# Verificar se token está válido
if 'token' in st.session_state.user:
    db.set_auth_token(st.session_state.user['token'])
```

---

## 📊 DADOS DE TESTE

### Ingredientes Base
- **Arquivo**: ingredientes_completos_200.csv
- **Quantidade**: 200 ingredientes únicos
- **Categorias**: Proteína Animal, Carboidrato, Vegetal, Tempero
- **Campos**: Nome, Categoria, Preço, Unidades, Calorias, Fator Conversão

### Usuário de Teste
- **Email**: weber.melo@gmail.com
- **Senha**: @Teste123
- **Privilégios**: Super Admin
- **UID**: (gerado pelo Firebase Auth)

---

## 🛠️ PRÓXIMOS PASSOS PARA RESOLUÇÃO

### Investigação Prioritária
1. **Verificar Token**: `st.session_state.user['token']` válido?
2. **Debug Firestore**: Dados realmente salvos na coleção correta?
3. **Permissões**: Rules do Firestore permitem read/write?
4. **Path Correction**: Coleção `users/{uid}/ingredients` existe?

### Debugging Sugerido
```python
# 1. Verificar token
logger.info(f"Token: {st.session_state.user.get('token', 'MISSING')[:50]}...")

# 2. Verificar dados salvos
logger.info(f"Tentando ler de: users/{user_id}/ingredients")

# 3. Verificar resposta raw
logger.info(f"Firebase response: {raw_ingredients}")

# 4. Verificar estrutura
for ing in raw_ingredients:
    logger.info(f"Ingredient keys: {list(ing.keys())}")
```

### Testes Necessários
1. **Manual Firestore**: Verificar dados via console Firebase
2. **Token Validation**: Testar token em API call manual
3. **Collection Path**: Confirmar path da coleção
4. **Data Structure**: Verificar estrutura salva vs esperada

---

## 📝 COMANDOS ÚTEIS

### Git
```bash
cd "C:/Users/weber/onedrive/jupyter/gemini cli/marmitas_web"
git add -A
git commit -m "Fix: descrição"
git push
```

### Streamlit
```bash
streamlit run app.py
```

### Debug Local
- URL: http://localhost:8501
- Logs: Terminal do Streamlit
- Debug Page: Menu "🔍 Debug" (admin only)

---

## 🔗 RECURSOS E LINKS

- **Repository**: https://github.com/webermelo/marmitas-fit.git
- **Streamlit App**: [URL do deploy]
- **Firebase Console**: https://console.firebase.google.com/project/marmita-fit-6a3ca
- **Documentação Streamlit**: https://docs.streamlit.io/
- **Firebase REST API**: https://firebase.google.com/docs/reference/rest/

---

## 💡 OBSERVAÇÕES FINAIS

### Pontos Fortes do Projeto
- ✅ Arquitetura sólida e escalável
- ✅ Interface intuitiva e responsiva
- ✅ Autenticação robusta implementada
- ✅ Sistema de upload/download funcional
- ✅ Cálculos precisos de custos/calorias
- ✅ PDFs profissionais gerados

### Desafios Principais
- 🔄 Persistência de dados Firebase inconsistente
- 🔄 Debugging complexo em ambiente cloud
- 🔄 Compatibilidade de estruturas de dados
- 🔄 Gestão de estado Streamlit

### Recomendações Imediatas
1. **Foco na investigação Firebase**: O upload mostra sucesso mas dados não persistem
2. **Logging intensivo**: Implementar logs detalhados em cada etapa
3. **Teste manual Firestore**: Verificar dados via console
4. **Validação de token**: Confirmar autenticação válida

---

**📅 Última atualização**: 08/01/2025
**👤 Desenvolvido por**: Claude Code (Anthropic) + Weber Melo
**🔧 Status**: Em desenvolvimento ativo - Problema crítico de persistência Firebase