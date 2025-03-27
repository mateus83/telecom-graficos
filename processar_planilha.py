# processar_planilha.py
import pandas as pd
import json

# Carregar a planilha do mesmo diretório (ou URL bruta do GitHub)
df = pd.read_excel('BaseES.xlsx')

# Converter colunas de data
df['Data Pedido'] = pd.to_datetime(df['Data Pedido'], errors='coerce')
df['Data Entregue'] = pd.to_datetime(df['Data Entregue'], errors='coerce')

# **Caixas Flutuantes com Totais**
totais = {
    'total_os': len(df),
    'os_em_andamento': df[~df['Fase'].isin(['FINALIZADO', 'FINALIZADO - CANCELADO'])].shape[0],
    'os_antes_construido': df[~df['Fase'].isin(['FINALIZADO', 'FINALIZADO - CANCELADO', 'CONSTRUÍDO'])].shape[0],
    'os_interrompida': df[df['Fase'] == 'INTERROMPIDO'].shape[0],
    'os_plano_emenda': df[df['Motivo Pendencia'] == 'EMBRATEL DOC - PLANO DE EMENDA'].shape[0],
    'os_carta_concessionaria': df[df['Motivo Pendencia'] == 'EMBRATEL DOC - CARTA CONCESSIONARIA'].shape[0]
}

# **Prazos**
df['Dias desde Cadastro'] = (pd.Timestamp.now() - df['Data Pedido']).dt.days
df_prazo = df[~df['Fase'].isin(['FINALIZADO', 'FINALIZADO - CANCELADO', 'CONSTRUÍDO'])]
prazos = {
    'prazo_30': df_prazo[df_prazo['Dias desde Cadastro'] <= 30].shape[0],
    'prazo_31_60': df_prazo[(df_prazo['Dias desde Cadastro'] > 30) & (df_prazo['Dias desde Cadastro'] <= 60)].shape[0],
    'prazo_61_90': df_prazo[(df_prazo['Dias desde Cadastro'] > 60) & (df_prazo['Dias desde Cadastro'] <= 90)].shape[0],
    'prazo_91_120': df_prazo[(df_prazo['Dias desde Cadastro'] > 90) & (df_prazo['Dias desde Cadastro'] <= 120)].shape[0],
    'prazo_acima_120': df_prazo[df_prazo['Dias desde Cadastro'] > 120].shape[0]
}

# **Em Execução por Fase**
fases = {
    'sem_fase': df[df['Fase'].isna()].shape[0],
    'em_projeto': df[df['Fase'] == 'PROJETO'].shape[0],
    'lancamento_cabo': df[df['Fase'] == 'LANÇAMENTO DE CABO'].shape[0],
    'fusao': df[df['Fase'] == 'FUSÃO'].shape[0]
}

# **Documentação**
documentacao = {
    'aguardando_doc': df[df['Fase'] == 'AGUARDANDO DOC'].shape[0],
    'cadastro_sagre': df[df['Fase'] == 'CADASTRO SAGRE'].shape[0],
    'validacao_asbuilt': df[df['Fase'] == 'VALIDAÇÃO AS-BUILT'].shape[0],
    'enviar_asbuilt': df[df['Fase'] == 'ENVIAR AS-BUILT'].shape[0]
}

# **Pedidos x Entregas**
df['Mes_Ano_Pedido'] = df['Data Pedido'].dt.to_period('M').astype(str)
df['Mes_Ano_Entrega'] = df['Data Entregue'].dt.to_period('M').astype(str)
pedidos_por_mes = df.groupby('Mes_Ano_Pedido').size().to_dict()
entregas_por_mes = df.groupby('Mes_Ano_Entrega').size().to_dict()

# Combinar todos os dados em um dicionário
data = {
    'totais': totais,
    'prazos': prazos,
    'fases': fases,
    'documentacao': documentacao,
    'pedidos_entregas': {'pedidos': pedidos_por_mes, 'entregas': entregas_por_mes}
}

# Salvar como JSON na pasta docs
with open('docs/data.json', 'w') as f:
    json.dump(data, f)
