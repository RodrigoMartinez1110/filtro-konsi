import pandas as pd
import streamlit as st  # Importando Streamlit para uso de st.error

def filtro_novo(base, coeficiente, banco, comissao, parcelas, comissao_min, margem_limite, vinculos_invalidos):
    # Verifica se a base está vazia
    if base.empty:
        st.error("Erro: A base está vazia.")
        return pd.DataFrame()
    
    
    
    # Formatando os dados
    if 'Nome_Cliente' in base.columns and base['Nome_Cliente'].notna().any():
        base['Nome_Cliente'] = base['Nome_Cliente'].apply(lambda x: x.title() if isinstance(x, str) else x)

    base['CPF'] = base['CPF'].str.replace(".", "", regex=False).str.replace("-", "", regex=False)

    # Adicionando informações do banco e parcelas
    base['banco_emprestimo'] = banco
    base['prazo_emprestimo'] = parcelas

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

    # Limitando as colunas se necessário
    base = base.iloc[:, :23]

    # Cálculo do valor liberado e da comissão
    base['valor_liberado_emprestimo'] = (base['MG_Emprestimo_Disponivel'] * coeficiente).round(2)
    base['comissao_emprestimo'] = (base['valor_liberado_emprestimo'] * comissao).round(2)

    # Filtrando com base na margem limite e comissão mínima
    base = base.loc[base['MG_Emprestimo_Disponivel'] >= margem_limite]
    base = base.loc[base['comissao_emprestimo'] >= comissao_min]

    # Ordenando e removendo duplicatas
    base = base.sort_values(by='valor_liberado_emprestimo', ascending=False)
    base = base.drop_duplicates(subset='CPF')

    # Selecionando colunas relevantes
    base['FONE1'] = ""
    base['FONE2'] = ""
    base['FONE3'] = ""
    base['FONE4'] = ""

    base['valor_liberado_beneficio'] = ""
    base['valor_liberado_cartao'] = ""

    base['comissao_beneficio'] = ""
    base['comissao_cartao'] = ""

    base['valor_parcela_emprestimo'] = ""
    base['valor_parcela_beneficio'] = ""
    base['valor_parcela_cartao'] = ""

    base['banco_beneficio'] = ""
    base['banco_cartao'] = ""

    base['prazo_beneficio'] = ""
    base['prazo_cartao'] = ""

    base['Campanha'] = ''

    colunas = [
        'Origem_Dado', 'Nome_Cliente', 'Matricula', 'CPF', 'Data_Nascimento',
        'MG_Emprestimo_Total', 'MG_Emprestimo_Disponivel',
        'MG_Beneficio_Saque_Total', 'MG_Beneficio_Saque_Disponivel',
        'MG_Cartao_Total', 'MG_Cartao_Disponivel',
        'Convenio', 'Vinculo_Servidor', 'Lotacao', 'Secretaria',
        'FONE1', 'FONE2', 'FONE3', 'FONE4',
        'valor_liberado_emprestimo', 'valor_liberado_beneficio', 'valor_liberado_cartao',
        'comissao_emprestimo', 'comissao_beneficio', 'comissao_cartao',
        'valor_parcela_emprestimo', 'valor_parcela_beneficio', 'valor_parcela_cartao',
        'banco_emprestimo', 'banco_beneficio', 'banco_cartao',
        'prazo_emprestimo', 'prazo_beneficio', 'prazo_cartao',
        'Campanha'
    ]

    base = base[colunas]

    mapeamento = {
        'Origem_Dado': 'ORIGEM DO DADO',
        'MG_Emprestimo_Total': 'Mg_Emprestimo_Total',
        'MG_Emprestimo_Disponivel': 'Mg_Emprestimo_Disponivel',
        'MG_Beneficio_Saque_Total': 'Mg_Beneficio_Saque_Total',
        'MG_Beneficio_Saque_Disponivel': 'Mg_Beneficio_Saque_Disponivel',
        'MG_Cartao_Total': 'Mg_Cartao_Total',
        'MG_Cartao_Disponivel': 'Mg_Cartao_Disponivel',
        'campanha': 'Campanha'
    }

    # Renomear as colunas
    base.rename(columns=mapeamento, inplace=True)
    st.write(base.shape)

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
    base = base.sort_values(by='MG_Emprestimo_Disponivel', ascending=True)
    base = base.loc[~base['Matricula'].isin(negativos['Matricula'])]

    # Filtrando pela margem mínima disponível
    base = base.loc[base['MG_Emprestimo_Disponivel'] >= margem_limite]

    # Adicionando informações de banco e parcelas com base em condições específicas
    # Para SEFAZ, que não são da Educação
    base.loc[(base['Secretaria'] != '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "banco_emprestimo"] = banco_sefaz
    base.loc[(base['Secretaria'] != '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "prazo_emprestimo"] = parcelas_sefaz
    base.loc[(base['Secretaria'] != '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "valor_liberado_emprestimo"] = (base['MG_Emprestimo_Disponivel'] * coeficiente_sefaz).round(2)

    # Para SEFAZ, que são da Educação
    base.loc[(base['Secretaria'] == '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "banco_emprestimo"] = banco_sefaz_educ
    base.loc[(base['Secretaria'] == '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "prazo_emprestimo"] = parcelas_sefaz_educ
    base.loc[(base['Secretaria'] == '08 - SECRETARIA DA EDUCACAO') & (base['Lotacao'] == 'SEFAZ'), "valor_liberado_emprestimo"] = (base['MG_Emprestimo_Disponivel'] * coeficiente_sefaz_educ).round(2)

    # Para lotações diferentes de SEFAZ
    base.loc[(base['Lotacao'] != 'SEFAZ'), "banco_emprestimo"] = banco_restante
    base.loc[(base['Lotacao'] != 'SEFAZ'), "prazo_emprestimo"] = parcelas_restante
    base.loc[(base['Lotacao'] != 'SEFAZ'), "valor_liberado_emprestimo"] = (base['MG_Emprestimo_Disponivel'] * coeficiente_restante).round(2)

    # Convertendo tipos de dados
    base["banco_emprestimo"] = base["banco_emprestimo"].astype(int)
    base["prazo_emprestimo"] = base["prazo_emprestimo"].astype(int)

    # Filtrando por vínculos aceitos, removendo os inválidos
    base = base.loc[~(base['Vinculo_Servidor'].isin(vinculos_invalidos)) | (base['Vinculo_Servidor'].isnull())]

    # Ajustando o banco para vínculos específicos
    base.loc[base['Vinculo_Servidor'] == '8 - ESTAB. CONSTIT.', 'banco'] = 707

    # Ordenando a base por valor liberado e removendo duplicatas
    base = base.sort_values(by='valor_liberado_emprestimo', ascending=False).drop_duplicates(['CPF'])

    # Cálculo da comissão
    base['comissao_emprestimo'] = (base['valor_liberado_emprestimo'] * comissao).round(2)

    # Filtrando pela comissão mínima
    base = base.loc[base['comissao_emprestimo'] >= comissao_min]

        # Selecionando colunas relevantes
    base['FONE1'] = ""
    base['FONE2'] = ""
    base['FONE3'] = ""
    base['FONE4'] = ""

    base['valor_liberado_beneficio'] = ""
    base['valor_liberado_cartao'] = ""

    base['comissao_beneficio'] = ""
    base['comissao_cartao'] = ""

    base['valor_parcela_emprestimo'] = ""
    base['valor_parcela_beneficio'] = ""
    base['valor_parcela_cartao'] = ""

    base['banco_beneficio'] = ""
    base['banco_cartao'] = ""

    base['prazo_beneficio'] = ""
    base['prazo_cartao'] = ""

    base['campanha'] = ''
    colunas = [
        'Origem_Dado', 'Nome_Cliente', 'Matricula', 'CPF', 'Data_Nascimento',
        'MG_Emprestimo_Total', 'MG_Emprestimo_Disponivel',
        'MG_Beneficio_Saque_Total', 'MG_Beneficio_Saque_Disponivel',
        'MG_Cartao_Total', 'MG_Cartao_Disponivel',
        'Convenio', 'Vinculo_Servidor', 'Lotacao', 'Secretaria',
        'FONE1', 'FONE2', 'FONE3', 'FONE4',
        'valor_liberado_emprestimo', 'valor_liberado_beneficio', 'valor_liberado_cartao',
        'comissao_emprestimo', 'comissao_beneficio', 'comissao_cartao',
        'valor_parcela_emprestimo', 'valor_parcela_beneficio', 'valor_parcela_cartao',
        'banco_emprestimo', 'banco_beneficio', 'banco_cartao',
        'prazo_emprestimo', 'prazo_beneficio', 'prazo_cartao',
        'campanha'
    ]

    base = base[colunas]

    mapeamento = {
        'Origem_Dado': 'ORIGEM DO DADO',
        'MG_Emprestimo_Total': 'Mg_Emprestimo_Total',
        'MG_Emprestimo_Disponivel': 'Mg_Emprestimo_Disponivel',
        'MG_Beneficio_Saque_Total': 'Mg_Beneficio_Saque_Total',
        'MG_Beneficio_Saque_Disponivel': 'Mg_Beneficio_Saque_Disponivel',
        'MG_Cartao_Total': 'Mg_Cartao_Total',
        'MG_Cartao_Disponivel': 'Mg_Cartao_Disponivel',
        'campanha': 'Campanha'
}

    # Renomear as colunas
    base.rename(columns=mapeamento, inplace=True)

    st.write(base.shape)

    # Retornando a base filtrada
    return base
