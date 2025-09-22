import streamlit as st
import pandas as pd

# Tratamento
def tratar_coluna_data(df, nome_coluna, nome_fonte=""):
    if nome_coluna in df.columns:
        numericos = pd.to_numeric(df[nome_coluna], errors='coerce')
        datas_de_numeros = pd.to_datetime(numericos, origin='1899-12-30', unit='D', errors='coerce')
        datas_de_texto = pd.to_datetime(df[nome_coluna], errors='coerce', dayfirst=True)
        coluna_limpa = datas_de_texto.fillna(datas_de_numeros)
        df[nome_coluna] = coluna_limpa.dt.date
    else:
        st.warning(f"A coluna de data '{nome_coluna}' não foi encontrada na fonte '{nome_fonte}'.")
    return df

def limpar_e_converter_para_numero(coluna_df):
    if coluna_df is None:
        return pd.Series(dtype='float64')
    
    coluna_limpa = (
        coluna_df.astype(str)
                 .str.replace('R$', '', regex=False)
                 .str.replace('.', '', regex=False)    
                 .str.replace(',', '.', regex=False)    
                 .str.strip()
    )
    valores_numericos = pd.to_numeric(coluna_limpa, errors='coerce').fillna(0)
    return valores_numericos 

# FUNÇÕES DE CARREGAMENTO 
def initialize_session_state_kapthaleadmeta():
    if 'kapthalead_meta' not in st.session_state:
        df = pd.read_csv("Dados/Dados Meta Kaptha  - Dados.csv")
        
        
        df.columns = df.columns.str.strip()
        
        df = tratar_coluna_data(df, 'Data', nome_fonte="Kaptha Lead Meta")
        df['Investimento'] = limpar_e_converter_para_numero(df.get('Investimento'))
        df['Primeiro Contato'] = limpar_e_converter_para_numero(df.get('Primeiro Contato'))
        
        st.session_state['kapthalead_meta'] = df
        
def initialize_session_state_kapthaenterprisemeta():
    if 'kapthaenterprise_meta' not in st.session_state:
        df = pd.read_csv("Dados/Dados Meta Kaptha Enterprise  - Dados.csv")
        df.columns = df.columns.str.strip() 
        df = tratar_coluna_data(df, 'Data', nome_fonte="Kaptha Enterprise Meta")
        df['Investimento'] = limpar_e_converter_para_numero(df.get('Investimento'))
        df['Primeiro Contato'] = limpar_e_converter_para_numero(df.get('Primeiro Contato'))
        st.session_state['kapthaenterprise_meta'] = df
        
def initialize_session_state_kapthagoogle():
    if 'kaptha_google' not in st.session_state:
        df = pd.read_csv("Dados/Dados Google Kaptha - Dados.csv")
        df.columns = df.columns.str.strip() 
        df = tratar_coluna_data(df, 'Data', nome_fonte="Kaptha Google")
        df['Investimento'] = limpar_e_converter_para_numero(df.get('Investimento'))
        df['Primeiro Contato'] = limpar_e_converter_para_numero(df.get('Primeiro Contato'))
        st.session_state['kaptha_google'] = df
        
def initialize_session_state_sprinthub():
    if 'sprinthub' not in st.session_state:
        df = pd.read_csv("Dados/Dados Sprint Hub - Dados.csv")
        df.columns = df.columns.str.strip()
        df = tratar_coluna_data(df, 'data_movimentacao', nome_fonte="SprintHub")
        df['valor'] = limpar_e_converter_para_numero(df['valor'])
        st.session_state['sprinthub'] = df
    
def tratar_coluna_data(df, nome_coluna, nome_fonte=""):
    if nome_coluna in df.columns:
        numericos = pd.to_numeric(df[nome_coluna], errors='coerce')
        datas_de_numeros = pd.to_datetime(numericos, origin='1899-12-30', unit='D', errors='coerce')
        datas_de_texto = pd.to_datetime(df[nome_coluna], errors='coerce', dayfirst=True)
        coluna_limpa = datas_de_texto.fillna(datas_de_numeros)
        df[nome_coluna] = coluna_limpa.dt.date
    else:
        st.warning(f"A coluna de data '{nome_coluna}' não foi encontrada na fonte '{nome_fonte}'.")
    return df