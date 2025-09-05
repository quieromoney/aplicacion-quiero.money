import streamlit as st

# ==============================
# Configuración general
# ==============================
st.set_page_config(page_title="Quiero.Money", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "login_phone"
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "pin" not in st.session_state:
    st.session_state.pin = ""

# ==============================
# Pantalla 1: Ingreso celular
# ==============================
def login_phone():
    st.markdown("<h2 style='text-align:center; color:white;'>Ingresa tu número</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Usa tu celular de 10 dígitos</p>", unsafe_allow_html=True)

    phone = st.text_input("Celular (10 dígitos)", max_chars=10, label_visibility="collapsed")

    if st.button("Continuar", use_container_width=True):
        if len(phone) == 10 and phone.isdigit():
            st.session_state.phone = phone
            st.session_state.page = "login_pin"
            st.rerun()
        else:
            st.error("Por favor ingresa un número válido de 10 dígitos")

# ==============================
# Pantalla 2: Ingreso PIN
# ==============================
def login_pin():
    st.markdown("<h2 style='text-align:center; color:white;'>Escribe tu clave</h2>", unsafe_allow_html=True)

    # Mostrar casillas PIN
    pin_boxes = "".join(
        [f"<span style='display:inline-block;width:40px;height:40px;margin:5px;"
         f"border-radius:8px;background-color:#2c2c2c;color:white;"
         f"font-size:24px;text-align:center;line-height:40px;'>"
         f"{d if i < len(st.session_state.pin) else ''}</span>"
         for i, d in enumerate("12345")]
    )
    st.markdown(f"<div style='text-align:center;'>{pin_boxes}</div>", unsafe_allow_html=True)

    # Teclado numérico
    keypad = [["1", "2", "3"],
              ["4", "5", "6"],
              ["7", "8", "9"],
              ["", "0", "⌫"]]

    for row in keypad:
        cols = st.columns(3)
        for i, key in enumerate(row):
            if key == "":
                cols[i].write(" ")
            elif key == "⌫":
                if cols[i].button("⌫", use_container_width=True):
                    st.session_state.pin = st.session_state.pin[:-1]
                    st.rerun()
            else:
                if cols[i].button(key, use_container_width=True):
                    if len(st.session_state.pin) < 5:
                        st.session_state.pin += key
                        st.rerun()

    # Validación
    if len(st.session_state.pin) == 5:
        if st.session_state.pin == "12345":
            st.success("Bienvenido ✅")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("PIN incorrecto")
            st.session_state.pin = ""

# ==============================
# Dashboard principal
# ==============================
def dashboard():
    st.sidebar.title("Quiero.Money")
    menu = st.sidebar.radio(
        "Navegación",
        ["Panel de Control", "Recargar", "Comprar BTC", "Vender BTC", "Enviar", "Historial"]
    )

    if menu == "Panel de Control":
        st.title("Panel de Control")
        st.write("Aquí va tu saldo y el gráfico de BTC 📊")
    elif menu == "Recargar":
        st.title("Recargar saldo")
    elif menu == "Comprar BTC":
        st.title("Comprar Bitcoin")
    elif menu == "Vender BTC":
        st.title("Vender Bitcoin")
    elif menu == "Enviar":
        st.title("Enviar dinero")
    elif menu == "Historial":
        st.title("Historial de transacciones")

# ==============================
# Router de páginas
# ==============================
if st.session_state.page == "login_phone":
    login_phone()
elif st.session_state.page == "login_pin":
    login_pin()
elif st.session_state.page == "dashboard":
    dashboard()
