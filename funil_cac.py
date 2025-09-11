import streamlit as st 
import pandas as pd 
import plotly.express as pe 
import numpy as np 
from datetime import datetime
from data_loader import(
    initialize_session_state_kapthaenterprisemeta,
    initialize_session_state_kapthagoogle,
    initialize_session_state_kapthaleadmeta,
    initialize_session_state_sprinthub
)

st.set_page_config(
    layout = "wide"
)

initialize_session_state_sprinthub()
initialize_session_state_kapthaleadmeta()
initialize_session_state_kapthaenterprisemeta()
initialize_session_state_kapthagoogle()

#Mapa Geral de Data
mapa_datas = {
    'kapthalead_meta': 'Data', 
    'kapthaenterprise_meta': 'Data',
    'kaptha_google': 'Data',
    'sprinthub' :'data_movimentacao'
}

#Mapas Métricas Google & Meta ADS
mapa_primeiro_contato = {
    'kapthalead_meta': 'Primeiro Contato', 
    'kapthaenterprise_meta': 'Primeiro Contato',
    'kaptha_google': 'Primeiro Contato'
}

mapa_investimento = {
    'kapthalead_meta': 'Investimento',
    'kapthaenterprise_meta': 'Investimento',
    'kaptha_google': 'Investimento',
}

#Mapas SprintHub
mapa_origem = {
    'sprinthub':'origem'
}



mapa_etapa = {
    'sprinthub':'etapa'
}

mapa_valor = {
    'sprinthub': 'valor'
}

lista_datas_minimas = []
lista_datas_maximas = []

for chave_data, coluna_data in mapa_datas.items():
    if chave_data in st.session_state:
        df = st.session_state[chave_data]
        if coluna_data in df.columns:
            # A linha de correção direta que resolveu o problema
            df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce', dayfirst=True).dt.date
            
            dados_validos = df[coluna_data].dropna()
            if not dados_validos.empty:
                lista_datas_minimas.append(dados_validos.min())
                lista_datas_maximas.append(dados_validos.max())

if lista_datas_minimas:
    data_minima_geral = min(lista_datas_minimas)
    data_maxima_geral = max(lista_datas_maximas)
else:
    st.warning("Nenhuma data válida encontrada para definir um período.")
    data_minima_geral = pd.to_datetime('today').date()
    data_maxima_geral = pd.to_datetime('today').date()

st.sidebar.header("Filtros de Data")
data_selecionada = st.sidebar.date_input(
    "Selecione o Período",
    value=(data_minima_geral, data_maxima_geral), 
    min_value=data_minima_geral,
    max_value=data_maxima_geral,
)

if len(data_selecionada) != 2:
    st.sidebar.warning("Por favor, selecione um intervalo de datas válido (início e fim).")
    st.stop() 

data_inicio, data_fim = data_selecionada

dfs_filtrados = {}

for chave, df_original in st.session_state.items():

    if chave in mapa_datas:
        coluna_data = mapa_datas[chave]
        df_original[coluna_data] = pd.to_datetime(df_original[coluna_data], errors='coerce').dt.date
        df_filtrado = df_original.query("@data_inicio <= `{0}` <= @data_fim".format(coluna_data))
        dfs_filtrados[chave] = df_filtrado
        
investimento_total = 0.0

for chave, coluna_investimento in mapa_investimento.items():
    if chave in dfs_filtrados:
        df_filtrado = dfs_filtrados[chave]
        if coluna_investimento in df_filtrado.columns:
            valores = pd.to_numeric(df_filtrado[coluna_investimento], errors='coerce')
            investimento_total += valores.sum()

total_primeiros_contatos = 0

for chave, coluna_contato in mapa_primeiro_contato.items():
    if chave in dfs_filtrados:
        df_filtrado = dfs_filtrados[chave]
    
        if coluna_contato in df_filtrado.columns:
            valores = pd.to_numeric(df_filtrado[coluna_contato], errors='coerce').fillna(0)
            total_primeiros_contatos += valores.sum()

reunioes_agendadas_inbound = 0

if 'sprinthub' in dfs_filtrados:
    df_sprint_filtrado = dfs_filtrados['sprinthub']

    coluna_etapa = mapa_etapa['sprinthub']
    coluna_origem = mapa_origem['sprinthub']
    
 
    if coluna_etapa in df_sprint_filtrado.columns and coluna_origem in df_sprint_filtrado.columns:
        condicao_etapa = (df_sprint_filtrado[coluna_etapa] == 'Reunião Agendada')
        condicao_origem = (df_sprint_filtrado[coluna_origem] == 'Inbound')
        reunioes_agendadas_inbound = df_sprint_filtrado[condicao_etapa & condicao_origem].shape[0]

