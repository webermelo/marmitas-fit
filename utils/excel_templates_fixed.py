# -*- coding: utf-8 -*-
"""
Gerador de Templates Excel para Marmitas Fit - VERSÃO CORRIGIDA
Templates para ingredientes, embalagens e custos fixos
"""

import pandas as pd
from io import BytesIO

def create_ingredientes_template():
    """Cria template para ingredientes"""
    
    data = [
        {
            'Nome': 'Frango (peito)',
            'Categoria': 'Proteína Animal',
            'Preço (R$)': 18.90,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 1.65,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Sem pele, congelado'
        },
        {
            'Nome': 'Arroz integral',
            'Categoria': 'Carboidrato',
            'Preço (R$)': 8.90,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 1.11,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Grão longo, tipo 1'
        },
        {
            'Nome': 'Brócolis',
            'Categoria': 'Vegetal',
            'Preço (R$)': 6.50,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 0.34,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Fresco, preço médio'
        },
        {
            'Nome': 'Azeite extra virgem',
            'Categoria': 'Gordura',
            'Preço (R$)': 12.00,
            'Unid.Receita': 'ml',
            'Unid.Compra': 'L',
            'Kcal/Unid': 8.84,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Primeira prensagem'
        },
        {
            'Nome': 'Sal refinado',
            'Categoria': 'Tempero',
            'Preço (R$)': 1.20,
            'Unid.Receita': 'g',
            'Unid.Compra': 'kg',
            'Kcal/Unid': 0.00,
            'Fator Conv.': 1000,
            'Ativo': True,
            'Observações': 'Iodado'
        }
    ]
    
    return create_excel_from_data(
        data, 
        "Template Ingredientes - Marmitas Fit",
        "Preencha com os ingredientes disponíveis no mercado"
    )

def create_embalagens_template():
    """Cria template para embalagens"""
    
    data = [
        {
            'Nome': 'Marmita 500ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.50,
            'Capacidade (ml)': 500,
            'Categoria': 'principal',
            'Ativo': True,
            'Descrição': 'PP transparente com tampa'
        },
        {
            'Nome': 'Marmita 750ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.65,
            'Capacidade (ml)': 750,
            'Categoria': 'principal',
            'Ativo': True,
            'Descrição': 'PP transparente com tampa'
        },
        {
            'Nome': 'Marmita 1000ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.80,
            'Capacidade (ml)': 1000,
            'Categoria': 'principal',
            'Ativo': True,
            'Descrição': 'PP transparente com tampa'
        },
        {
            'Nome': 'Pote sobremesa 150ml',
            'Tipo': 'descartavel',
            'Preço (R$)': 0.25,
            'Capacidade (ml)': 150,
            'Categoria': 'complemento',
            'Ativo': True,
            'Descrição': 'Para doces e frutas'
        },
        {
            'Nome': 'Talher plástico',
            'Tipo': 'utensilio',
            'Preço (R$)': 0.08,
            'Capacidade (ml)': 0,
            'Categoria': 'utensilio',
            'Ativo': True,
            'Descrição': 'Garfo + faca + colher'
        },
        {
            'Nome': 'Guardanapo',
            'Tipo': 'higiene',
            'Preço (R$)': 0.05,
            'Capacidade (ml)': 0,
            'Categoria': 'higiene',
            'Ativo': True,
            'Descrição': 'Papel 20x20cm'
        },
        {
            'Nome': 'Sacola plástica',
            'Tipo': 'transporte',
            'Preço (R$)': 0.12,
            'Capacidade (ml)': 0,
            'Categoria': 'transporte',
            'Ativo': True,
            'Descrição': '30x40cm alça camiseta'
        }
    ]
    
    return create_excel_from_data(
        data,
        "Template Embalagens - Marmitas Fit",
        "Defina os custos das embalagens utilizadas"
    )

def create_custos_fixos_template():
    """Cria template para custos fixos"""
    
    data = [
        {
            'Categoria': 'Energia',
            'Item': 'Conta de luz',
            'Custo Mensal (R$)': 150.00,
            'Rateio por Marmita': 0.30,
            'Descrição': 'Fogão, geladeira, freezer'
        },
        {
            'Categoria': 'Gás',
            'Item': 'Botijão 13kg',
            'Custo Mensal (R$)': 80.00,
            'Rateio por Marmita': 0.16,
            'Descrição': 'Consumo médio mensal'
        },
        {
            'Categoria': 'Água',
            'Item': 'Conta de água',
            'Custo Mensal (R$)': 60.00,
            'Rateio por Marmita': 0.12,
            'Descrição': 'Limpeza e preparo'
        },
        {
            'Categoria': 'Aluguel',
            'Item': 'Espaço cozinha',
            'Custo Mensal (R$)': 800.00,
            'Rateio por Marmita': 1.60,
            'Descrição': 'Proporcional ao uso'
        },
        {
            'Categoria': 'Mão de obra',
            'Item': 'Salário próprio',
            'Custo Mensal (R$)': 2000.00,
            'Rateio por Marmita': 4.00,
            'Descrição': 'Base: 500 marmitas/mês'
        },
        {
            'Categoria': 'TOTAL',
            'Item': '',
            'Custo Mensal (R$)': 3090.00,
            'Rateio por Marmita': 6.18,
            'Descrição': 'Base: 500 marmitas/mês'
        }
    ]
    
    return create_excel_from_data(
        data,
        "Template Custos Fixos - Marmitas Fit",
        "Calcule seus custos fixos mensais por marmita"
    )

def create_excel_from_data(data, title, subtitle):
    """Cria arquivo Excel simples a partir dos dados"""
    
    # Converter para DataFrame
    df = pd.DataFrame(data)
    
    # Criar buffer
    buffer = BytesIO()
    
    # Usar pandas para criar Excel básico (sem formatação complexa)
    df.to_excel(buffer, sheet_name='Template', index=False)
    
    buffer.seek(0)
    return buffer.getvalue()

# Funções para uso no Streamlit
def generate_ingredientes_template():
    """Gera template de ingredientes para download"""
    return create_ingredientes_template()

def generate_embalagens_template():
    """Gera template de embalagens para download"""
    return create_embalagens_template()

def generate_custos_fixos_template():
    """Gera template de custos fixos para download"""
    return create_custos_fixos_template()