# -*- coding: utf-8 -*-
"""
Página de Administração - Versão Segura (Sem openpyxl)
Painel para gerenciar ingredientes, embalagens e usuários
"""

import streamlit as st
from datetime import datetime

# Lista de administradores autorizados
ADMINS = [
    "weber.melo@gmail.com",    # Super Admin Principal
    "weber@marmitasfit.com",   # Backup
    "admin@marmitasfit.com",   # Admin secundário
    "demo@marmitasfit.com"     # Para testes
]

def is_admin(user_email):
    """Verifica se o usuário é administrador"""
    return user_email.lower() in [admin.lower() for admin in ADMINS]

def show_admin_page():
    """Página principal de administração - Versão Segura"""
    
    # Verificar autenticação
    if 'user' not in st.session_state:
        st.error("🔐 Acesso restrito. Faça login primeiro.")
        return
    
    user_email = st.session_state.user.get('email', '')
    
    # Verificar permissões de admin
    if not is_admin(user_email):
        st.error("🚫 Acesso negado. Você não tem permissões de administrador.")
        st.info(f"👤 Usuário atual: {user_email}")
        return
    
    # Interface de administração
    st.title("👑 Painel de Administração")
    st.success(f"🔓 Acesso autorizado: {user_email}")
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📥 Templates", "📤 Uploads & Limpeza", "📊 Estatísticas"])
    
    with tab1:
        show_templates_safe()
    
    with tab2:
        show_uploads_safe()
        st.markdown("---")
        show_cleanup_tools()
    
    with tab3:
        show_stats_safe()

