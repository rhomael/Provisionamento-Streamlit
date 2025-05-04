import streamlit as st
import telnetlib
import time

# Configuração da interface do Streamlit
st.title("Provisionamento OLT Huawei")

# Solicitar ao usuário que insira as informações de login 🔑
usuario = st.text_input("Insira o nome de usuário da OLT:")
senha = st.text_input("Insira a senha da OLT:", type="password")
port = st.text_input("Insira a porta de acesso da OLT (default: 23):", value="23")

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

# Mostrar os endereços IP disponíveis
st.subheader("Endereços IP disponíveis:")
endereco_escolhido = st.selectbox("Escolha um endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Botão para listar as ONUs disponíveis
if st.button("Listar ONUs Disponíveis"):
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
        st.text_area("ONUs disponíveis:", output)

        # Fechando a conexão Telnet
        tn.close()

    except Exception as e:
        st.error(f"Erro ao listar as ONUs: {e}")

# Campos para dados de provisionamento
slot_value = st.text_input("Informe o valor do campo SLOT:")
pon_value = st.text_input("Informe o valor do campo PON:")
id_value = st.text_input("Informe o valor do campo ID SERIAL:")
veip_value = st.text_input("Informe o valor do campo VEIP 30,300 ou 40,1022:")
vlan_value = st.text_input("Informe o valor do campo VLAN:")
desc_value = st.text_input("Informe o valor do campo DESCRIÇÃO:")
onu_value = st.text_input("Informe o valor do campo ID ONU:")

# Botão para iniciar o provisionamento
if st.button("Iniciar Provisionamento"):
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
        st.text_area("Saída do comando 'display ont optical-info':", output)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")