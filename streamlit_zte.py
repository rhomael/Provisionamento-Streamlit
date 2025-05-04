import streamlit as st
import telnetlib
import time

# Configuração da interface do Streamlit
st.title("Provisionamento OLT ZTE")

# Solicitar ao usuário que insira as informações de login 🔑
usuario = st.text_input("Insira o nome de usuário da OLT:")
senha = st.text_input("Insira a senha da OLT:", type="password")
port = st.text_input("Insira a porta de acesso da OLT (default: 23):", value="23")

# Endereços IP e seus respectivos nomes pré-definidos da OLT ZTE
enderecos_ip = {
    "🖥  OLT ZTE PARAISO ➡": "172.31.188.2",
    "🖥  OLT ZTE PALMEIRANDIA ➡": "172.31.239.2"
}

# Mostrar os endereços IP disponíveis
st.subheader("Endereços IP disponíveis:")
endereco_escolhido = st.selectbox("Escolha um endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Botão para listar as ONUs disponíveis
if st.button("Listar ONUs Disponíveis"):
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
        st.text_area("Saída do comando 'show pon onu uncfg':", output)

        # Fechando a conexão Telnet
        tn.close()

    except Exception as e:
        st.error(f"Erro ao listar as ONUs: {e}")

# Campos para dados de provisionamento
pon_value = st.text_input("Informe o valor do campo PON:")
id_onu = st.text_input("Informe o valor do campo ID ONU:")
type_onu = st.text_input("Informe o campo type ZTE-F643 ou ZTE-F660:")
sn_onu = st.text_input("Informe o campo da SERIAL:")
vlan_value = st.text_input("Informe o campo da VLAN:")
name_onu = st.text_input("Informe o nome do CLIENTE:")

# Botão para iniciar o provisionamento
if st.button("Iniciar Provisionamento"):
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
        st.text_area("Saída do comando 'show gpon onu state':", output)

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
        st.text_area("Saída do comando 'show pon power attenuation':", output)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")