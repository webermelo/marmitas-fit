# 🥗 Marmitas Fit - Sistema Web

Sistema web completo para gestão de marmitas fitness com cálculos automáticos de custos, calorias e geração de listas de compras.

## ✨ Funcionalidades

### 🥕 **Gestão de Ingredientes**
- Cadastro completo com preços e informações nutricionais
- Categorização automática
- Conversão de unidades (receita ↔ compra)

### 📝 **Criação de Receitas**
- Interface intuitiva para montagem de receitas
- Cálculo automático de custos e calorias
- Visualização detalhada dos ingredientes

### 🏭 **Planejamento de Produção**
- Seleção múltipla de receitas
- Definição de quantidades por receita
- Cálculo de custo por marmita
- Histórico de produções

### 🛒 **Lista de Compras Inteligente**
- Consolidação automática de ingredientes
- Conversão para unidades de compra
- Cálculo de custos totais
- **Export para PDF** com formatação profissional

### 🔐 **Autenticação**
- Login/registro com Firebase Authentication
- Modo demonstração para testes
- Dados isolados por usuário

## 🚀 **Demo Online**

👉 **[Acesse a aplicação](https://marmitasfit.streamlit.app)** 

*Modo demonstração disponível - não é necessário criar conta para testar!*

## 🛠️ **Tecnologias**

- **Frontend**: Streamlit
- **Backend**: Python
- **Banco de Dados**: Firebase Firestore
- **Autenticação**: Firebase Auth
- **PDF**: ReportLab
- **Deploy**: Streamlit Cloud

## 📱 **Como usar**

### Online (Recomendado)
1. Acesse [marmitasfit.streamlit.app](https://marmitasfit.streamlit.app)
2. Clique em "Usar Modo Demo" para testar
3. Ou crie uma conta para salvar seus dados permanentemente

### Local
1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/marmitas-fit.git
cd marmitas-fit
```

2. Instale as dependências
```bash
pip install -r requirements.txt
```

3. Execute a aplicação
```bash
streamlit run app.py
```

## 🔧 **Configuração Firebase (Opcional)**

Para usar autenticação real e banco de dados, configure suas credenciais Firebase em `.streamlit/secrets.toml`:

```toml
[firebase]
apiKey = "sua-api-key"
authDomain = "seu-projeto.firebaseapp.com"
projectId = "seu-projeto-id"
storageBucket = "seu-projeto.appspot.com"
messagingSenderId = "123456789"
appId = "1:123456789:web:abcdef123456"
databaseURL = "https://seu-projeto-default-rtdb.firebaseio.com/"
```

## 🎮 Modo Demonstração

O sistema funciona em **modo demonstração** mesmo sem Firebase:
- Use qualquer email/senha para login
- Dados são salvos na sessão (temporários)
- Ingredientes padrão são carregados automaticamente

## 📋 Funcionalidades

### ✅ Implementado
- **Autenticação multi-usuário** (Firebase Auth + modo demo)
- **Gestão de ingredientes** (CRUD completo)
- **Criação de receitas** com cálculo automático de custos/calorias
- **Planejamento de produção** com múltiplas receitas
- **Lista de compras consolidada** com cálculos precisos
- **Dashboard** com métricas e início rápido
- **Interface responsiva** com Streamlit
- **Exportação de dados** (Excel/CSV)

### 🔄 Em Desenvolvimento
- Relatórios avançados com gráficos
- Análise nutricional detalhada
- Sistema de notificações
- Integração completa com Firebase Storage

## 🗂️ Estrutura do Projeto

```
marmitas_web/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── run_webapp.bat        # Script de execução
├── config/
│   └── firebase_config.py # Configurações Firebase
├── pages/
│   ├── auth.py           # Sistema de autenticação
│   ├── ingredientes.py   # Gestão de ingredientes
│   ├── receitas.py       # Gestão de receitas
│   └── producao.py       # Planejamento de produção
├── utils/
│   └── database.py       # Operações Firestore
└── .streamlit/
    └── config.toml       # Configurações Streamlit
```

## 🔐 Segurança

- **Autenticação Firebase**: Login seguro por email/senha
- **Dados isolados**: Cada usuário vê apenas seus dados
- **Validação de entrada**: Todos os campos são validados
- **Modo offline**: Funciona sem conexão para demonstração

## 🎯 Uso do Sistema

### 1. **Login/Registro**
- Crie conta ou faça login
- Modo demo disponível para testes

### 2. **Cadastrar Ingredientes**
- Adicione ingredientes com preços e informações nutricionais
- Organize por categorias
- Importe de Excel se necessário

### 3. **Criar Receitas**
- Monte receitas com ingredientes cadastrados
- Veja cálculos automáticos de custo e calorias
- Salve para uso na produção

### 4. **Planejar Produção**
- Adicione receitas ao planejamento
- Defina quantidades de cada receita
- Visualize custos totais

### 5. **Gerar Lista de Compras**
- Lista consolidada de todos os ingredientes
- Quantidades exatas para comprar
- Custos estimados por item

## 💡 Dicas de Uso

- **Mantenha preços atualizados** para cálculos precisos
- **Use categorias** para organizar ingredientes
- **Exporte dados** regularmente como backup
- **Teste no modo demo** antes de configurar Firebase

## 🆘 Suporte

- Sistema totalmente **web-based**
- Funciona em qualquer navegador moderno
- **Responsivo** - funciona em mobile e desktop
- **Multi-usuário** - cada pessoa tem seus dados isolados

## 🔧 Personalização

O sistema pode ser facilmente personalizado:
- Cores e tema em `.streamlit/config.toml`
- Configurações Firebase em `config/firebase_config.py`
- Novas páginas em `pages/`
- Funcionalidades de banco em `utils/database.py`