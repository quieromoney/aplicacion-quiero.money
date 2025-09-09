import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Quiero.Money", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "login_phone"
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "pin" not in st.session_state:
    st.session_state.pin = ""
if "saldo_cop" not in st.session_state:
    st.session_state.saldo_cop = 1_000_000
if "saldo_btc" not in st.session_state:
    st.session_state.saldo_btc = 0.05
if "historial" not in st.session_state:
    st.session_state.historial = []
if "btc_price" not in st.session_state:
    st.session_state.btc_price = 250_000_000

# ======================
# Precio BTC en COP
# ======================
def get_btc_price_cop():
    try:
        btc = yf.Ticker("BTC-USD")
        precio_usd = btc.history(period="1d")["Close"][-1]
        tasa_usd_cop = 4100  # puedes mejorar esto con API de tipo de cambio
        return precio_usd * tasa_usd_cop
    except:
        return st.session_state.btc_price

# ======================
# Historial
# ======================
def add_hist(tipo, cop, btc):
    st.session_state.historial.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "cop": cop,
        "btc": btc
    })

# ======================
# Login
# ======================
def login_phone():
    st.title("Quiero.Money")
    st.subheader("Ingresa tu celular (10 dígitos)")
    phone = st.text_input("Celular", max_chars=10)
    if st.button("Continuar", use_container_width=True):
        if len(phone) == 10 and phone.isdigit():
            st.session_state.phone = phone
            st.session_state.page = "login_pin"
            st.rerun()
        else:
            st.error("Número inválido")

def login_pin():
    st.title("Quiero.Money")
    st.subheader("Ingresa tu PIN (5 dígitos)")

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(st.session_state.pin[i] if i < len(st.session_state.pin) else "")

    keypad = [
        ["1","2","3"],
        ["4","5","6"],
        ["7","8","9"],
        ["","0","←"]
    ]

    for row in keypad:
        cols = st.columns(3)
        for i, key in enumerate(row):
            if key:
                if cols[i].button(key, use_container_width=True):
                    if key == "←":
                        st.session_state.pin = st.session_state.pin[:-1]
                    elif len(st.session_state.pin) < 5:
                        st.session_state.pin += key

    if len(st.session_state.pin) == 5:
        if st.session_state.pin == "12345":
            st.session_state.page = "panel"
            st.rerun()
        else:
            st.error("PIN incorrecto")
            st.session_state.pin = ""

# ======================
# Panel principal
# ======================
def panel():
    st.sidebar.title("Menú")
    if st.sidebar.button("Panel", use_container_width=True): st.session_state.page = "panel"; st.rerun()
    if st.sidebar.button("Comprar", use_container_width=True): st.session_state.page = "comprar"; st.rerun()
    if st.sidebar.button("Vender", use_container_width=True): st.session_state.page = "vender"; st.rerun()
    if st.sidebar.button("Recargar", use_container_width=True): st.session_state.page = "recargar"; st.rerun()
    if st.sidebar.button("Historial", use_container_width=True): st.session_state.page = "historial"; st.rerun()
    if st.sidebar.button("Wallet", use_container_width=True):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://developer.metamask.io/login">', unsafe_allow_html=True)

    st.title("Quiero.Money")

    st.session_state.btc_price = get_btc_price_cop()

    st.subheader("Saldo COP")
    st.info(f"${st.session_state.saldo_cop:,.0f}")

    st.subheader("Saldo BTC")
    st.info(f"{st.session_state.saldo_btc:.6f} BTC")

    st.subheader("Precio BTC")
    st.success(f"${st.session_state.btc_price:,.0f} COP")

    st.subheader("Gráfico BTC (TradingView)")
    st.components.v1.iframe(
        "https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=BTCUSD&interval=30&hidesidetoolbar=1&theme=dark&style=1&timezone=Etc/UTC&locale=es",
        height=400
    )

# ======================
# Comprar BTC
# ======================
def comprar():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"; st.rerun()

    st.title("Comprar BTC")
    monto = st.number_input("Monto en COP", min_value=0, step=10000)
    if st.button("Comprar", use_container_width=True):
        if monto > 0 and st.session_state.saldo_cop >= monto:
            btc = monto / st.session_state.btc_price
            st.session_state.saldo_cop -= monto
            st.session_state.saldo_btc += btc
            add_hist("Compra", -monto, btc)
            st.success(f"Compra realizada: {btc:.6f} BTC")
            st.session_state.page = "panel"; st.rerun()
        else:
            st.error("Fondos insuficientes")

# ======================
# Vender BTC
# ======================
def vender():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"; st.rerun()

    st.title("Vender BTC")
    monto_btc = st.number_input("Monto en BTC", min_value=0.0, step=0.001, format="%.6f")
    if st.button("Vender", use_container_width=True):
        if monto_btc > 0 and st.session_state.saldo_btc >= monto_btc:
            cop = monto_btc * st.session_state.btc_price
            st.session_state.saldo_btc -= monto_btc
            st.session_state.saldo_cop += cop
            add_hist("Venta", cop, -monto_btc)
            st.success(f"Venta realizada: ${cop:,.0f} COP")
            st.session_state.page = "panel"; st.rerun()
        else:
            st.error("Saldo BTC insuficiente")

# ======================
# Recargar COP
# ======================
def recargar():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"; st.rerun()

    st.title("Recargar COP")
    monto = st.number_input("Monto COP", min_value=0, step=1000)

    st.image("assets/nequi.png", use_container_width=True)
    if st.button("Recargar con Nequi", use_container_width=True):
        st.session_state.saldo_cop += monto
        add_hist("Recarga Nequi", monto, 0)
        st.success("Recarga realizada con Nequi")
        st.session_state.page = "panel"; st.rerun()

    st.image("assets/daviplata.png", use_container_width=True)
    if st.button("Recargar con Daviplata", use_container_width=True):
        st.session_state.saldo_cop += monto
        add_hist("Recarga Daviplata", monto, 0)
        st.success("Recarga realizada con Daviplata")
        st.session_state.page = "panel"; st.rerun()

# ======================
# Historial
# ======================
def historial():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"; st.rerun()

    st.title("Historial de Movimientos")
    if st.session_state.historial:
        df = pd.DataFrame(st.session_state.historial)
        st.table(df)
    else:
        st.info("No hay movimientos registrados aún.")

# ======================
# Router
# ======================
if st.session_state.page == "login_phone":
    login_phone()
elif st.session_state.page == "login_pin":
    login_pin()
elif st.session_state.page == "panel":
    panel()
elif st.session_state.page == "comprar":
    comprar()
elif st.session_state.page == "vender":
    vender()
elif st.session_state.page == "recargar":
    recargar()
elif st.session_state.page == "historial":
    historial()
