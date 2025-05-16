import streamlit as st
import telnetlib
import time

st.set_page_config(page_title="Provisionamento OLT Intelbras", page_icon="🖥", layout="wide")
st.title("🖥 Provisionamento OLT Intelbras")
st.markdown("""
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        background-color: #800080; /* Cor de fundo roxa */
        color: #ffffff; /* Texto branco para contraste */
    }
    .stButton > button {
        background-color: #007aff; /* Azul padrão da Apple */
        color: white;
        border: none;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px; /* Bordas arredondadas maiores */
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button:hover {
        background-color: #005bb5; /* Azul mais escuro ao passar o mouse */
        transform: scale(1.05); /* Leve aumento ao passar o mouse */
    }
    .stTextInput > div > input {
        border: 2px solid #007aff;
        border-radius: 12px;
        padding: 12px;
        width: 100%;
        box-sizing: border-box;
        font-size: 16px;
        color: #333333;
    }
    .stTextInput > div > input:focus {
        border-color: #005bb5;
        outline: none;
        box-shadow: 0 0 5px rgba(0, 91, 181, 0.5);
    }
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
        }
        .stTextInput > div > input {
            font-size: 14px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Solicitar ao usuário que insira as informações de login 🔑
st.sidebar.header("Configurações de Login")
usuario = st.sidebar.text_input("Usuário:")
senha = st.sidebar.text_input("Senha:", type="password")
port = st.sidebar.text_input("Porta de acesso (default: 23):", value="23")

# Endereços IP e seus respectivos nomes pré-definidos da OLT Intelbras
enderecos_ip = {
    "🖥  OLT INTELBRAS PARAISO": "172.31.188.2",
    "🖥  OLT INTELBRAS BOM_VIVER ➡": "172.31.248.2",
    "🖥  OLT INTELBRAS FORTALEZA ➡": "172.31.194.2",
    "🖥  OLT INTELBRAS 3 FUROS ➡": "172.31.195.2"
}

st.sidebar.subheader("Selecione a OLT")
endereco_escolhido = st.sidebar.selectbox("Endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Campos para dados de provisionamento
st.header("📋 Dados de Provisionamento")
col1, col2, col3 = st.columns(3)

with col1:
    sn_value = st.text_input("ID Serial:")
    pon_value = st.text_input("PON:")

with col2:
    id_value = st.text_input("ID:")
    desc_value = st.text_input("Nome:")

with col3:
    veip_value = st.text_input("VEIP:")

# Botão para listar as ONUs disponíveis
if st.button("🔍 Listar ONUs Disponíveis"):
    try:
        # Conectando à OLT Intelbras via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        tn.write(usuario.encode('ascii') + b"\n")
        tn.write(senha.encode('ascii') + b"\n")

        # Executando o comando "show ont-find list interface gpon all"
        tn.write(b"enable\n")
        tn.write(b"configure terminal\n")
        tn.write(b"show ont-find list interface gpon all\n")
        time.sleep(3)

        output = tn.read_very_eager().decode('ascii')
        st.text_area("ONUs disponíveis:", output, height=300)

        # Fechando a conexão Telnet
        tn.close()

    except Exception as e:
        st.error(f"Erro ao listar as ONUs: {e}")

# Botão para iniciar o provisionamento
if st.button("🚀 Iniciar Provisionamento"):
    try:
        # Conectando à OLT Intelbras via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        tn.write(usuario.encode('ascii') + b"\n")
        tn.write(senha.encode('ascii') + b"\n")

        # Executando o comando "show ont brief sn string-hex"
        time.sleep(1)
        tn.write(f"show ont brief sn string-hex {sn_value}\n".encode('ascii'))
        tn.write(b"\n")
        time.sleep(3)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show ont brief sn string-hex':", output, height=300)

        # Executando os comandos de provisionamento
        tn.write(f"interface gpon 0/{pon_value}\n".encode('ascii'))
        time.sleep(3)
        tn.write(b"deploy profile rule\n")
        time.sleep(3)
        tn.write(f"aim 0/{pon_value}/{id_value} name {desc_value}\n".encode('ascii'))
        time.sleep(3)
        tn.write(f"permit sn string-hex {sn_value} line {veip_value} default line {veip_value}\n".encode('ascii'))
        time.sleep(3)
        tn.write(b"active\n")
        time.sleep(3)
        tn.write(b"y\n")
        time.sleep(3)
        tn.write(b"exit\n")
        time.sleep(3)
        tn.write(b"end\n")
        time.sleep(3)

        # Executar o comando "show ont optical-info"
        time.sleep(1)
        tn.write(f"show ont optical-info 0/{pon_value}/{id_value}\n".encode('ascii'))
        time.sleep(3)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show ont optical-info':", output, height=300)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")