if 'sprinthub' in dfs_filtrados:
    df_sprint_filtrado = dfs_filtrados['sprinthub']
    
    coluna_etapa = mapa_etapa['sprinthub']
    coluna_origem = mapa_origem['sprinthub']
    if coluna_etapa in df_sprint_filtrado.columns and coluna_origem in df_sprint_filtrado.columns:
        condicao_etapa = (df_sprint_filtrado[coluna_etapa] == 'Proposta Apresentada')
        condicao_origem = (df_sprint_filtrado[coluna_origem] == 'Inbound')
        propostas_apresentadas_inbound = df_sprint_filtrado[condicao_etapa & condicao_origem].shape[0]

contratos_assinados_inbound = 0

if 'sprinthub' in dfs_filtrados:
    df_sprint_filtrado = dfs_filtrados['sprinthub']
    
    coluna_etapa = mapa_etapa['sprinthub']
    coluna_origem = mapa_origem['sprinthub']
    if coluna_etapa in df_sprint_filtrado.columns and coluna_origem in df_sprint_filtrado.columns:
        condicao_etapa = (df_sprint_filtrado[coluna_etapa] == 'Contrato Assinado')
        condicao_origem = (df_sprint_filtrado[coluna_origem] == 'Inbound')
        contratos_assinados_inbound = df_sprint_filtrado[condicao_etapa & condicao_origem].shape[0]
        
valor_reunioes_inbound = 0.0

if 'sprinthub' in dfs_filtrados:
    df_sprint_filtrado = dfs_filtrados['sprinthub']
    
    coluna_etapa = mapa_etapa['sprinthub']
    coluna_origem = mapa_origem['sprinthub']
    coluna_valor = mapa_valor['sprinthub']

    if all(col in df_sprint_filtrado.columns for col in [coluna_etapa, coluna_origem, coluna_valor]):     
        condicao_etapa = (df_sprint_filtrado[coluna_etapa] == 'Reunião Agendada')
        condicao_origem = (df_sprint_filtrado[coluna_origem] == 'Inbound')
        valor_reunioes_inbound = df_sprint_filtrado[condicao_etapa & condicao_origem][coluna_valor].sum()

valor_propostas_inbound = 0.0

if 'sprinthub' in dfs_filtrados:
    df_sprint_filtrado = dfs_filtrados['sprinthub']
    coluna_etapa = mapa_etapa['sprinthub']
    coluna_origem = mapa_origem['sprinthub']
    coluna_valor = mapa_valor['sprinthub']

    if all(col in df_sprint_filtrado.columns for col in [coluna_etapa, coluna_origem, coluna_valor]):
        condicao_etapa = (df_sprint_filtrado[coluna_etapa] == 'Proposta Apresentada')
        condicao_origem = (df_sprint_filtrado[coluna_origem] == 'Inbound')
        
        valor_propostas_inbound = df_sprint_filtrado[condicao_etapa & condicao_origem][coluna_valor].sum()

if total_primeiros_contatos > 0:
    cpl_inbound = investimento_total / total_primeiros_contatos
else:
    cpl_inbound = 0

if reunioes_agendadas_inbound > 0:
    cpra_inbound = investimento_total / reunioes_agendadas_inbound
else:
    cpra_inbound = 0

if propostas_apresentadas_inbound > 0:
    cppa_inbound = investimento_total / propostas_apresentadas_inbound
else:
    cppa_inbound = 0
    
if contratos_assinados_inbound > 0:
    cac_inbound = investimento_total / contratos_assinados_inbound
else:
    cac_inbound = 0

resultados_cadencia = {
    'Contatos': 0.0,
    'Reuniões': 0.0,
    'Propostas': 0.0,
    'Contratos': 0.0
}

df_contatos_unificado = None
lista_dfs_contato = []
fontes_anuncio = ['kapthalead_meta', 'kapthaenterprise_meta', 'kaptha_google']
for chave in fontes_anuncio:
    if chave in dfs_filtrados:
        df_anuncio = dfs_filtrados[chave]
        coluna_data = mapa_datas[chave]
        coluna_contato = mapa_primeiro_contato[chave]
        if coluna_data in df_anuncio.columns and coluna_contato in df_anuncio.columns:
            lista_dfs_contato.append(df_anuncio[[coluna_data, coluna_contato]])
