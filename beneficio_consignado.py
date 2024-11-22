import pandas as pd
import streamlit as st  # Importando Streamlit para uso de st.error

def filtro_beneficio_consignado(base, coeficiente_beneficio, coeficiente_consignado,
                                banco_beneficio, banco_consignado, 
                                comissao_beneficio, comissao_consignado, 
                                parcelas_beneficio, parcelas_consignado,
                                comissao_min, margem_limite, vinculos_invalidos):
    # Verifica se a base está vazia
    if base.empty:
        st.error("Erro: A base está vazia.")
        return pd.DataFrame()
    
    # Limitando as colunas para as primeiras 23, se necessário
    base = base.iloc[:, :23]

    # Identificando o convênio único
    convenio = base['Convenio'].unique()[0]

    # Definindo variáveis para o cálculo de margens e restrições específicas do GOVSP
    if convenio == 'govsp':
        base['margem_beneficio_usada'] = base['MG_Beneficio_Saque_Total'] - base['MG_Beneficio_Saque_Disponivel']
        base['margem_cartao_usada'] = base['MG_Cartao_Total'] - base['MG_Cartao_Disponivel']
        usou_beneficio = base.loc[base['margem_beneficio_usada'] > 0]
        usou_cartao = base.loc[base['margem_cartao_usada'] > 0]

    # Cálculo do valor liberado de acordo com o convênio
    base['valor_liberado_beneficio'] = 0
    base['valor_liberado_cartao'] = 0

    if convenio == 'govsp':
        base.loc[base['margem_beneficio_usada'] == 0, 'valor_liberado_beneficio'] = (base['MG_Beneficio_Saque_Disponivel'] * coeficiente_beneficio).round(2)
        base.loc[base['margem_cartao_usada'] == 0, 'valor_liberado_cartao'] = (base['MG_Cartao_Disponivel'] * coeficiente_consignado).round(2)
        
        # Para Celetistas (vínculo 4) que não usaram margem de benefício
        base.loc[(base['Vinculo_Servidor'] == '4 - Celetista') & (base['margem_beneficio_usada'] == 0), 'valor_liberado_beneficio'] = (base['MG_Beneficio_Saque_Disponivel'] * coeficiente_beneficio).round(2)
        base.loc[(base['Vinculo_Servidor'] == '4 - Celetista') & (base['margem_cartao_usada'] == 0), 'valor_liberado_cartao'] = 0
    else:
        base['valor_liberado_beneficio'] = (base['MG_Beneficio_Saque_Disponivel'] * coeficiente_beneficio).round(2)
        base['valor_liberado_cartao'] = (base['MG_Cartao_Disponivel'] * coeficiente_consignado).round(2)

    # Filtrando registros com 'MG_Emprestimo_Disponivel' abaixo do limite de margem
    base = base[base['MG_Emprestimo_Disponivel'] < margem_limite]

    # Excluindo vínculos inválidos
    base = base[~base['Vinculo_Servidor'].isin(vinculos_invalidos) | base['Vinculo_Servidor'].isnull()]

    # Excluindo lotação 'ALESP' do convênio GOVSP
    if convenio == 'govsp':
        base = base[base['Lotacao'] != "ALESP"]

    # Restrição de GOVSP para provimentos específicos
    if convenio == 'govsp':
        base = base[(base['valor_liberado_beneficio'] != 0) | (base['valor_liberado_cartao'] != 0)]
        base.loc[(base['valor_liberado_beneficio'] != 0) & (base['Matricula'].isin(usou_beneficio['Matricula'])), 'valor_liberado_beneficio'] = 0
        base.loc[(base['valor_liberado_cartao'] != 0) & (base['Matricula'].isin(usou_cartao['Matricula'])), 'valor_liberado_cartao'] = 0

    # Cálculo da comissão sobre os valores liberados
    base['comissao_beneficio'] = (base['valor_liberado_beneficio'] * comissao_beneficio).round(2)
    base['comissao_cartao'] = (base['valor_liberado_cartao'] * comissao_consignado).round(2)
    base['comissao_total'] = (base['comissao_beneficio'] + base['comissao_cartao']).round(2)

    # Filtrando registros com comissão total acima do mínimo
    base = base[base['comissao_total'] >= comissao_min]

    # Ordenação por comissão total e remoção de duplicatas por CPF
    base = base.sort_values(by='comissao_total', ascending=False)
    base = base.drop_duplicates(subset=['CPF'])

    # Formatação de dados: Nome do cliente e CPF
    base['Nome_Cliente'] = base['Nome_Cliente'].apply(lambda x: x.title())
    base['CPF'] = base['CPF'].str.replace(".", "", regex=False).str.replace("-", "", regex=False)

    # Adicionando informações de banco e parcelas
    base['banco_beneficio'] = banco_beneficio
    base['banco_cartao'] = banco_consignado
    base['prazo_beneficio'] = parcelas_beneficio
    base['prazo_cartao'] = parcelas_consignado

    base['FONE1'] = ""
    base['FONE2'] = ""
    base['FONE3'] = ""
    base['FONE4'] = ""

    base['valor_liberado_emprestimo'] = ""

    base['comissao_emprestimo'] = ""

    base['valor_parcela_emprestimo'] = ""
    base['valor_parcela_beneficio'] = ""
    base['valor_parcela_cartao'] = ""

    base['banco_emprestimo'] = ""

    base['prazo_emprestimo'] = ""

    base['Campanha'] = ''

    # Selecionando colunas relevantes para o retorno final
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

