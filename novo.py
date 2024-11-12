import pandas as pd
import streamlit as st  # Importando Streamlit para uso de st.error

def filtro_novo(base, coeficiente, banco, comissao, parcelas, comissao_min, margem_limite, vinculos_invalidos):
    # Verifica se a base está vazia
    if base.empty:
        st.error("Erro: A base está vazia.")
        return pd.DataFrame()
    
    # Limitando as colunas se necessário
    base = base.iloc[:, :23]
    
    # Formatando os dados
    if 'Nome_Cliente' in base.columns and base['Nome_Cliente'].notna().any():
        base['Nome_Cliente'] = base['Nome_Cliente'].apply(lambda x: x.title() if isinstance(x, str) else x)

    base['CPF'] = base['CPF'].str.replace(".", "", regex=False).str.replace("-", "", regex=False)

    # Adicionando informações do banco e parcelas
    base['banco'] = banco
    base['parcelas'] = parcelas

    # Filtrando os vínculos aceitos
    st.write(vinculos_invalidos)
    base = base.loc[~base['Vinculo_Servidor'].isin(vinculos_invalidos) | base['Vinculo_Servidor'].isnull()]
    
    # Aplicando condições específicas para diferentes convênios
    if 'Convenio' in base.columns:
        if base['Convenio'].str.contains('govsp', case=False, na=False).any():
            negativos = base.loc[base['MG_Emprestimo_Disponivel'] < 0, ['Matricula', 'Nome_Cliente', 'MG_Emprestimo_Disponivel']]
            base = base.loc[~base['Matricula'].isin(negativos['Matricula'])]
        elif base['Convenio'].str.contains('govmt', case=False, na=False).any():
            base = base.loc[base['MG_Compulsoria_Disponivel'] >= 0]

    # Cálculo do valor liberado e da comissão
    base['valor_liberado'] = (base['MG_Emprestimo_Disponivel'] * coeficiente).round(2)
    base['comissao'] = (base['valor_liberado'] * comissao).round(2)

    # Filtrando com base na margem limite e comissão mínima
    base = base.loc[base['MG_Emprestimo_Disponivel'] >= margem_limite]
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


def filtro_novo_govsp(base, coeficiente_sefaz, coeficiente_sefaz_educ, coeficiente_restante,
                       banco_sefaz, banco_sefaz_educ, banco_restante,
                       parcelas_sefaz, parcelas_sefaz_educ, parcelas_restante,
                       comissao, comissao_min, margem_limite, vinculos_invalidos):
    # Verifica se a base está vazia
    if base.empty:
        st.error("Erro: A base está vazia.")
        return pd.DataFrame()

    # Limitando as colunas se necessário
    base = base.iloc[:, :23]

    # Formatando os dados
    if 'Nome_Cliente' in base.columns and base['Nome_Cliente'].notna().any():
        base['Nome_Cliente'] = base['Nome_Cliente'].apply(lambda x: x.title() if isinstance(x, str) else x)
    base['CPF'] = base['CPF'].str.replace(".", "", regex=False).str.replace("-", "", regex=False)

    # Filtrando matrículas com empréstimos negativos
    negativos = base.loc[base['MG_Emprestimo_Disponivel'] < 0, ['Matricula', 'Nome_Cliente', 'MG_Emprestimo_Disponivel']]
    base = base.loc[~base['Matricula'].isin(negativos['Matricula'])]

    # Filtrando pela margem mínima disponível
    base = base.loc[base['MG_Emprestimo_Disponivel'] >= margem_limite]

    # Adicionando informações de banco e parcelas com base em condições específicas
    # Para SEFAZ, que não são da Educação
    base.loc[(base['Secretaria'] != '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "banco"] = banco_sefaz
    base.loc[(base['Secretaria'] != '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "parcelas"] = parcelas_sefaz
    base.loc[(base['Secretaria'] != '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "valor_liberado"] = (base['MG_Emprestimo_Disponivel'] * coeficiente_sefaz).round(2)

    # Para SEFAZ, que são da Educação
    base.loc[(base['Secretaria'] == '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "banco"] = banco_sefaz_educ
    base.loc[(base['Secretaria'] == '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "parcelas"] = parcelas_sefaz_educ
    base.loc[(base['Secretaria'] == '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "valor_liberado"] = (base['MG_Emprestimo_Disponivel'] * coeficiente_sefaz_educ).round(2)

    # Para lotações diferentes de SEFAZ
    base.loc[(base['Lotacao'] != 'SEFAZ'), "banco"] = banco_restante
    base.loc[(base['Lotacao'] != 'SEFAZ'), "parcelas"] = parcelas_restante
    base.loc[(base['Lotacao'] != 'SEFAZ'), "valor_liberado"] = (base['MG_Emprestimo_Disponivel'] * coeficiente_restante).round(2)

    # Convertendo tipos de dados
    base["banco"] = base["banco"].astype(int)
    base["parcelas"] = base["parcelas"].astype(int)

    # Filtrando por vínculos aceitos, removendo os inválidos
    base = base.loc[~(base['Vinculo_Servidor'].isin(vinculos_invalidos)) | (base['Vinculo_Servidor'].isnull())]

    # Ajustando o banco para vínculos específicos
    base.loc[base['Vinculo_Servidor'] == '8 - ESTAB. CONSTIT.', 'banco'] = 707

    # Ordenando a base por valor liberado e removendo duplicatas
    base = base.sort_values(by='valor_liberado', ascending=False).drop_duplicates(['CPF'])

    # Cálculo da comissão
    base['comissao'] = (base['valor_liberado'] * comissao).round(2)

    # Filtrando pela comissão mínima
    base = base.loc[base['comissao'] >= comissao_min]

    # Selecionando colunas relevantes para retorno
    colunas = [
        'Origem_Dado', 'Nome_Cliente', 'Matricula', 'CPF', 'Data_Nascimento',
        'MG_Emprestimo_Total', 'MG_Emprestimo_Disponivel', 'MG_Beneficio_Saque_Total',
        'MG_Beneficio_Saque_Disponivel', 'MG_Cartao_Total', 'MG_Cartao_Disponivel',
        'Convenio', 'Vinculo_Servidor', 'Lotacao', 'Secretaria',
        'valor_liberado', 'comissao', 'banco', 'parcelas'
    ]

    # Retornando a base filtrada
    return base.loc[:, colunas]  # Retorna o DataFrame filtrado
