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
    pin_display = "".join(["⬜" for _ in range(5 - len(st.session_state.pin))])
    st.markdown(
        f"<h1 style='text-align:center; color:#EAEAEA;'>{st.session_state.pin}{pin_display}</h1>",
        unsafe_allow_html=True
    )

    # Teclado numérico
    cols = st.columns(3)
    for i, num in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]):
        if i % 3 == 0:
            cols = st.columns(3)
        if cols[i % 3].button(num, use_container_width=True):
            if len(st.session_state.pin) < 5:
                st.session_state.pin += num
                st.rerun()

    # Botón borrar
    if st.button("Borrar", use_container_width=True):
        st.session_state.pin = st.session_state.pin[:-1]
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
# Dashboard
# ==============================
def dashboard():
    st.title("Panel de Control")
    st.write("Aquí va el contenido de tu app...")

# ==============================
# Router de páginas
# ==============================
if st.session_state.page == "login_phone":
    login_phone()
elif st.session_state.page == "login_pin":
    login_pin()
elif st.session_state.page == "dashboard":
    dashboard()
