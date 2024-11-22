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
    base['banco_beneficio'] = banco
    base['prazo_beneficio'] = parcelas
    
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
    base['valor_liberado_beneficio'] = (base['MG_Beneficio_Saque_Disponivel'] * coeficiente).round(2)
    
    # Cálculo da comissão
    base['comissao_beneficio'] = (base['valor_liberado_beneficio'] * comissao).round(2)

    # Filtrando com base na comissão mínima
    base = base.loc[base['comissao_beneficio'] >= comissao_min]

    # Ordenando e removendo duplicatas
    base = base.sort_values(by='valor_liberado_beneficio', ascending=False)
    base = base.drop_duplicates(subset='CPF')

    # Selecionando colunas relevantes
    base['FONE1'] = ""
    base['FONE2'] = ""
    base['FONE3'] = ""
    base['FONE4'] = ""

    base['valor_liberado_emprestimo'] = ""
    base['valor_liberado_cartao'] = ""
    
    base['comissao_emprestimo'] = ""
    base['comissao_cartao'] = ""
    
    base['valor_parcela_emprestimo'] = ""
    base['valor_parcela_beneficio'] = ""
    base['valor_parcela_cartao'] = ""

    base['banco_emprestimo'] = ""
    base['banco_cartao'] = ""
    
    base['prazo_emprestimo'] = ""
    base['prazo_cartao'] = ""
    
    base['Campanha'] = ''

    # Selecionando colunas relevantes
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
    }

    # Renomear as colunas
    base.rename(columns=mapeamento, inplace=True)
    st.write(base.shape)

    return base  # Retorna o DataFrame filtrado
