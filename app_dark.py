
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Quiero.Money", layout="wide")

# Estado de sesión
if "page" not in st.session_state:
    st.session_state.page = "login_phone"
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "pin" not in st.session_state:
    st.session_state.pin = ""

# ---------- Función: Login por celular ----------
def login_phone():
    st.markdown("<h2 style='text-align:center;'>Ingresa tu número</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray;'>Usa tu celular de 10 dígitos</p>", unsafe_allow_html=True)

    phone = st.text_input("Celular (10 dígitos)", value=st.session_state.phone, max_chars=10)

    if st.button("Continuar", use_container_width=True):
        if phone.isdigit() and len(phone) == 10:
            st.session_state.phone = phone
            st.session_state.page = "login_pin"
            st.rerun()
        else:
            st.error("Por favor ingresa un número de 10 dígitos válido.")

# ---------- Función: Login por PIN ----------
def login_pin():
    st.markdown("<h2 style='text-align:center;'>Escribe tu clave</h2>", unsafe_allow_html=True)

    # Mostrar casillas del PIN
    cols = st.columns(5, gap="small")
    for i in range(5):
        char = st.session_state.pin[i] if i < len(st.session_state.pin) else ""
        cols[i].markdown(f"<div class='pin-box'>{char}</div>", unsafe_allow_html=True)

    # Teclado numérico
    teclado = [
        ["1","2","3"],
        ["4","5","6"],
        ["7","8","9"],
        ["0","⌫"]
    ]

    for fila in teclado:
        cols = st.columns(len(fila), gap="small")
        for i, tecla in enumerate(fila):
            if cols[i].button(tecla, use_container_width=True):
                if tecla == "⌫":
                    st.session_state.pin = st.session_state.pin[:-1]
                else:
                    if len(st.session_state.pin) < 5:
                        st.session_state.pin += tecla

    # Validar PIN
    if len(st.session_state.pin) == 5:
        if st.session_state.pin == "12345":
            st.success("Bienvenido ✅")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("PIN incorrecto")
            st.session_state.pin = ""

    if st.button("Editar número", use_container_width=True):
        st.session_state.page = "login_phone"
        st.session_state.pin = ""
        st.rerun()

# ---------- Función: Dashboard ----------
def dashboard():
    st.markdown("## Panel de Control")

    # Datos ficticios
    saldo_cop = 100000
    saldo_btc = 0.0
    precio_btc = 111976.84

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo COP", f"${saldo_cop:,}")
    col2.metric("Saldo BTC", f"{saldo_btc:.8f}")
    col3.metric("Precio BTC", f"${precio_btc:,.2f} USD")

    # Gráfico de BTC (últimos 7 días)
    btc = yf.download("BTC-USD", period="7d", interval="1d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=btc.index, y=btc["Close"], mode="lines+markers", line=dict(color="yellow")))
    fig.update_layout(title="Evolución de Bitcoin (7 días)", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Render de páginas ----------
if st.session_state.page == "login_phone":
    login_phone()
elif st.session_state.page == "login_pin":
    login_pin()
elif st.session_state.page == "dashboard":
    dashboard()
