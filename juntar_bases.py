import streamlit as st
import pandas as pd

# Função para juntar os arquivos carregados
def juntar_bases(files):
    dataframes = []
    for arquivo in files:
        try:
            df = pd.read_csv(arquivo, low_memory=False)
            if df.empty:
                st.warning(f"O arquivo {arquivo.name} está vazio.")
            else:
                dataframes.append(df)
        except pd.errors.EmptyDataError:
            st.error(f"O arquivo {arquivo.name} está vazio ou não contém dados.")
        except pd.errors.ParserError:
            st.error(f"Erro ao analisar o arquivo {arquivo.name}. Verifique o formato do arquivo.")
        except Exception as e:
            st.error(f"Erro ao carregar {arquivo.name}: {e}")
            continue  # Pula para o próximo arquivo
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        st.error("Nenhum arquivo válido foi carregado.")
        return pd.DataFrame()  # Retorna DataFrame vazio se nenhum arquivo for válido