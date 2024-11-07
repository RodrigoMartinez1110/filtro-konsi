import pandas as pd
import streamlit as st  # Importando Streamlit para uso de st.error

def filtro_beneficio(base, coeficiente, banco, comissao, parcelas, comissao_min, margem_limite, vinculos_invalidos):
    # Verifica se a base está vazia
    if base.empty:
        st.error("Erro: A base está vazia.")
        return pd.DataFrame()
    
    # Limitando as colunas se necessário
    base = base.iloc[:, :23]
    
    # Adicionando informações do banco e parcelas
    base['banco'] = banco
    base['parcelas'] = parcelas
    
    # Formatando os dados
    base['Nome_Cliente'] = base['Nome_Cliente'].apply(lambda x: x.title())
    base['CPF'] = base['CPF'].str.replace(".", "", regex=False).str.replace("-", "", regex=False)

    # Filtrando registros com MG_Emprestimo_Disponivel abaixo da margem limite
    base = base.loc[base['MG_Emprestimo_Disponivel'] < margem_limite]

    # Filtrando registros com MG_Beneficio_Total igual a MG_Beneficio_livre
    base = base.loc[base['MG_Beneficio_Saque_Disponivel'] == base['MG_Beneficio_Saque_Total']]

    # Filtrando os vínculos aceitos
    base = base.loc[~base['Vinculo_Servidor'].isin(vinculos_invalidos) | base['Vinculo_Servidor'].isnull()]

    # Cálculo do valor liberado
    base['valor_liberado'] = (base['MG_Beneficio_Saque_Disponivel'] * coeficiente).round(2)
    
    # Cálculo da comissão
    base['comissao'] = (base['valor_liberado'] * comissao).round(2)

    # Filtrando com base na comissão mínima
    base = base.loc[base['comissao'] >= comissao_min]

    # Ordenando e removendo duplicatas
    base = base.sort_values(by='valor_liberado', ascending=False)
    base = base.drop_duplicates(subset='CPF')

    # Selecionando colunas relevantes
    colunas = [
        'Origem_Dado', 'Nome_Cliente', 'Matricula', 'CPF', 'Data_Nascimento',
        'MG_Emprestimo_Total', 'MG_Emprestimo_Disponivel', 'MG_Beneficio_Saque_Total',
        'MG_Beneficio_Saque_Disponivel', 'MG_Cartao_Total', 'MG_Cartao_Disponivel',
        'Convenio', 'Vinculo_Servidor', 'Lotacao', 'Secretaria',
        'valor_liberado', 'comissao', 'banco', 'parcelas'
    ]

    base = base[colunas]

    return base  # Retorna o DataFrame filtrado
