import pandas as pd
import os

# Essa função aqui é pra carregar os dados de um CSV se ele existir
# Se não existir, eu retorno um DataFrame vazio com colunas indefinidas 
def carregar_dados(caminho):
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    else:
        return pd.DataFrame()

# Aqui eu salvo os dados no caminho especificado em CSV
# Sempre sobrescreve, mas posso mudar depois se quiser versionar
def salvar_dados(df, caminho):
    df.to_csv(caminho, index=False)
