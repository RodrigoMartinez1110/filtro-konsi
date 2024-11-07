import streamlit as st
import pandas as pd
from juntar_bases import juntar_bases

# Filtros de NOVO
from novo import filtro_novo
from novo import filtro_novo_govsp

# Filtros de BENEFICIO
from beneficio import filtro_beneficio

# Filtros de CONSIGNADO
from consignado import filtro_consignado

from beneficio_consignado import filtro_beneficio_consignado

# Função para selecionar as variáveis da campanha
def escolha_campanha(campanha, base, vinculos_invalidos):
    bancos = ['2', '243', '422', '623', '643', '707', '33', '955']
    if campanha != "Beneficio & Cartao":
        banco = st.sidebar.selectbox(f"Banco do coeficiente {campanha}", bancos, key=f"banco_{campanha}")
        coeficiente = st.sidebar.number_input(f"Digite o coeficiente da campanha {campanha}:", min_value=0.0, max_value=100.1)
        comissao = round(st.sidebar.number_input(f"Digite a comissão da campanha {campanha} em %:", min_value=0.0, max_value=100.0, step=0.01) / 100, 2)
        parcelas = st.sidebar.slider(f'Quantidade de parcelas {campanha}', min_value=1, max_value=180, step=1)

    else:
        banco_beneficio = st.sidebar.selectbox(f"Banco do coeficiente {campanha}", bancos, key=f"banco_{campanha}")
        banco_consignado = st.sidebar.selectbox(f"Banco do coeficiente {campanha}", bancos, key=f"banco_{campanha}2")

        coeficiente_beneficio = st.sidebar.number_input(f"Digite o coeficiente do Cartão Beneficio:", min_value=0.0, max_value=100.1)
        coeficiente_consignado = st.sidebar.number_input(f"Digite o coeficiente do Cartao Consignado:", min_value=0.0, max_value=100.1)

        comissao_beneficio = round(st.sidebar.number_input(f"Digite a comissão da campanha Cartão Beneficio em %:", min_value=0.0, max_value=100.0, step=0.01) / 100, 2)
        comissao_consignado = round(st.sidebar.number_input(f"Digite a comissão da campanha Cartao Consignado em %:", min_value=0.0, max_value=100.0, step=0.01) / 100, 2)

        parcelas_beneficio = st.sidebar.slider(f'Quantidade de parcelas Cartão Beneficio', min_value=1, max_value=180, step=1)
        parcelas_consignado = st.sidebar.slider(f'Quantidade de parcelas Cartao Consignado', min_value=1, max_value=180, step=1)

    comissao_min = st.sidebar.number_input("Comissão mínima para filtrar:")

    margem_limite = st.sidebar.number_input(
        f"Digite o valor {'mínimo' if campanha == 'Novo' else 'máximo'} de margem limite", 
        min_value=0.0, max_value=1000.0
    )

    # Atualizando a seleção de vínculos não aceitos
        # PREF GOIANIA É LOTACAO
    if convenio == 'prefgyn':
        vinculos_validos = base[~base['Lotacao'].isin(vinculos_invalidos)]['Lotacao'].unique()
        vinculos_invalidos = st.sidebar.multiselect(
            f"Escolha as Lotacões NÃO ACEITAS em {convenio}:", 
            options=vinculos_validos.tolist(),  # Atualizando opções com vínculos válidos
            default=vinculos_invalidos  # Mantendo seleção anterior
        )
    else:
        vinculos_validos = base[~base['Vinculo_Servidor'].isin(vinculos_invalidos)]['Vinculo_Servidor'].unique()
        vinculos_invalidos = st.sidebar.multiselect(
            f"Escolha os Vinculos NÃO ACEITOS em {convenio}:", 
            options=vinculos_validos.tolist(),  # Atualizando opções com vínculos válidos
            default=vinculos_invalidos  # Mantendo seleção anterior
        )


    if campanha != "Beneficio & Cartao":
        return coeficiente, banco, comissao, parcelas, comissao_min, margem_limite, vinculos_invalidos
    else:
        return coeficiente_beneficio, coeficiente_consignado, banco_beneficio, banco_consignado, comissao_beneficio, comissao_consignado, parcelas_beneficio, parcelas_consignado, comissao_min, margem_limite, vinculos_invalidos