if lista_dfs_contato:
    df_contatos_unificado = pd.concat(lista_dfs_contato)
    df_contatos_unificado.columns = ['Data', 'Primeiro Contato']
    df_contatos_unificado['Primeiro Contato'] = pd.to_numeric(df_contatos_unificado['Primeiro Contato'], errors='coerce').fillna(0)
    df_contatos_unificado['Data'] = pd.to_datetime(df_contatos_unificado['Data'], errors='coerce')
    df_contatos_unificado.dropna(subset=['Data'], inplace=True)

df_sprint_inbound = None
if 'sprinthub' in dfs_filtrados:
    df_sprint = dfs_filtrados['sprinthub'].copy()
    col_etapa = mapa_etapa['sprinthub']
    col_origem = mapa_origem['sprinthub']
    col_data_mov = 'data_movimentacao'
    if all(c in df_sprint.columns for c in [col_etapa, col_origem, col_data_mov]):
        df_sprint[col_data_mov] = pd.to_datetime(df_sprint[col_data_mov], errors='coerce')
        df_sprint_inbound = df_sprint[df_sprint[col_origem] == 'Inbound'].dropna(subset=[col_data_mov])

etapas_para_calcular = {
    'Contatos': {'fonte': df_contatos_unificado, 'col_data': 'Data', 'col_eventos': 'Primeiro Contato'},
    'Reuniões': {'fonte': df_sprint_inbound, 'col_data': 'data_movimentacao', 'filtro_etapa': 'Reunião Agendada'},
    'Propostas': {'fonte': df_sprint_inbound, 'col_data': 'data_movimentacao', 'filtro_etapa': 'Proposta Apresentada'},
    'Contratos': {'fonte': df_sprint_inbound, 'col_data': 'data_movimentacao', 'filtro_etapa': 'Contrato Assinado'}
}

for nome_metrica, config in etapas_para_calcular.items():
    df_fonte = config['fonte']
    
    if df_fonte is not None and not df_fonte.empty:
        df_etapa = df_fonte
        
        if 'filtro_etapa' in config:
            df_etapa = df_fonte[df_fonte[mapa_etapa['sprinthub']] == config['filtro_etapa']]
        
        if nome_metrica == 'Contatos':
            num_eventos = df_etapa[config['col_eventos']].sum()
        else:
            num_eventos = len(df_etapa)
            
        if num_eventos > 1:
            data_inicio = df_etapa[config['col_data']].min()
            data_fim = df_etapa[config['col_data']].max()
            intervalo_total_dias = (data_fim - data_inicio).days
            
            if intervalo_total_dias > 0:
                resultados_cadencia[nome_metrica] = intervalo_total_dias / (num_eventos - 1)

soma_das_cadencias = sum(resultados_cadencia.values())

st.title("Análise de Funil CAC 📊")
lista_dfs_investimento = []
fontes_anuncio = ['kapthalead_meta', 'kapthaenterprise_meta', 'kaptha_google']
for chave in st.session_state: # Itera sobre todas as chaves carregadas
    if chave in fontes_anuncio:
        df_original = st.session_state[chave]
        if 'Data' in df_original.columns and 'Investimento' in df_original.columns:
            lista_dfs_investimento.append(df_original[['Data', 'Investimento']])

investimento_diario = pd.Series(dtype='float64')
if lista_dfs_investimento:
    df_investimento_historico = pd.concat(lista_dfs_investimento)
    df_investimento_historico['Data'] = pd.to_datetime(df_investimento_historico['Data'], errors='coerce')
    df_investimento_historico.dropna(subset=['Data'], inplace=True)
    investimento_diario = df_investimento_historico.groupby('Data')['Investimento'].sum().sort_index()
    
investimento_anterior = 0.0
delta_str = "—" 
delta_color = "#aab0b6"

# 1. Define as datas do período anterior (sem a necessidade de 'duracao_periodo')
data_fim_anterior = data_inicio - pd.Timedelta(days=1)
data_inicio_anterior = data_fim_anterior - pd.Timedelta(days=30) # Comparando com 30 dias fixos

# --- CORREÇÃO APLICADA AQUI ---
# Converte as datas para o tipo Timestamp do Pandas para garantir a compatibilidade
data_inicio_anterior_ts = pd.Timestamp(data_inicio_anterior)
data_fim_anterior_ts = pd.Timestamp(data_fim_anterior)
# --------------------------------

