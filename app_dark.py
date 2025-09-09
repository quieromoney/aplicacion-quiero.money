
# app_dark.py - Streamlit app with improved panel, back arrows, and recarga logos
import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Quiero.Money", page_icon="💳", layout="centered")

# inject css
def load_css():
    try:
        with open("styles.css","r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.write("Error cargando CSS:", e)

load_css()

# --- State init ---
def init():
    if "page" not in st.session_state:
        st.session_state.page = "login-phone"
    if "phone" not in st.session_state:
        st.session_state.phone = ""
    if "pin" not in st.session_state:
        st.session_state.pin = ""
    if "saldo_cop" not in st.session_state:
        st.session_state.saldo_cop = 1_000_000.0
    if "saldo_btc" not in st.session_state:
        st.session_state.saldo_btc = 0.05
    if "btc_price" not in st.session_state:
        st.session_state.btc_price = 250_000_000.0
    if "hist" not in st.session_state:
        st.session_state.hist = []
init()

# --- helpers ---
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_hist(tipo, cop_delta, btc_delta, detalle=""):
    st.session_state.hist.insert(0, {
        "fecha": now(),
        "tipo": tipo,
        "cop_delta": cop_delta,
        "btc_delta": btc_delta,
        "cop_after": st.session_state.saldo_cop,
        "btc_after": st.session_state.saldo_btc,
        "detalle": detalle
    })

# --- Login pages ---
def login_phone():
    st.markdown('<div class="centered card login-card"><div class="brand">Quiero.<span class="accent">Money</span></div></div>', unsafe_allow_html=True)
    st.text_input("Ingresa tu celular", value=st.session_state.phone, placeholder="3001234567", key="phone_input")
    if st.button("Continuar", use_container_width=True, key="continue_phone"):
        raw = "".join([c for c in st.session_state.phone_input if c.isdigit()])
        if len(raw) == 10 and raw.startswith("3"):
            st.session_state.phone = raw
            st.session_state.page = "login-pin"
            st.rerun()
        else:
            st.error("Número inválido. Debe ser un celular colombiano de 10 dígitos que empiece por 3.")

def login_pin():
    st.markdown('<div class="centered card login-card"><div class="brand">Quiero.<span class="accent">Money</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="centered small-muted">Número: <strong>+57 {st.session_state.phone}</strong></div>', unsafe_allow_html=True)
    boxes_html = "".join([f'<div class="pin-box">{"•" if i < len(st.session_state.pin) else ""}</div>' for i in range(5)])
    st.markdown(f'<div class="pin-row">{boxes_html}</div>', unsafe_allow_html=True)
    keys = [1,2,3,4,5,6,7,8,9,"",0,"←"]
    rows = [keys[i:i+3] for i in range(0,len(keys),3)]
    for row in rows:
        cols = st.columns(3)
        for c,k in zip(cols,row):
            if k=="":
                c.markdown("&nbsp;", unsafe_allow_html=True)
            else:
                if c.button(str(k), use_container_width=True, key=f"key_{k}_{len(st.session_state.pin)}"):
                    if k=="←":
                        st.session_state.pin = st.session_state.pin[:-1]
                    else:
                        if len(st.session_state.pin)<5:
                            st.session_state.pin += str(k)
                    st.rerun()
    if st.button("Confirmar PIN", use_container_width=True):
        if st.session_state.pin == "12345":
            st.success("PIN correcto. Bienvenido.")
            st.session_state.page="panel"
            st.session_state.pin=""
            st.rerun()
        else:
            st.error("PIN incorrecto")
            st.session_state.pin=""

# nav button
def nav_button(label,target):
    if st.button(label, use_container_width=True, key=f"nav_{label}"):
        st.session_state.page=target
        st.rerun()

# tradingview iframe
def tradingview_iframe(symbol="BTCUSD", height=360):
    src = f"https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol={symbol}&interval=30&hidesidetoolbar=1&theme=dark&style=1&timezone=Etc/UTC&locale=es"
    html = f'<div class="chart-card"><iframe src="{src}" style="width:100%; height:{height}px;" frameborder="0"></iframe></div>'
    components.html(html, height=height+20)

# pages
def panel():
    st.markdown('<div class="centered card panel-card">', unsafe_allow_html=True)
    cols = st.columns(3)
    cols[0].markdown(f'<div class="metric-card"><div class="metric-title">Saldo COP</div><div class="metric-value">${st.session_state.saldo_cop:,.0f}</div></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div class="metric-card"><div class="metric-title">Saldo BTC</div><div class="metric-value">{st.session_state.saldo_btc:.8f} BTC</div></div>', unsafe_allow_html=True)
    cols[2].markdown(f'<div class="metric-card"><div class="metric-title">Precio BTC</div><div class="metric-value">${st.session_state.btc_price:,.0f} COP</div></div>', unsafe_allow_html=True)
    tradingview_iframe()
    st.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.header("Menú")
    nav_button("Panel","panel")
    nav_button("Comprar","comprar")
    nav_button("Vender","vender")
    nav_button("Recargar","recargar")
    nav_button("Historial","historial")

def comprar():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page="panel"; st.rerun()
    st.header("Comprar BTC")
    monto = st.number_input("Monto en COP", min_value=0, step=1000)
    if st.button("Comprar ahora", use_container_width=True):
        if monto>0 and monto<=st.session_state.saldo_cop:
            btc=monto/st.session_state.btc_price
            st.session_state.saldo_cop-=monto
            st.session_state.saldo_btc+=btc
            add_hist("Compra",-monto,btc)
            st.success("Compra realizada")
            st.session_state.page="panel"
            st.rerun()

def vender():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page="panel"; st.rerun()
    st.header("Vender BTC")
    btc_amt=st.number_input("Monto en BTC", min_value=0.0, format="%.8f", step=0.000001)
    if st.button("Vender ahora", use_container_width=True):
        if btc_amt>0 and btc_amt<=st.session_state.saldo_btc:
            cop=btc_amt*st.session_state.btc_price
            st.session_state.saldo_btc-=btc_amt
            st.session_state.saldo_cop+=cop
            add_hist("Venta",cop,-btc_amt)
            st.success("Venta realizada")
            st.session_state.page="panel"
            st.rerun()

def recargar():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page="panel"; st.rerun()
    st.header("Recargar COP")
    monto=st.number_input("Monto COP",min_value=0,step=1000)
    col1,col2=st.columns(2)
    with col1:
        st.image("assets/nequi.png", use_column_width=True)
        if st.button("Recargar con Nequi", use_container_width=True):
            st.session_state.saldo_cop+=monto
            add_hist("Recarga Nequi",monto,0)
            st.success("Recarga realizada con Nequi")
            st.session_state.page="panel"
            st.rerun()
    with col2:
        st.image("assets/daviplata.png", use_column_width=True)
        if st.button("Recargar con Daviplata", use_container_width=True):
            st.session_state.saldo_cop+=monto
            add_hist("Recarga Daviplata",monto,0)
            st.success("Recarga realizada con Daviplata")
            st.session_state.page="panel"
            st.rerun()

def historial_page():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page="panel"; st.rerun()
    st.header("Historial de movimientos")
    if not st.session_state.hist:
        st.info("No hay movimientos")
    else:
        df=pd.DataFrame(st.session_state.hist)
        st.dataframe(df,use_container_width=True)

# router
if st.session_state.page=="login-phone":
    login_phone()
elif st.session_state.page=="login-pin":
    login_pin()
elif st.session_state.page=="panel":
    panel()
elif st.session_state.page=="comprar":
    comprar()
elif st.session_state.page=="vender":
    vender()
elif st.session_state.page=="recargar":
    recargar()
elif st.session_state.page=="historial":
    historial_page()
else:
    panel()
