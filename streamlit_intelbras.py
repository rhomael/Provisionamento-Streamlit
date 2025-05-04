import streamlit as st
import telnetlib
import time

# Configuração da interface do Streamlit
st.title("Provisionamento OLT Intelbras")

# Solicitar ao usuário que insira as informações de login 🔑
usuario = st.text_input("Insira o nome de usuário da OLT:")
senha = st.text_input("Insira a senha da OLT:", type="password")
port = st.text_input("Insira a porta de acesso da OLT (default: 23):", value="23")

# Endereços IP e seus respectivos nomes pré-definidos da OLT Intelbras
enderecos_ip = {
    "🖥  OLT INTELBRAS PARAISO": "172.31.188.2",
    "🖥  OLT INTELBRAS BOM_VIVER ➡": "172.31.248.2",
    "🖥  OLT INTELBRAS FORTALEZA ➡": "172.31.194.2",
    "🖥  OLT INTELBRAS 3 FUROS ➡": "172.31.195.2"
}

# Mostrar os endereços IP disponíveis
st.subheader("Endereços IP disponíveis:")
endereco_escolhido = st.selectbox("Escolha um endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Botão para listar as ONUs disponíveis
if st.button("Listar ONUs Disponíveis"):
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
        st.text_area("ONUs disponíveis:", output)

        # Fechando a conexão Telnet
        tn.close()

    except Exception as e:
        st.error(f"Erro ao listar as ONUs: {e}")

# Campos para dados de provisionamento
sn_value = st.text_input("Informe o valor do campo ID Serial:")
pon_value = st.text_input("Informe o valor do campo PON:")
id_value = st.text_input("Informe o valor do campo ID:")
desc_value = st.text_input("Informe o valor do campo Nome:")
veip_value = st.text_input("Informe o valor do campo VEIP:")

# Botão para iniciar o provisionamento
if st.button("Iniciar Provisionamento"):
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
        st.text_area("Saída do comando 'show ont brief sn string-hex':", output)

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
        st.text_area("Saída do comando 'show ont optical-info':", output)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")