# Recalcula o investimento para o período anterior
for chave, df_original in st.session_state.items():
    if chave in mapa_investimento:
        coluna_data = mapa_datas[chave]
        coluna_investimento = mapa_investimento[chave]
        
        if coluna_data in df_original.columns and coluna_investimento in df_original.columns:
            # Garante que a coluna de data no DF também seja do tipo datetime completo
            df_original[coluna_data] = pd.to_datetime(df_original[coluna_data], errors='coerce')
            
            # Usa as novas variáveis Timestamp na query
            df_periodo_anterior = df_original.query(
                "@data_inicio_anterior_ts <= `{0}` <= @data_fim_anterior_ts".format(coluna_data)
            )
            investimento_anterior += df_periodo_anterior[coluna_investimento].sum()

if investimento_anterior > 0:
    mudanca_percentual = ((investimento_total - investimento_anterior) / investimento_anterior)
    delta_str = f"{mudanca_percentual:+.1%}" # Formato de porcentagem com sinal
elif investimento_total > 0:
    delta_str = "Novo"


st.subheader("Performance de Investimento")
with st.container(border=True):
    col_metrica, col_delta, col_sparkline = st.columns([3,3,3])

    with col_metrica:
        st.metric(
            label="Investimento Total no Período",
            value=f"R$ {investimento_total:,.2f}"
        )

    with col_sparkline:
        
        st.write("Investimento no Tempo")
        if not investimento_diario.empty:
            fig_sparkline = pe.line(
                x=investimento_diario.index,
                y=investimento_diario.values,
                
            )
            fig_sparkline.update_layout(
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=100
            )
            fig_sparkline.update_traces(line=dict(color='#0583F2', width=3))
            st.plotly_chart(fig_sparkline, use_container_width=True)
    
with col_delta:
    st.metric(
        label="Comparação com Período Anterior:",
        value=delta_str,
        delta=delta_str
    )

st.markdown("---") 
st.subheader("Funil de Etapas")

df_cadencia = pd.DataFrame(resultados_cadencia.items(), columns=['Etapa', 'Dias'])

ordem_etapas = ['Contatos', 'Reuniões', 'Propostas', 'Contratos']
df_cadencia['Etapa'] = pd.Categorical(df_cadencia['Etapa'], categories=ordem_etapas, ordered=True)
df_cadencia = df_cadencia.sort_values('Etapa')

df_cadencia = pd.DataFrame(resultados_cadencia.items(), columns=['Etapa', 'Dias'])
ordem_etapas = ['Contatos', 'Reuniões', 'Propostas', 'Contratos']
df_cadencia['Etapa'] = pd.Categorical(df_cadencia['Etapa'], categories=ordem_etapas, ordered=True)
df_cadencia = df_cadencia.sort_values('Etapa')

data_funil = {
    'Etapa': ['Contatos', 'Reuniões', 'Propostas', 'Contratos'],
    'Quantidade': [total_primeiros_contatos, reunioes_agendadas_inbound, propostas_apresentadas_inbound, contratos_assinados_inbound]
}
df_funil = pd.DataFrame(data_funil)

mapa_de_cores = { 
    'Contatos': '#020659',
    'Reuniões': '#031CA6',
    'Propostas': '#0540F2',
    'Contratos': '#0583F2'
}

col1, col2, col3 = st.columns(3)

