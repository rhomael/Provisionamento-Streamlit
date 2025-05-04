import streamlit as st
import telnetlib
import time

st.set_page_config(page_title="Provisionamento OLT Huawei", page_icon="🖥", layout="wide")
st.title("🖥 Provisionamento OLT Huawei")
st.markdown("""
<style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .stTextInput > div > input {
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Solicitar ao usuário que insira as informações de login 🔑
st.sidebar.header("Configurações de Login")
usuario = st.sidebar.text_input("Usuário:")
senha = st.sidebar.text_input("Senha:", type="password")
port = st.sidebar.text_input("Porta de acesso (default: 23):", value="23")

# Endereços IP e seus respectivos nomes pré-definidos da OLT Huawei
enderecos_ip = {
    "🖥  OLT HUWAEI COHAB ➡": "186.216.11.0",
    "🖥  OLT HUWAEI ITAPECURU ➡": "45.181.228.67",
    "🖥  OLT HUWAEI FIALHO ➡": "186.216.11.0",
    "🖥  OLT HUWAEI PINHEIRO ➡": "172.31.237.2",
    "🖥  OLT HUAWEI MIRINZAL ➡": "172.31.238.2",
    "🖥  OLT HUWAEI SANTA HELENA ➡": "45.181.230.29",
    "🖥  OLT HUWAEI TURIACU ➡": "186.216.45.254"
}

st.sidebar.subheader("Selecione a OLT")
endereco_escolhido = st.sidebar.selectbox("Endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Campos para dados de provisionamento
st.header("📋 Dados de Provisionamento")
col1, col2, col3 = st.columns(3)

with col1:
    slot_value = st.text_input("SLOT:")
    pon_value = st.text_input("PON:")

with col2:
    id_value = st.text_input("ID SERIAL:")
    veip_value = st.text_input("VEIP 30,300 ou 40,1022:")

with col3:
    vlan_value = st.text_input("VLAN:")
    desc_value = st.text_input("DESCRIÇÃO:")
    onu_value = st.text_input("ID ONU:")

# Botão para listar as ONUs disponíveis
if st.button("🔍 Listar ONUs Disponíveis"):
    try:
        # Conectando à OLT Huawei via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        tn.write(usuario.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(senha.encode('ascii') + b"\n")
        time.sleep(1)

        # Executando o comando "display ont autofind all"
        tn.write(b"enable\n")
        time.sleep(1)
        tn.write(b"config\n")
        time.sleep(1)
        tn.write(b"display ont autofind all\n")
        tn.write(b" \n")
        time.sleep(3)
        tn.write(b" q\n")
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
        # Conectando à OLT Huawei via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        tn.write(usuario.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(senha.encode('ascii') + b"\n")
        time.sleep(1)

        # Executando os comandos de provisionamento
        tn.write(f"interface gpon 0/{slot_value}\n".encode('ascii'))
        time.sleep(3)
        tn.write(f"ont confirm {pon_value} sn-auth {id_value} omci ont-lineprofile-id {veip_value} ont-srvprofile-id {vlan_value} desc {desc_value}\n".encode('ascii'))
        time.sleep(3)
        tn.write(f"ont port native-vlan {pon_value} {onu_value} eth 1 vlan {vlan_value}\n".encode('ascii'))
        time.sleep(3)
        tn.write(b"quit\n")
        time.sleep(3)
        tn.write(f"service-port vlan {vlan_value} gpon 0/{slot_value}/{pon_value} ont {onu_value} gemport 5 multi-service user-vlan {vlan_value}\n".encode('ascii'))
        time.sleep(3)

        # Executar o comando "display ont optical-info"
        tn.write(f"interface gpon 0/{slot_value}\n".encode('ascii'))
        time.sleep(1)
        tn.write(f"display ont optical-info {pon_value} {onu_value}\n".encode('ascii'))
        tn.write(b"\n")
        time.sleep(10)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'display ont optical-info':", output, height=300)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")