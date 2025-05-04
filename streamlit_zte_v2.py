import streamlit as st
import telnetlib
import time

st.set_page_config(page_title="Provisionamento OLT ZTE", page_icon="🖥", layout="wide")
st.title("🖥 Provisionamento OLT ZTE")
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

# Endereços IP e seus respectivos nomes pré-definidos da OLT ZTE
enderecos_ip = {
    "🖥  OLT ZTE PARAISO ➡": "172.31.188.2",
    "🖥  OLT ZTE PALMEIRANDIA ➡": "172.31.239.2"
}

st.sidebar.subheader("Selecione a OLT")
endereco_escolhido = st.sidebar.selectbox("Endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Campos para dados de provisionamento
st.header("📋 Dados de Provisionamento")
col1, col2, col3 = st.columns(3)

with col1:
    pon_value = st.text_input("PON:")
    id_onu = st.text_input("ID ONU:")

with col2:
    type_onu = st.text_input("Type (ZTE-F643 ou ZTE-F660):")
    sn_onu = st.text_input("Serial:")

with col3:
    vlan_value = st.text_input("VLAN:")
    name_onu = st.text_input("Nome do Cliente:")

# Botão para listar as ONUs disponíveis
if st.button("🔍 Listar ONUs Disponíveis"):
    try:
        # Conectando à OLT ZTE via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        time.sleep(0.5)
        tn.write(usuario.encode('ascii') + b"\n")
        time.sleep(0.5)
        tn.write(senha.encode('ascii') + b"\n")
        time.sleep(0.5)

        # Executando o comando "show pon onu uncfg"
        tn.write(b"configure terminal\n")
        time.sleep(0.5)
        tn.write(b"show pon onu uncfg\n")
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
        # Conectando à OLT ZTE via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        time.sleep(0.5)
        tn.write(usuario.encode('ascii') + b"\n")
        time.sleep(0.5)
        tn.write(senha.encode('ascii') + b"\n")
        time.sleep(0.5)

        # Executar o comando "show gpon onu state"
        tn.write(f"show gpon onu state gpon_olt-1/3/{pon_value}\n".encode('ascii'))
        tn.write(b" \n")
        time.sleep(0.5)
        tn.write(b" \n")
        time.sleep(0.5)
        tn.write(b" \n")
        time.sleep(0.5)
        tn.write(b" \n")
        time.sleep(0.5)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show gpon onu state':", output, height=300)

        # Executando comandos de provisionamento
        tn.write(b"!\n")
        time.sleep(1)
        tn.write(f"interface gpon_olt-1/3/{pon_value}\n".encode('ascii'))
        time.sleep(1)
        tn.write(f"onu {id_onu} type {type_onu} sn {sn_onu}\n".encode('ascii'))
        time.sleep(1)
        tn.write(b"exit\n")
        time.sleep(1)
        tn.write(b"!\n")
        time.sleep(1)
        tn.write(f"interface gpon_onu-1/3/{pon_value}:{id_onu}\n".encode('ascii'))
        time.sleep(1)
        tn.write(f"name {name_onu}\n".encode('ascii'))
        time.sleep(1)
        tn.write(b"sn-bind enable sn\n")
        time.sleep(1)
        tn.write(b"tcont 4 profile 1G\n")
        time.sleep(1)
        tn.write(b"gemport 1 tcont 4\n")
        time.sleep(1)
        tn.write(b"exit\n")
        time.sleep(1)
        tn.write(b"!\n")
        time.sleep(1)
        tn.write(f"interface vport-1/3/{pon_value}.{id_onu}:1\n".encode('ascii'))
        time.sleep(1)
        tn.write(f"service-port 1 user-vlan {vlan_value} vlan {vlan_value}\n".encode('ascii'))
        time.sleep(1)
        tn.write(b"exit\n")
        time.sleep(1)
        tn.write(b"!\n")
        time.sleep(1)
        tn.write(f"pon-onu-mng gpon_onu-1/3/{pon_value}:{id_onu}\n".encode('ascii'))
        time.sleep(1)
        tn.write(f"service 1 gemport 1 vlan {vlan_value}\n".encode('ascii'))
        time.sleep(1)
        tn.write(f"vlan port eth_0/1 mode tag vlan {vlan_value}\n".encode('ascii'))
        time.sleep(1)
        tn.write(b"exit\n")
        time.sleep(1)
        tn.write(b"exit\n")
        time.sleep(1)

        # Executar o comando "show pon power attenuation"
        tn.write(f"show pon power attenuation gpon_onu-1/3/{pon_value}:{id_onu}\n".encode('ascii'))
        time.sleep(3)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show pon power attenuation':", output, height=300)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")