# Função específica para campanha govsp
def escolha_campanha_govsp(campanha, base, vinculos_invalidos):
    bancos = ['2', '243', '422', '623', '643', '707', '33', '955']

    st.sidebar.write("**SEFAZ**")
    coeficiente_sefaz = st.sidebar.number_input(f"Digite o coeficiente da campanha {campanha} sefaz:", min_value=0.0, max_value=100.1)
    banco_sefaz = st.sidebar.selectbox(f"Banco do coeficiente {campanha} sefaz", bancos)
    parcelas_sefaz = st.sidebar.slider(f'Quantidade de parcelas {campanha} sefaz', min_value=1, max_value=180, step=1)
    st.sidebar.write("---")

    st.sidebar.write("**SEFAZ EDUCAÇÃO**")
    coeficiente_sefaz_educ = st.sidebar.number_input(f"Digite o coeficiente da campanha {campanha} sefaz educação:", min_value=0.0, max_value=100.1)
    banco_sefaz_educ = st.sidebar.selectbox(f"Banco do coeficiente {campanha} sefaz educação", bancos)
    parcelas_sefaz_educ = st.sidebar.slider(f'Quantidade de parcelas {campanha} sefaz educação', min_value=1, max_value=180, step=1)
    st.sidebar.write("---")

    st.sidebar.write("**PMESP E SPPREV**")
    coeficiente_restante = st.sidebar.number_input(f"Digite o coeficiente da campanha {campanha} restante:", min_value=0.0, max_value=100.1)
    banco_restante = st.sidebar.selectbox(f"Banco do coeficiente {campanha} restante (spprev e pmesp)", bancos)
    parcelas_restante = st.sidebar.slider(f'Quantidade de parcelas {campanha} restante', min_value=1, max_value=180, step=1)
    st.sidebar.write("---")

    st.sidebar.write("**Filtros gerais**")
    margem_limite = st.sidebar.number_input(f"Digite o valor mínimo de margem limite", min_value=0.0, max_value=1000.0)
    comissao = round(st.sidebar.number_input(f"Digite a comissão da campanha {campanha} em %:", min_value=0.0, max_value=100.0, step=0.01) / 100, 2)
    comissao_min = st.sidebar.number_input("Comissão mínima para filtrar:")

    # Atualizando a seleção de vínculos não aceitos
    vinculos_validos = base[~base['Vinculo_Servidor'].isin(vinculos_invalidos)]['Vinculo_Servidor'].unique()
    vinculos_invalidos = st.sidebar.multiselect(
        f"Escolha os Vinculos NÃO ACEITOS em {convenio}:", 
        options=vinculos_validos.tolist(),  # Atualizando opções com vínculos válidos
        default=vinculos_invalidos  # Mantendo seleção anterior
    )

    return (coeficiente_sefaz, coeficiente_sefaz_educ, coeficiente_restante,
            banco_sefaz, banco_sefaz_educ, banco_restante,
            parcelas_sefaz, parcelas_sefaz_educ, parcelas_restante,
            comissao, comissao_min, margem_limite, vinculos_invalidos)


# Título da aplicação
st.title("Filtrador Konsi")

# Carregamento de arquivos CSV
arquivos = st.file_uploader('Selecione os arquivos CSV', accept_multiple_files=True, type=['csv'])

# Verificando se arquivos foram carregados
if arquivos:
    base = juntar_bases(arquivos)
    if not base.empty:
        st.write(base.head(500))  # Mostrando as primeiras linhas para verificação

        # Configuração do sidebar para seleção de campanha
        st.sidebar.title("Variáveis")
        campanha = st.sidebar.selectbox("Escolha o tipo de campanha:", ['Novo', 'Beneficio', 'Cartao', 'Beneficio & Cartao'])
        st.sidebar.write("---")

        # Inicializa a lista de vínculos inválidos
        vinculos_invalidos = []

        convenio = base.loc[1, 'Convenio']
        if convenio == "govsp" and campanha == 'Novo':
            # Chamando função específica para govsp
            variaveis = escolha_campanha_govsp(campanha, base, vinculos_invalidos)
        else:
            # Chamando função geral para outras campanhas
            variaveis = escolha_campanha(campanha, base, vinculos_invalidos)

        # Botão de início da filtragem
        if st.button("Iniciar Filtragem!"):
            # Chamada da função filtro_novo com todos os parâmetros
            if campanha == "Novo":
                if convenio == "govsp":
                    resultados = filtro_novo_govsp(base, *variaveis)
                else:
                    resultados = filtro_novo(base, *variaveis)
            elif campanha == "Beneficio":
                resultados = filtro_beneficio(base, *variaveis)
            elif campanha == "Cartao":
                resultados = filtro_consignado(base, *variaveis)
            elif campanha == "Beneficio & Cartao":
                resultados = filtro_beneficio_consignado(base, *variaveis)
                

            if not resultados.empty:
                st.dataframe(resultados)
                # Adiciona botão para download do CSV filtrado
                csv = resultados.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name='resultados_filtrados.csv',
                    mime='text/csv',
                )
            else:
                st.warning("Nenhum resultado encontrado com os filtros aplicados.")