with col1:
    if soma_das_cadencias > 0:
        df_cadencia['Porcentagem'] = (df_cadencia['Dias'] / soma_das_cadencias) * 100
    else:
        df_cadencia['Porcentagem'] = 0
    
    titulo_grafico = f"Ciclo Médio ({soma_das_cadencias:.1f} Dias)<br><sub>Tempo por etapas.</sub>"
    
    fig = pe.bar(
        df_cadencia,
        x='Dias',
        y='Etapa',
        orientation='h',
        title=titulo_grafico,
        color='Etapa',
        color_discrete_map=mapa_de_cores,
        custom_data=['Dias', 'Porcentagem']
    )

    fig.update_layout(
        yaxis=dict(categoryorder='array', categoryarray=['Contratos', 'Propostas', 'Reuniões', 'Contatos']),
        yaxis_title=None,
        xaxis_title="Duração Média (Dias)",
        showlegend=False,
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="white"
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(showticklabels=True) 

    fig.update_traces(
        texttemplate='%{x:.1f}d (%{customdata[1]:.0f}%)',
        textposition='inside'
    )
    
    for trace in fig.data:
        if trace.name == 'Propostas' and 'Contratos':
            trace.textposition = 'outside'

    st.plotly_chart(fig, use_container_width=True)
with col2:
    data_funil = {
        'Etapa': ['Contatos', 'Reuniões', 'Propostas', 'Contratos'],
        'Quantidade': [total_primeiros_contatos, reunioes_agendadas_inbound, propostas_apresentadas_inbound, contratos_assinados_inbound]
    }
    df_funil = pd.DataFrame(data_funil)
    
    titulo_funil = f"Funil de Conversão<br><sub>Investimento Total: R$ {investimento_total:,.2f}</sub>"

    fig_funil = pe.funnel(df_funil, x='Quantidade', y='Etapa', title=titulo_funil,
                          color='Etapa', color_discrete_map=mapa_de_cores)
    
    fig_funil.update_layout(
        showlegend=False,
        font=dict(family="Arial", size=14, color="white"),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',yaxis_title=None,

    )
    
    fig_funil.update_yaxes(
        categoryorder='array', 
        categoryarray=['Contatos', 'Reuniões', 'Propostas', 'Contratos'],
        showticklabels=False  
    )
    
    fig_funil.update_traces(textinfo='label+value', 
                            textfont_color='white',
                            textposition='inside')
    
    fig_funil.update_traces(
        texttemplate='R$ %{x:,.2f}',
        textposition='outside' # <-- ALTERADO DE 'inside' PARA 'outside'
    )
    
    for trace in fig_funil.data:
        # Se o nome da barra for 'Contratos', mudamos a posição do texto SÓ DELA para 'inside'
        if trace.name == 'Contatos':
            trace.textposition = 'inside'
    
    st.plotly_chart(fig_funil, use_container_width=True)
with col3:
    # --- Preparação dos dados (continua o mesmo) ---
    data_custo = {
        'Etapa': ['Contatos', 'Reuniões', 'Propostas', 'Contratos'],
        'Custo': [cpl_inbound, cpra_inbound, cppa_inbound, cac_inbound]
    }
    df_custo = pd.DataFrame(data_custo)

    # --- Criação do Gráfico (continua o mesmo) ---
    titulo_custo = "Custo por Etapa do Funil<br><sub>CAC e custos intermediários</sub>"
    fig_custo = pe.bar(
        df_custo, x='Custo', y='Etapa', orientation='h',
        title=titulo_custo, text='Custo', color='Etapa',
        color_discrete_map=mapa_de_cores
    )

    # --- Refinamentos do Layout do Gráfico ---
    fig_custo.update_layout(
        yaxis_title=None,
        xaxis_title="Custo Médio (R$)",
        showlegend=False,
        font=dict(family="Arial", size=14, color="white"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # --- MUDANÇA 1: INVERTE A DIREÇÃO DAS BARRAS (direita para esquerda) ---
    fig_custo.update_xaxes(autorange="reversed")

    # --- MUDANÇA 2: MOVE O EIXO Y PARA A DIREITA ---
    # (E mantém a ordem das categorias que já tínhamos, com Contatos no topo)
    fig_custo.update_yaxes(
        side='right',
        categoryorder='array',
        categoryarray=['Contratos', 'Propostas', 'Reuniões', 'Contatos']
    )
    
    
    fig_custo.update_traces(
        texttemplate='R$ %{x:,.2f}',
        textposition='outside'
    )

    # Etapa 2: Iteramos por cada barra (trace) do gráfico para encontrar a que queremos mudar
    for trace in fig_custo.data:
        # Se o nome da barra for 'Contratos', mudamos a posição do texto SÓ DELA para 'inside'
        if trace.name == 'Contratos':
            trace.textposition = 'inside'

    # --- Exibição do Gráfico no Streamlit ---
    st.plotly_chart(fig_custo, use_container_width=True)
    
col1, col2, col3, col4 , col5, col6= st.columns(6)

with col3:
    st.metric(
        label = "Orçamento em Reuniões Agendadas:",
        value = f"{valor_reunioes_inbound:,.2f}",
        border=True
    )
    
with col4:
    st.metric(
        label="Orçamento em Propostas Pendentes:",
        value = f"{valor_propostas_inbound:,.2f}",
        border=True
    )