def show_templates_safe():
    """Seção de templates - versão segura"""
    
    st.header("📥 Templates CSV")
    st.info("💡 Baixe os templates para facilitar o preenchimento de dados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("🥕 Ingredientes")
        st.markdown("""
        **Template para:**
        - Nome e categoria
        - Preços atualizados
        - Informações nutricionais
        - Unidades de medida
        """)
        
        csv_ingredientes = """Nome,Categoria,Preco,Unid_Receita,Unid_Compra,Kcal_Unid,Fator_Conv,Ativo,Observacoes
Frango peito,Proteina Animal,18.90,g,kg,1.65,1000,TRUE,Sem pele congelado
Arroz integral,Carboidrato,8.90,g,kg,1.11,1000,TRUE,Grao longo tipo 1
Brocolis,Vegetal,6.50,g,kg,0.34,1000,TRUE,Fresco preco medio
Azeite extra virgem,Gordura,12.00,ml,L,8.84,1000,TRUE,Primeira prensagem
Sal refinado,Tempero,1.20,g,kg,0.00,1000,TRUE,Iodado"""
        
        st.download_button(
            label="📥 Download Ingredientes (CSV)",
            data=csv_ingredientes.encode('utf-8-sig'),
            file_name=f"ingredientes_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.subheader("📦 Embalagens")
        st.markdown("""
        **Template para:**
        - Tipos de embalagens
        - Preços unitários
        - Capacidades
        - Categorias
        """)
        
        csv_embalagens = """Nome,Tipo,Preco,Capacidade_ml,Categoria,Ativo,Descricao
Marmita 500ml,descartavel,0.50,500,principal,TRUE,PP transparente com tampa
Marmita 750ml,descartavel,0.65,750,principal,TRUE,PP transparente com tampa
Marmita 1000ml,descartavel,0.80,1000,principal,TRUE,PP transparente com tampa
Pote sobremesa 150ml,descartavel,0.25,150,complemento,TRUE,Para doces e frutas
Talher plastico,utensilio,0.08,0,utensilio,TRUE,Garfo + faca + colher
Guardanapo,higiene,0.05,0,higiene,TRUE,Papel 20x20cm
Sacola plastica,transporte,0.12,0,transporte,TRUE,30x40cm alca camiseta"""
        
        st.download_button(
            label="📥 Download Embalagens (CSV)",
            data=csv_embalagens.encode('utf-8-sig'),
            file_name=f"embalagens_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        st.subheader("🏠 Custos Fixos")
        st.markdown("""
        **Template para:**
        - Energia, gás, água
        - Aluguel e mão de obra
        - Rateio por marmita
        - Cálculo automático
        """)
        
        csv_custos = """Categoria,Item,Custo_Mensal,Rateio_por_Marmita,Descricao
Energia,Conta de luz,150.00,0.30,Fogao geladeira freezer
Gas,Botijao 13kg,80.00,0.16,Consumo medio mensal
Agua,Conta de agua,60.00,0.12,Limpeza e preparo
Aluguel,Espaco cozinha,800.00,1.60,Proporcional ao uso
Mao de obra,Salario proprio,2000.00,4.00,Base 500 marmitas por mes
TOTAL,,3090.00,6.18,Base 500 marmitas por mes"""
        
        st.download_button(
            label="📥 Download Custos (CSV)",
            data=csv_custos.encode('utf-8-sig'),
            file_name=f"custos_fixos_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col4:
        st.subheader("📝 Receitas")
        st.markdown("""
        **Template para:**
        - Nome da receita
        - Ingredientes e quantidades
        - Preço de custo
        - Informações nutricionais
        """)
        
        csv_receitas = """Nome,Categoria,Ingredientes_JSON,Porcoes,Calorias_Porcao,Preco_Custo,Margem_Lucro,Preco_Sugerido,Ativo,Observacoes
Frango Grelhado com Arroz,Fitness,"{""frango_peito"":200_""arroz_integral"":100_""brocolis"":80_""azeite"":5}",1,420,8.50,40,11.90,TRUE,Rica em proteina
Salada de Quinoa,Vegano,"{""quinoa"":80_""tomate"":60_""pepino"":40_""azeite"":10}",1,285,6.20,40,8.68,TRUE,Rica em fibras
Peixe com Legumes,Light,"{""tilapia"":150_""cenoura"":60_""abobrinha"":60_""azeite"":5}",1,320,9.80,40,13.72,TRUE,Baixa caloria"""
        
        st.download_button(
            label="📥 Download Receitas (CSV)",
            data=csv_receitas.encode('utf-8-sig'),
            file_name=f"receitas_template_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Instruções de uso
    st.markdown("---")
    st.subheader("📋 Como usar os templates:")
    
    with st.expander("📖 Instruções detalhadas"):
        st.markdown("""
        ### 🎯 Passo a passo:
        
        1. **📥 Baixe** o template desejado (formato CSV)
        2. **📝 Abra** no Excel ou Google Sheets
        3. **✏️ Preencha** os dados nas colunas
        4. **💾 Salve** como CSV
        5. **📤 Contate** o administrador para fazer upload
        6. **✅ Confirme** a importação
        
        ### ⚠️ Regras importantes:
        
        - **Não altere** os nomes das colunas
        - **Mantenha** os tipos de dados (texto, número, verdadeiro/falso)
        - **Use pontos** para decimais (ex: 18.90)
        - **Ative/Desative** com TRUE/FALSE
        - **Teste primeiro** com poucos registros
        
        ### 🔄 Frequência de atualização:
        
        - **Ingredientes:** Mensal (preços de mercado)
        - **Embalagens:** Trimestral (novos fornecedores)
        - **Custos Fixos:** Conforme necessário
        - **Receitas:** Conforme criação de novos pratos
        
        ### 📝 Formato especial para Receitas:
        
        - **Ingredientes_JSON:** Use formato `{"ingrediente":quantidade_"outro":quantidade}`
        - **Margem_Lucro:** Porcentagem (ex: 40 para 40%)
        - **Exemplo:** `{"frango_peito":200_"arroz":100_"brocolis":50}`
        """)
    
    # FERRAMENTAS DE EMERGÊNCIA AQUI (mais visível)
    st.markdown("---")
    st.subheader("🚨 ATENÇÃO: Limpeza de Dados")
    
    total_ingredients = len(st.session_state.get('demo_ingredients', []))
    if total_ingredients > 10:
        st.error(f"⚠️ PROBLEMA DETECTADO: {total_ingredients} ingredientes duplicados!")
        st.info("💡 Use os botões abaixo para resolver:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ LIMPAR DUPLICATAS", key="fix_duplicates_now", type="primary"):
                ingredientes_unicos = []
                nomes_vistos = set()
                
                for ing in st.session_state.demo_ingredients:
                    nome = ing.get('Nome', '')
                    if nome and nome not in nomes_vistos and str(nome).lower() not in ['none', 'nan', '']:
                        ingrediente_limpo = {
                            'Nome': nome,
                            'Categoria': ing.get('Categoria', 'Outros'),
                            'Unidade_Receita': ing.get('Unidade_Receita', 'g'),
                            'Unidade_Compra': ing.get('Unidade_Compra', 'kg'),
                            'Preco_Padrao': float(ing.get('Preco_Padrao', 0)),
                            'Kcal_Por_Unidade_Receita': float(ing.get('Kcal_Por_Unidade_Receita', 0)),
                            'Fator_Conversao': float(ing.get('Fator_Conversao', 1000))
                        }
                        ingredientes_unicos.append(ingrediente_limpo)
                        nomes_vistos.add(nome)
                
                st.session_state.demo_ingredients = ingredientes_unicos
                st.success(f"✅ CORRIGIDO! {len(ingredientes_unicos)} ingredientes únicos.")
                st.balloons()
                st.rerun()
        
        with col2:
            if st.button("🔄 RESETAR DADOS", key="reset_all_data"):
                st.session_state.demo_ingredients = [
                    {'Nome': 'Frango (peito)', 'Categoria': 'Proteína Animal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 18.9, 'Kcal_Por_Unidade_Receita': 1.65, 'Fator_Conversao': 1000},
                    {'Nome': 'Arroz integral', 'Categoria': 'Carboidrato', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 1.11, 'Fator_Conversao': 1000},
                    {'Nome': 'Brócolis', 'Categoria': 'Vegetal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 0.34, 'Fator_Conversao': 1000},
                ]
                st.success("✅ RESETADO! Dados limpos.")
                st.rerun()
    else:
        st.success(f"✅ Dados OK: {total_ingredients} ingredientes")

def show_uploads_safe():
    """Seção de uploads CSV - versão segura"""
    
    st.header("📤 Upload de Dados")
    st.info("📋 Faça upload dos templates CSV preenchidos para popular o banco de dados")
    
    # Tabs para diferentes tipos de upload
    tab1, tab2, tab3, tab4 = st.tabs(["🥕 Ingredientes", "📦 Embalagens", "🏠 Custos Fixos", "📝 Receitas"])
    
    with tab1:
        upload_ingredientes_safe()
    
    with tab2:
        upload_embalagens_safe()
    
    with tab3:
        upload_custos_fixos_safe()
    
    with tab4:
        upload_receitas_safe()
    
    # Seção de emergência para limpeza rápida
    st.markdown("---")
    st.subheader("🚨 Limpeza Rápida de Emergência")
    
    total_ingredients = len(st.session_state.get('demo_ingredients', []))
    if total_ingredients > 10:
        st.error(f"⚠️ Detectados {total_ingredients} ingredientes (possível duplicação!)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ LIMPAR DUPLICATAS AGORA", key="emergency_cleanup", type="primary"):
                if st.session_state.get('demo_ingredients'):
                    ingredientes_unicos = []
                    nomes_vistos = set()
                    
                    for ing in st.session_state.demo_ingredients:
                        nome = ing.get('Nome', '')
                        if nome and nome not in nomes_vistos and str(nome).lower() not in ['none', 'nan', '']:
                            # Garantir estrutura correta
                            ingrediente_limpo = {
                                'Nome': nome,
                                'Categoria': ing.get('Categoria', 'Outros'),
                                'Unidade_Receita': ing.get('Unidade_Receita', 'g'),
                                'Unidade_Compra': ing.get('Unidade_Compra', 'kg'),
                                'Preco_Padrao': float(ing.get('Preco_Padrao', 0)),
                                'Kcal_Por_Unidade_Receita': float(ing.get('Kcal_Por_Unidade_Receita', 0)),
                                'Fator_Conversao': float(ing.get('Fator_Conversao', 1000))
                            }
                            ingredientes_unicos.append(ingrediente_limpo)
                            nomes_vistos.add(nome)
                    
                    st.session_state.demo_ingredients = ingredientes_unicos
                    st.success(f"✅ LIMPEZA CONCLUÍDA! {len(ingredientes_unicos)} ingredientes únicos mantidos.")
                    st.balloons()
                    st.rerun()
        
        with col2:
            if st.button("🔄 RESETAR TUDO", key="emergency_reset"):
                st.session_state.demo_ingredients = [
                    {'Nome': 'Frango (peito)', 'Categoria': 'Proteína Animal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 18.9, 'Kcal_Por_Unidade_Receita': 1.65, 'Fator_Conversao': 1000},
                    {'Nome': 'Arroz integral', 'Categoria': 'Carboidrato', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 1.11, 'Fator_Conversao': 1000},
                    {'Nome': 'Brócolis', 'Categoria': 'Vegetal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 0.34, 'Fator_Conversao': 1000},
                ]
                st.success("✅ RESETADO! Volte aos 3 ingredientes iniciais.")
                st.rerun()
    else:
        st.success(f"✅ {total_ingredients} ingredientes - quantidade normal")

def upload_ingredientes_safe():
    """Upload de ingredientes CSV - versão segura"""
    
    st.subheader("🥕 Upload Ingredientes")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de ingredientes",
        type=['csv'],
        key="ingredientes_upload_safe",
        help="Use o template CSV baixado na aba Templates"
    )
    
    if uploaded_file is not None:
        try:
            # Usar pandas com engine Python (sem Excel dependencies)
            import pandas as pd
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Debug: Mostrar informações sobre o DataFrame
            with st.expander("🔍 Debug - Informações do arquivo"):
                st.write("**Colunas encontradas:**")
                st.write(list(df.columns))
                st.write("**Tipos de dados:**")
                st.write(df.dtypes)
                st.write("**Primeiras 3 linhas (raw):**")
                for i in range(min(3, len(df))):
                    st.write(f"Linha {i}: {df.iloc[i].to_dict()}")
                st.write("**Valores únicos na coluna 'Nome' (primeiros 10):**")
                st.write(df['Nome'].dropna().head(10).tolist())
            
            # Validar colunas obrigatórias
            required_columns = ['Nome', 'Categoria', 'Preco', 'Unid_Receita', 'Unid_Compra', 'Kcal_Unid', 'Fator_Conv', 'Ativo']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                st.info("💡 Baixe o template correto na aba Templates")
                return
            
            # Validação de dados
            validation_errors = validate_ingredientes_data(df)
            if validation_errors:
                st.warning("⚠️ **Problemas encontrados nos dados:**")
                for error in validation_errors:
                    st.write(f"- {error}")
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Ingredientes", key="confirm_ingredientes_safe"):
                with st.spinner("Salvando ingredientes..."):
                    success_count = save_ingredientes_to_session(df)
                    if success_count > 0:
                        st.success(f"🎉 {success_count} ingredientes salvos com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao salvar ingredientes")
                        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo está no formato CSV correto")

def upload_embalagens_safe():
    """Upload de embalagens CSV - versão segura"""
    
    st.subheader("📦 Upload Embalagens")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de embalagens",
        type=['csv'],
        key="embalagens_upload_safe",
        help="Use o template CSV baixado na aba Templates"
    )
    
    if uploaded_file is not None:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Validar colunas obrigatórias
            required_columns = ['Nome', 'Tipo', 'Preco', 'Capacidade_ml', 'Categoria', 'Ativo']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                return
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Embalagens", key="confirm_embalagens_safe"):
                with st.spinner("Salvando embalagens..."):
                    success_count = save_embalagens_to_session(df)
                    if success_count > 0:
                        st.success(f"🎉 {success_count} embalagens salvas com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao salvar embalagens")
                        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def upload_custos_fixos_safe():
    """Upload de custos fixos CSV - versão segura"""
    
    st.subheader("🏠 Upload Custos Fixos")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de custos fixos",
        type=['csv'],
        key="custos_upload_safe",
        help="Use o template CSV baixado na aba Templates"
    )
    
    if uploaded_file is not None:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Validar colunas obrigatórias
            required_columns = ['Categoria', 'Item', 'Custo_Mensal', 'Rateio_por_Marmita']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                return
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Custos Fixos", key="confirm_custos_safe"):
                with st.spinner("Salvando custos fixos..."):
                    success_count = save_custos_to_session(df)
                    if success_count > 0:
                        st.success(f"🎉 {success_count} custos fixos salvos com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao salvar custos fixos")
                        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def upload_receitas_safe():
    """Upload de receitas CSV - versão segura"""
    
    st.subheader("📝 Upload Receitas")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV de receitas",
        type=['csv'],
        key="receitas_upload_safe",
        help="Use o template CSV baixado na aba Templates"
    )
    
    if uploaded_file is not None:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', engine='python')
            
            st.write("📋 **Preview dos dados:**")
            st.dataframe(df.head())
            
            st.write(f"📊 **Total de registros:** {len(df)}")
            
            # Validar colunas obrigatórias
            required_columns = ['Nome', 'Categoria', 'Ingredientes_JSON', 'Porcoes', 'Calorias_Porcao', 'Preco_Custo', 'Ativo']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                return
            
            # Validação especial para receitas
            validation_errors = validate_receitas_data(df)
            if validation_errors:
                st.warning("⚠️ **Problemas encontrados nos dados:**")
                for error in validation_errors:
                    st.write(f"- {error}")
            
            # Botão para confirmar upload
            if st.button("✅ Confirmar Upload Receitas", key="confirm_receitas_safe"):
                with st.spinner("Salvando receitas..."):
                    success_count = save_receitas_to_session(df)
                    if success_count > 0:
                        st.success(f"🎉 {success_count} receitas salvas com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao salvar receitas")
                        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def validate_ingredientes_data(df):
    """Valida dados de ingredientes"""
    errors = []
    
    for idx, row in df.iterrows():
        linha = idx + 2  # +2 porque pandas começa em 0 e tem header
        
        # Validar preço
        try:
            preco = float(row['Preco'])
            if preco <= 0:
                errors.append(f"Linha {linha}: Preço deve ser maior que zero")
        except:
            errors.append(f"Linha {linha}: Preço inválido")
        
        # Validar ativo
        if str(row['Ativo']).upper() not in ['TRUE', 'FALSE']:
            errors.append(f"Linha {linha}: Ativo deve ser TRUE ou FALSE")
    
    return errors[:10]  # Limitar a 10 erros para não poluir a tela

def validate_receitas_data(df):
    """Valida dados de receitas"""
    errors = []
    
    for idx, row in df.iterrows():
        linha = idx + 2
        
        # Validar JSON de ingredientes (formato simplificado)
        ingredientes_str = str(row['Ingredientes_JSON'])
        if not (ingredientes_str.startswith('{') and ingredientes_str.endswith('}')):
            errors.append(f"Linha {linha}: Formato de ingredientes inválido (deve começar com {{ e terminar com }})")
        
        # Validar porções
        try:
            porcoes = int(row['Porcoes'])
            if porcoes <= 0:
                errors.append(f"Linha {linha}: Porções deve ser maior que zero")
        except:
            errors.append(f"Linha {linha}: Porções inválido")
    
    return errors[:10]

def save_ingredientes_to_session(df):
    """Salva ingredientes no session state E Firebase - VERSÃO COMPLETA"""
    try:
        # Limpar ingredientes existentes para evitar duplicatas
        st.session_state.demo_ingredients = []
        
        success_count = 0
        firebase_success_count = 0
        failed_rows = []
        
        # PASSO 1: Limpar todos os ingredientes antigos do Firebase se for admin
        if 'user' in st.session_state:
            clear_all_user_ingredients_from_firebase()
        
        for idx, row in df.iterrows():
            try:
                # Validar dados linha por linha
                nome = str(row['Nome']).strip() if pd.notna(row['Nome']) else ''
                categoria = str(row['Categoria']).strip() if pd.notna(row['Categoria']) else ''
                
                # Pular linhas vazias
                if not nome or nome.lower() == 'nan' or not categoria or categoria.lower() == 'nan':
                    continue
                
                # Converter preço com tratamento de erro
                try:
                    preco = float(row['Preco']) if pd.notna(row['Preco']) else 0.0
                except:
                    preco = 0.0
                
                # Converter calorias com tratamento de erro
                try:
                    kcal_unid = float(row['Kcal_Unid']) if pd.notna(row['Kcal_Unid']) else 0.0
                except:
                    kcal_unid = 0.0
                
                # Converter fator de conversão
                try:
                    fator_conv = float(row['Fator_Conv']) if pd.notna(row['Fator_Conv']) else 1.0
                except:
                    fator_conv = 1.0
                
                # Estrutura COMPATÍVEL com o app (Nome maiúsculo, Preco_Padrao, etc.)
                ingredient_data_compatible = {
                    # Estrutura ANTIGA que o app espera
                    'Nome': nome,
                    'Categoria': categoria,
                    'Unidade_Receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
                    'Unidade_Compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
                    'Preco_Padrao': preco,
                    'Kcal_Por_Unidade_Receita': kcal_unid,
                    'Fator_Conversao': fator_conv,
                    'Ativo': str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True,
                    'Observacoes': str(row.get('Observacoes', '')).strip() if pd.notna(row.get('Observacoes', '')) else '',
                    
                    # Estrutura NOVA também (para Firebase)
                    'nome': nome,
                    'categoria': categoria,
                    'unid_receita': str(row['Unid_Receita']).strip() if pd.notna(row['Unid_Receita']) else 'g',
                    'unid_compra': str(row['Unid_Compra']).strip() if pd.notna(row['Unid_Compra']) else 'kg',
                    'preco': preco,
                    'kcal_unid': kcal_unid,
                    'fator_conv': fator_conv,
                    'ativo': str(row['Ativo']).upper() == 'TRUE' if pd.notna(row['Ativo']) else True,
                    'observacoes': str(row.get('Observacoes', '')).strip() if pd.notna(row.get('Observacoes', '')) else ''
                }
                
                # Salvar no session state (estrutura compatível)
                st.session_state.demo_ingredients.append(ingredient_data_compatible)
                success_count += 1
                
                # SALVAR NO FIREBASE (SEM IMPORT CIRCULAR)
                try:
                    if save_ingredient_to_firebase_direct(ingredient_data_compatible):
                        firebase_success_count += 1
                        st.success(f"🔥 '{nome}' salvo no Firebase!")
                    else:
                        st.error(f"❌ Falha ao salvar '{nome}' no Firebase")
                except Exception as firebase_error:
                    st.error(f"❌ ERRO FIREBASE '{nome}': {firebase_error}")
                    st.code(str(firebase_error))  # Mostrar erro completo
                    # NÃO usar pass - queremos ver os erros!
                
            except Exception as row_error:
                failed_rows.append(f"Linha {idx+2}: {str(row_error)}")
                continue
        
        # Mostrar resultados
        if firebase_success_count > 0:
            st.success(f"🔥 {firebase_success_count} ingredientes salvos no Firebase!")
            st.success(f"💾 {success_count} ingredientes salvos localmente!")
        else:
            st.warning(f"💾 {success_count} ingredientes salvos apenas localmente (Firebase indisponível)")
        
        # Mostrar erros se houver
        if failed_rows:
            st.warning("⚠️ Algumas linhas não puderam ser importadas:")
            for error in failed_rows[:5]:  # Mostrar apenas os primeiros 5 erros
                st.write(f"- {error}")
            if len(failed_rows) > 5:
                st.write(f"... e mais {len(failed_rows)-5} erros")
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro geral no upload: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return 0

def save_ingredient_to_firebase_direct(ingredient):
    """Salva ingrediente diretamente no Firebase SEM import circular"""
    
    # Verificar se usuário está logado
    if 'user' not in st.session_state:
        st.error("❌ Usuário não logado")
        return False
    
    try:
        # Import direto do cliente
        from utils.firestore_client import get_firestore_client
        
        # Obter cliente Firestore
        db = get_firestore_client()
        if not db:
            st.error("❌ Cliente Firestore não inicializado")
            return False
        
        # Verificar e configurar token
        if 'token' not in st.session_state.user or not st.session_state.user['token']:
            st.error("❌ Token de autenticação não encontrado")
            return False
        
        # Configurar autenticação
        token = st.session_state.user['token']
        db.set_auth_token(token)
        st.info(f"🔑 Token configurado: {token[:20]}...")
        
        # Preparar dados
        user_id = st.session_state.user['uid']
        collection_path = f'users/{user_id}/ingredients'
        
        # Dados completos para Firebase
        ingredient_data = ingredient.copy()
        ingredient_data['user_id'] = user_id
        ingredient_data['created_at'] = datetime.now().isoformat()
        
        st.info(f"📍 Salvando em: {collection_path}")
        st.info(f"📋 Item: {ingredient_data.get('nome', 'N/A')} - {ingredient_data.get('categoria', 'N/A')}")
        
        # Salvar no Firebase via REST API
        st.info(f"🔥 Chamando db.collection('{collection_path}').add()")
        result = db.collection(collection_path).add(ingredient_data)
        
        st.info(f"🔍 Result type: {type(result)}")
        st.info(f"🔍 Result value: {result}")
        
        if result:
            st.success(f"✅ Firebase: '{ingredient_data.get('nome', 'N/A')}' salvo com sucesso!")
            st.info(f"📄 Document ID: {result}")
            return True
        else:
            st.error("❌ Firebase: Falha na resposta (resultado vazio)")
            return False
            
    except Exception as e:
        st.error(f"❌ EXCEÇÃO no save Firebase: {str(e)}")
        
        # Mostrar stack trace completo para debug
        import traceback
        error_details = traceback.format_exc()
        st.code(f"Stack trace:\n{error_details}")
        
        return False

def clear_all_user_ingredients_from_firebase():
    """Remove todos os ingredientes do usuário do Firebase antes de upload"""
    try:
        if 'user' not in st.session_state:
            return False
            
        from utils.firestore_client import get_firestore_client
        import requests
        
        db = get_firestore_client()
        if db and 'token' in st.session_state.user:
            db.set_auth_token(st.session_state.user['token'])
            
            user_id = st.session_state.user['uid']
            collection_path = f'users/{user_id}/ingredients'
            
            # URL para listar documentos
            url = f"{db.base_url}/{collection_path}"
            response = requests.get(url, headers=db._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                if 'documents' in data:
                    # Deletar cada documento encontrado
                    deleted_count = 0
                    for doc in data['documents']:
                        doc_path = doc['name']  # Caminho completo do documento
                        delete_response = requests.delete(doc_path, headers=db._get_headers())
                        if delete_response.status_code in [200, 204]:
                            deleted_count += 1
                    
                    print(f"DEBUG: Removidos {deleted_count} ingredientes antigos do Firebase")
                    return True
            
    except Exception as e:
        print(f"DEBUG: Erro ao limpar ingredientes antigos: {e}")
        pass  # Não falhar o upload por causa disso
    
    return False

def save_embalagens_to_session(df):
    """Salva embalagens no session state (versão demo)"""
    try:
        if 'demo_embalagens' not in st.session_state:
            st.session_state.demo_embalagens = []
        
        success_count = 0
        
        for _, row in df.iterrows():
            embalagem_data = {
                'id': f"upload_emb_{len(st.session_state.demo_embalagens)}_{success_count}",
                'nome': str(row['Nome']).strip(),
                'tipo': str(row['Tipo']).strip(),
                'preco': float(row['Preco']),
                'capacidade_ml': int(row['Capacidade_ml']) if row['Capacidade_ml'] != 0 else 0,
                'categoria': str(row['Categoria']).strip(),
                'ativo': str(row['Ativo']).upper() == 'TRUE',
                'descricao': str(row.get('Descricao', '')).strip(),
                'source': 'upload_csv'
            }
            
            st.session_state.demo_embalagens.append(embalagem_data)
            success_count += 1
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro ao salvar embalagens: {str(e)}")
        return 0

def save_custos_to_session(df):
    """Salva custos fixos no session state (versão demo)"""
    try:
        if 'demo_custos_fixos' not in st.session_state:
            st.session_state.demo_custos_fixos = []
        
        success_count = 0
        
        for _, row in df.iterrows():
            custo_data = {
                'id': f"upload_custo_{len(st.session_state.demo_custos_fixos)}_{success_count}",
                'categoria': str(row['Categoria']).strip(),
                'item': str(row['Item']).strip(),
                'custo_mensal': float(row['Custo_Mensal']),
                'rateio_por_marmita': float(row['Rateio_por_Marmita']),
                'descricao': str(row.get('Descricao', '')).strip(),
                'source': 'upload_csv'
            }
            
            st.session_state.demo_custos_fixos.append(custo_data)
            success_count += 1
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro ao salvar custos fixos: {str(e)}")
        return 0

def save_receitas_to_session(df):
    """Salva receitas no session state (versão demo)"""
    try:
        if 'demo_recipes' not in st.session_state:
            st.session_state.demo_recipes = []
        
        success_count = 0
        
        for _, row in df.iterrows():
            # Converter JSON simplificado de ingredientes
            ingredientes_str = str(row['Ingredientes_JSON'])
            ingredientes_dict = parse_simple_json(ingredientes_str)
            
            receita_data = {
                'id': f"upload_receita_{len(st.session_state.demo_recipes)}_{success_count}",
                'nome': str(row['Nome']).strip(),
                'categoria': str(row['Categoria']).strip(),
                'ingredientes': ingredientes_dict,
                'porcoes': int(row['Porcoes']),
                'calorias_porcao': float(row['Calorias_Porcao']),
                'preco_custo': float(row['Preco_Custo']),
                'margem_lucro': float(row.get('Margem_Lucro', 40)),
                'preco_sugerido': float(row.get('Preco_Sugerido', 0)),
                'ativo': str(row['Ativo']).upper() == 'TRUE',
                'observacoes': str(row.get('Observacoes', '')).strip(),
                'source': 'upload_csv'
            }
            
            st.session_state.demo_recipes.append(receita_data)
            success_count += 1
        
        return success_count
        
    except Exception as e:
        st.error(f"Erro ao salvar receitas: {str(e)}")
        return 0

def parse_simple_json(json_str):
    """Parser simples para formato {"item":valor_"item2":valor}"""
    try:
        # Remover chaves
        content = json_str.strip('{}')
        
        # Separar por _
        pairs = content.split('_')
        
        result = {}
        for pair in pairs:
            if ':' in pair:
                # Separar por :
                parts = pair.split(':')
                if len(parts) >= 2:
                    key = parts[0].strip().strip('"')
                    value = float(parts[1].strip())
                    result[key] = value
        
        return result
        
    except Exception as e:
        return {}

def show_cleanup_tools():
    """Ferramentas de limpeza e manutenção dos dados"""
    
    st.header("🧹 Ferramentas de Limpeza")
    st.warning("⚠️ Use essas ferramentas para corrigir problemas de dados duplicados!")
    
    # Estatísticas atuais
    st.subheader("📊 Status Atual dos Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_ing = len(st.session_state.get('demo_ingredients', []))
        st.metric("🥕 Total Ingredientes", total_ing)
    
    with col2:
        total_rec = len(st.session_state.get('demo_recipes', []))
        st.metric("📝 Total Receitas", total_rec)
    
    with col3:
        total_emb = len(st.session_state.get('demo_embalagens', []))
        st.metric("📦 Total Embalagens", total_emb)
    
    # Análise de duplicatas
    st.subheader("🔍 Análise de Duplicatas")
    
    if st.session_state.get('demo_ingredients'):
        ingredientes = st.session_state.demo_ingredients
        
        # Contar por nome
        nomes = [ing.get('Nome', 'Sem nome') for ing in ingredientes]
        from collections import Counter
        contador_nomes = Counter(nomes)
        
        duplicatas = {nome: count for nome, count in contador_nomes.items() if count > 1}
        
        if duplicatas:
            st.warning(f"⚠️ Encontradas {len(duplicatas)} nomes duplicados:")
            
            for nome, count in list(duplicatas.items())[:10]:  # Mostrar apenas os primeiros 10
                st.write(f"- **{nome}**: {count} ocorrências")
            
            if len(duplicatas) > 10:
                st.write(f"... e mais {len(duplicatas) - 10} duplicatas")
        else:
            st.success("✅ Nenhuma duplicata encontrada por nome")
        
        # Análise de estrutura
        st.subheader("🔧 Análise de Estrutura")
        
        estruturas_diferentes = {}
        for i, ing in enumerate(ingredientes):
            chaves = tuple(sorted(ing.keys()))
            if chaves not in estruturas_diferentes:
                estruturas_diferentes[chaves] = []
            estruturas_diferentes[chaves].append(i)
        
        if len(estruturas_diferentes) > 1:
            st.warning(f"⚠️ Encontradas {len(estruturas_diferentes)} estruturas diferentes:")
            
            for i, (estrutura, indices) in enumerate(estruturas_diferentes.items()):
                st.write(f"**Estrutura {i+1}** ({len(indices)} ingredientes):")
                st.write(f"Campos: {list(estrutura)}")
                st.write(f"Primeiros ingredientes: {indices[:5]}")
        else:
            st.success("✅ Todos os ingredientes têm a mesma estrutura")
    
    # Ferramentas de limpeza
    st.subheader("🛠️ Ferramentas de Limpeza")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🥕 Ingredientes:**")
        
        if st.button("🗑️ Remover Duplicatas por Nome", key="remove_duplicates"):
            if st.session_state.get('demo_ingredients'):
                ingredientes_unicos = []
                nomes_vistos = set()
                
                for ing in st.session_state.demo_ingredients:
                    nome = ing.get('Nome', '')
                    if nome and nome not in nomes_vistos:
                        # Garantir estrutura correta
                        ingrediente_limpo = {
                            'Nome': nome,
                            'Categoria': ing.get('Categoria', 'Outros'),
                            'Unidade_Receita': ing.get('Unidade_Receita', 'g'),
                            'Unidade_Compra': ing.get('Unidade_Compra', 'kg'),
                            'Preco_Padrao': float(ing.get('Preco_Padrao', 0)),
                            'Kcal_Por_Unidade_Receita': float(ing.get('Kcal_Por_Unidade_Receita', 0)),
                            'Fator_Conversao': float(ing.get('Fator_Conversao', 1000))
                        }
                        ingredientes_unicos.append(ingrediente_limpo)
                        nomes_vistos.add(nome)
                
                st.session_state.demo_ingredients = ingredientes_unicos
                st.success(f"✅ Limpeza concluída! {len(ingredientes_unicos)} ingredientes únicos mantidos.")
                st.rerun()
        
        if st.button("🔄 Resetar Ingredientes", key="reset_ingredients"):
            st.session_state.demo_ingredients = [
                {'Nome': 'Frango (peito)', 'Categoria': 'Proteína Animal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 18.9, 'Kcal_Por_Unidade_Receita': 1.65, 'Fator_Conversao': 1000},
                {'Nome': 'Arroz integral', 'Categoria': 'Carboidrato', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 1.11, 'Fator_Conversao': 1000},
                {'Nome': 'Brócolis', 'Categoria': 'Vegetal', 'Unidade_Receita': 'g', 'Unidade_Compra': 'kg', 'Preco_Padrao': 8.9, 'Kcal_Por_Unidade_Receita': 0.34, 'Fator_Conversao': 1000},
            ]
            st.success("✅ Ingredientes resetados para os 3 iniciais!")
            st.rerun()
    
    with col2:
        st.write("**🧹 Geral:**")
        
        if st.button("🔄 Limpar Todos os Dados", key="reset_all"):
            st.session_state.demo_ingredients = []
            st.session_state.demo_recipes = []
            st.session_state.demo_embalagens = []
            st.session_state.demo_custos_fixos = []
            st.success("✅ Todos os dados foram limpos!")
            st.rerun()
        
        if st.button("🔧 Corrigir Estrutura dos Dados", key="fix_structure"):
            if st.session_state.get('demo_ingredients'):
                ingredientes_corrigidos = []
                
                for ing in st.session_state.demo_ingredients:
                    # Tentar extrair nome válido
                    nome = ing.get('Nome') or ing.get('nome') or ing.get('name') or 'Ingrediente sem nome'
                    
                    # Pular se nome for None, NaN ou vazio
                    if not nome or str(nome).lower() in ['none', 'nan', '']:
                        continue
                    
                    ingrediente_corrigido = {
                        'Nome': str(nome).strip(),
                        'Categoria': str(ing.get('Categoria') or ing.get('categoria') or 'Outros').strip(),
                        'Unidade_Receita': str(ing.get('Unidade_Receita') or ing.get('unid_receita') or 'g').strip(),
                        'Unidade_Compra': str(ing.get('Unidade_Compra') or ing.get('unid_compra') or 'kg').strip(),
                        'Preco_Padrao': float(ing.get('Preco_Padrao') or ing.get('preco') or 0),
                        'Kcal_Por_Unidade_Receita': float(ing.get('Kcal_Por_Unidade_Receita') or ing.get('kcal_unid') or 0),
                        'Fator_Conversao': float(ing.get('Fator_Conversao') or ing.get('fator_conv') or 1000)
                    }
                    ingredientes_corrigidos.append(ingrediente_corrigido)
                
                st.session_state.demo_ingredients = ingredientes_corrigidos
                st.success(f"✅ Estrutura corrigida! {len(ingredientes_corrigidos)} ingredientes válidos.")
                st.rerun()

def show_stats_safe():
    """Seção de estatísticas - versão segura"""
    
    st.header("📊 Estatísticas do Sistema")
    
    # Mock data para demonstração
    st.subheader("📈 Métricas de Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("👥 Total Usuários", "1.247", "12 novos")
        st.metric("💎 Assinantes Ativos", "1.189", "4.2%")
        st.metric("🍽️ Receitas Criadas", "15.632")
        st.metric("🏭 Produções Planejadas", "8.947")
    
    with col2:
        st.metric("💰 Receita Mensal", "R$ 2.958", "4.2%")
        st.metric("📈 Taxa Conversão", "95.3%", "2.1%")
        st.metric("🛒 Listas Geradas", "12.458")
        st.metric("📄 PDFs Baixados", "9.234")
    
    # Resumo do modelo de negócio
    st.markdown("---")
    st.subheader("💼 Modelo de Negócio")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **💰 Preço:**
        R$ 29,90/ano
        
        **🎯 Meta:**
        200k usuários
        
        **📈 Margem:**
        40% nos preços
        """)
    
    with col2:
        st.success("""
        **💵 Projeção:**
        R$ 5.98M/ano
        
        **👥 Conversão:**
        95% dos usuários
        
        **🔄 Renovação:**
        Anual automática
        """)
    
    with col3:
        st.warning("""
        **📊 Atualizações:**
        Preços mensais
        
        **🎁 Diferencial:**
        Sem versão gratuita
        
        **⚡ Foco:**
        Empreendedores sérios
        """)

# Função para incluir no menu principal
def show_admin_menu_item():
    """Mostra item de menu admin se usuário for administrador"""
    
    if 'user' in st.session_state:
        user_email = st.session_state.user.get('email', '')
        
        if is_admin(user_email):
            return True
    
    return False