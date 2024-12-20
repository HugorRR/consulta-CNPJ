import streamlit as st
import requests
import pandas as pd
import re
from io import BytesIO

def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)
    
    if len(cnpj) != 14:
        st.error("CNPJ inválido. Deve conter 14 dígitos.")
        return False
    
    return True

def consulta_CNPJ(cnpj):
    url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na consulta: {e}")
        return None

def formatar_dados(dados):
    def safe_get(dicionario, chave, padrao='Não informado'):
        return dicionario.get(chave, padrao)

    atividade_principal = safe_get(dados, 'atividade_principal', [{}])[0]
    texto = safe_get(atividade_principal, 'text')
    codigo = safe_get(atividade_principal, 'code')
    atividades_secundarias = safe_get(dados, 'atividades_secundarias', [])
    textos = [f"{d.get('text', '')} ({d.get('code', '')})" for d in atividades_secundarias]

    return {
        'CNPJ': safe_get(dados, 'cnpj'),
        'Tipo': safe_get(dados, 'tipo'),
        'Porte': safe_get(dados, 'porte'),
        'Nome': safe_get(dados, 'nome'),
        'Fantasia': safe_get(dados, 'fantasia'),
        'Abertura': safe_get(dados, 'abertura'),
        'Atividade Principal': f'{texto} ({codigo})',
        'Atividades Secundárias': ', '.join(textos),
        'Natureza Jurídica': safe_get(dados, 'natureza_juridica'),
        'Logradouro': safe_get(dados, 'logradouro'),
        'Número': safe_get(dados, 'numero'),
        'Complemento': safe_get(dados, 'complemento'),
        'CEP': safe_get(dados, 'cep'),
        'Bairro': safe_get(dados, 'bairro'),
        'Município': safe_get(dados, 'municipio'),
        'UF': safe_get(dados, 'uf'),
        'Email': safe_get(dados, 'email'),
        'Telefone': safe_get(dados, 'telefone'),
        'EFR': safe_get(dados, 'efr'),
        'Situação': safe_get(dados, 'situacao'),
        'Data Situação': safe_get(dados, 'data_situacao'),
        'Motivo Situação': safe_get(dados, 'motivo_situacao'),
        'Situação Especial': safe_get(dados, 'situacao_especial'),
        'Data Situação Especial': safe_get(dados, 'data_situacao_especial'),
        'Capital Social': safe_get(dados, 'capital_social'),
        'QSA': ', '.join([f"{d['nome']} ({d['qual']}) - {d.get('pais_origem', 'Não informado')}" for d in safe_get(dados, 'qsa', [])]),
        'Última Atualização': safe_get(dados, 'ultima_atualizacao'),
        'Status': safe_get(dados, 'status'),
    }

def update_access_counter():
    try:
        with open('access_counter.txt', 'r') as f:
            count = int(f.read())
    except FileNotFoundError:
        count = 0

    count += 1

    with open('access_counter.txt', 'w') as f:
        f.write(str(count))

    return count

def pagina_doacoes():
    st.sidebar.header("🤝 Apoie este Projeto")
    
    st.sidebar.subheader("💳 Doação via PIX")
    st.sidebar.write("Chave PIX: hugorogerio522@gmail.com")
    
    st.sidebar.subheader("💰 Doação em Criptomoedas")
    
    with st.sidebar.expander("📍 Bitcoin (BTC)"):
        btc_address = "1KnmyxZMv4qgTCqu6PNFA2oQ5i1WwQwcu"
        st.image(r"qrcode.png", width=150)
        st.code(btc_address, language='text')
    
    with st.sidebar.expander("📍 Ethereum (ETH) ERC20"):
        eth_address = "0x489bb9936151473b995e289fc68defc967e788b2"
        st.code(eth_address, language='text')

    access_count = update_access_counter()
    st.sidebar.markdown(f"👥 Número de acessos: {access_count}")

def main():
    st.set_page_config(
        page_title="Consulta CNPJ da B/PALMA", 
        page_icon="🏢", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        color: #333;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🔍 Consulta de CNPJ")
    st.markdown('<p class="big-font">Consulte informações detalhadas de empresas brasileiras</p>', unsafe_allow_html=True)
    st.markdown('<div class="highlight">Atenção: API limitada a 3 consultas por minuto</div>', unsafe_allow_html=True)

    cnpj = st.text_input("Digite o CNPJ desejado (somente números):", max_chars=14, key="cnpj_input")

    if st.button("Consultar", type="primary"):
        if cnpj:
            if validar_cnpj(cnpj):
                try:
                    with st.spinner("Consultando CNPJ..."):
                        cnpj_limpo = re.sub(r'\D', '', cnpj)
                        dados = consulta_CNPJ(cnpj_limpo)
                    
                    if dados:
                        dados_formatados = formatar_dados(dados)
                        
                        st.success("CNPJ encontrado!")
                        
                        cols = st.columns(3)
                        info_sections = [
                            ('Informações Principais', ['CNPJ', 'Nome', 'Fantasia', 'Tipo', 'Porte', 'Abertura', 'Situação']),
                            ('Atividades', ['Atividade Principal', 'Atividades Secundárias']),
                            ('Contato', ['Email', 'Telefone'])
                        ]
                        
                        for i, (titulo, campos) in enumerate(info_sections):
                            with cols[i]:
                                st.subheader(titulo)
                                for chave in campos:
                                    st.write(f"**{chave}:** {dados_formatados[chave]}")

                        st.subheader("Endereço")
                        st.write(f"{dados_formatados['Logradouro']}, {dados_formatados['Número']} - {dados_formatados['Complemento']}")
                        st.write(f"{dados_formatados['Bairro']}, {dados_formatados['Município']} - {dados_formatados['UF']}, CEP: {dados_formatados['CEP']}")

                        st.subheader("Informações Adicionais")
                        for chave in ['Natureza Jurídica', 'EFR', 'Data Situação', 'Motivo Situação', 'Situação Especial', 'Data Situação Especial', 'Capital Social', 'QSA', 'Última Atualização', 'Status']:
                            st.write(f"**{chave}:** {dados_formatados[chave]}")

                        df = pd.DataFrame([dados_formatados])
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Dados')

                        st.download_button(
                            label="Baixar dados em XLSX",
                            data=excel_buffer.getvalue(),
                            file_name=f"Dados_{cnpj}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("CNPJ não encontrado.")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {str(e)}")
        else:
            st.warning("Por favor, digite um CNPJ.")

    pagina_doacoes()

if __name__ == "__main__":
    main()