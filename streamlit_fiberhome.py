import streamlit as st
import telnetlib
import time
import re

# Configuração da interface do Streamlit
st.title("Provisionamento OLT Fiberhome")

# Solicitar ao usuário que insira as informações de login 🔑
usuario = st.text_input("Insira o nome de usuário da OLT:")
senha = st.text_input("Insira a senha da OLT:", type="password")
port = st.text_input("Insira a porta de acesso da OLT (default: 23):", value="23")
senha_enable = st.text_input("Insira a senha enable da OLT:", type="password")

# Endereços IP e seus respectivos nomes pré-definidos da OLT Fiberhome
enderecos_ip = {
    "🖥  OLT PINHEIRO ➡": "172.31.255.3",
    "🖥  OLT SÃO LUIS ➡": "172.30.247.100",
    "🖥  OLT SAO BENTO ➡": "172.31.254.2",
    "🖥  OLT TURIACU ➡": "172.31.200.254",
    "🖥  OLT VILA DA PAZ ➡": "172.31.187.2",
    "🖥  OLT SANTA HELENA ➡": "172.30.253.254",
    "🖥  OLT PEDRO DO ROSARIO ➡": "172.31.246.2",
    "🖥  OLT PACAS ➡": "172.31.191.2",
    "🖥  OLT PRESIDENTE SARNEY ➡": "172.31.252.3",
    "🖥  OLT CONECTA ➡": "177.66.195.157",
    "🖥  OLT SLP ➡": "172.31.254.2",
    "🖥  OLT MHZ ➡": "172.16.0.2",
    "🖥  OLT GNF ➡": "172.31.253.2"
}

# Mostrar os endereços IP disponíveis
st.subheader("Endereços IP disponíveis:")
endereco_escolhido = st.selectbox("Escolha um endereço IP:", list(enderecos_ip.keys()))
host = enderecos_ip[endereco_escolhido]

# Campos para dados de provisionamento
id_value = st.text_input("Informe o valor do campo ID:")
slot_value = st.text_input("Informe o valor do campo SLOT:")
pon_value = st.text_input("Informe o valor do campo PON:")
vlan_value = st.text_input("Informe o valor do campo VLAN:")
veip_value = st.text_input("Informe o valor do campo VEIP 1 ou 2:")
vlan_mode = st.text_input("Informe o valor do campo TAG ou TRANSPARENT:")
id_vlan_mode = st.text_input("Informe o valor do campo ID VLAN 0 ou 255:")

# Adicionar botão para listar as ONUs disponíveis
if st.button("Listar ONUs Disponíveis"):
    try:
        # Conectando à OLT Fiberhome via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        tn.read_until(b"Login: ")
        tn.write(usuario.encode('ascii') + b"\n")
        tn.read_until(b"Password: ")
        tn.write(senha.encode('ascii') + b"\n")

        # Habilitando o modo privilegiado
        tn.write(b"enable\n")
        tn.read_until(b"Password: ")
        tn.write(senha_enable.encode('ascii') + b"\n")

        # Executando o comando "show discovery slot all pon all"
        tn.write(b"cd onu\n")
        tn.write(b"show discovery slot all pon all\n")
        time.sleep(15)  # Aguardar tempo suficiente para o retorno ser obtido
        output = tn.read_very_eager().decode('ascii')
        st.text_area("ONUs disponíveis:", output)

        # Fechando a conexão Telnet
        tn.close()

    except Exception as e:
        st.error(f"Erro ao listar as ONUs: {e}")

# Botão para iniciar o provisionamento
if st.button("Iniciar Provisionamento"):
    try:
        # Conectando à OLT Fiberhome via Telnet
        tn = telnetlib.Telnet(host, port)

        # Fazendo login
        tn.read_until(b"Login: ")
        tn.write(usuario.encode('ascii') + b"\n")
        tn.read_until(b"Password: ")
        tn.write(senha.encode('ascii') + b"\n")

        # Habilitando o modo privilegiado
        tn.write(b"enable\n")
        tn.read_until(b"Password: ")
        tn.write(senha_enable.encode('ascii') + b"\n")

        # Executando o comando "show discovery slot all pon all"
        tn.write(b"cd onu\n")
        tn.write(b"show discovery slot all pon all\n")
        time.sleep(15)  # Aguardar tempo suficiente para o retorno ser obtido
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show discovery slot all pon all':", output)

        # Atualizando os campos em Dados de provisionamento
        tn.write("set whitelist phy_addr address {0} password null action delete\n".format(id_value).encode('ascii'))
        time.sleep(1)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'set whitelist delete':", output)

        tn.write("show authorization slot {} pon {}\n".format(slot_value, pon_value).encode('ascii'))
        time.sleep(1)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show authorization':", output)

        # Executando o comando vazio até a mensagem "Command execute success."
        timeout = 100  # Tempo máximo de espera (em segundos)
        start_time = time.time()
        while "Command execute success." not in output:
            tn.write(b"\n")
            time.sleep(0.5)
            output += tn.read_very_eager().decode('ascii')
            if time.time() - start_time > timeout:
                st.error("Timeout atingido. Não foi possível obter a mensagem 'Command execute success.'")
                break

        # Extrair números da coluna
        numbers = re.findall(r"\b(\d{1,3})\b", output)

        # Encontrar o próximo número pulado
        if numbers:
            numbers = list(map(int, numbers))  # Converter os números para inteiros
            min_number = min(numbers)
            max_number = max(numbers)
            sequence = list(range(min_number, max_number + 1))
            missing_numbers = list(set(sequence) - set(numbers))
            if missing_numbers:
                onu_value = str(min(missing_numbers))
            else:
                onu_value = str(max_number + 1)
        else:
            onu_value = "1"

        # Comandos de provisionamento
        comandos_provisionamento = [
            "set whitelist phy_addr address {0} password null action delete\n",
            "set whitelist phy_addr address {0} password null action add slot {1} pon {2} onu {3} type HG260",
            "cd lan",
            "set epon slot {1} pon {2} onu {3} port 1 service number 1",
            "set epon slot {1} pon {2} onu {3} port 1 service 1 vlan_mode {6} {7} 33024 {4}",
            "set epon slot {1} pon {2} onu {3} port 1 onuveip 1 33024 {4} 65535 33024 65535 65535 33024 65535 65535 0 {5} 65535 servn null service_type 1",
            "apply onu {1} {2} {3} vlan",
            "cd .."
        ]

        # Executando os comandos de provisionamento
        for comando_provisionamento in comandos_provisionamento:
            comando_provisionamento = comando_provisionamento.format(
                id_value, slot_value, pon_value, onu_value, vlan_value, veip_value, vlan_mode, id_vlan_mode
            )

            tn.write(comando_provisionamento.encode('ascii') + b"\n")
            time.sleep(1.5)
            output = tn.read_very_eager().decode('ascii')
            st.text_area(f"Saída do comando '{comando_provisionamento}':", output)

        # Executar o comando "show optic_module slot pon onu"
        time.sleep(5)
        tn.write("show optic_module slot {} pon {} onu {}\n".format(slot_value, pon_value, onu_value).encode('ascii'))
        time.sleep(10)
        output = tn.read_very_eager().decode('ascii')
        st.text_area("Saída do comando 'show optic_module slot pon onu':", output)

        # Fechando a conexão Telnet
        tn.close()

        st.success("Provisionamento concluído 😎 ✅ ✅ ✅")

    except Exception as e:
        st.error(f"Erro durante o provisionamento: {e}")
