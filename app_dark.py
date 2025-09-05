
import os
import time
import streamlit as st
import pandas as pd

try:
    import plotly.express as px
except Exception:
    px = None

try:
    import yfinance as yf
except Exception:
    yf = None

st.set_page_config(page_title="Quiero.Money", page_icon="💳", layout="wide")

# ---------- Cargar estilos ----------
CSS_FILE = "styles.css"
if os.path.exists(CSS_FILE):
    with open(CSS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Estado inicial ----------
def init_state():
    if "initialized" not in st.session_state:
        # Saldos base
        st.session_state.saldo_cop = 100_000.0
        st.session_state.saldo_btc = 0.0
        st.session_state.saldo_nequi = 500_000.0
        st.session_state.saldo_daviplata = 500_000.0
        st.session_state.hist = []
        # Login 2 pasos
        st.session_state.authenticated = False
        st.session_state.login_step = "phone"  # phone -> pin
        st.session_state.phone_tmp = ""
        st.session_state.page = "Panel de Control"
        st.session_state.initialized = True

init_state()

# ---------- Utils ----------
def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def add_hist(tipo, detalle, delta_cop=0.0, delta_btc=0.0):
    st.session_state.hist.insert(0, {
        "fecha": now(),
        "tipo": tipo,
        "detalle": detalle,
        "Δ COP": delta_cop,
        "Δ BTC": delta_btc,
        "COP": st.session_state.saldo_cop,
        "BTC": st.session_state.saldo_btc,
        "Nequi": st.session_state.saldo_nequi,
        "Daviplata": st.session_state.saldo_daviplata,
    })

def get_btc_price_usd() -> float:
    price = 30500.0
    if yf is not None:
        try:
            data = yf.Ticker("BTC-USD").history(period="2d", interval="1h")
            if not data.empty and "Close" in data:
                price = float(data["Close"].iloc[-1])
        except Exception:
            pass
    return float(price)

def btc_history_df(days=7):
    if yf is not None:
        try:
            hist = yf.Ticker("BTC-USD").history(period=f"{days}d")
            if not hist.empty and "Close" in hist:
                df = hist[["Close"]].reset_index().rename(
                    columns={"Date":"Fecha","Close":"BTC_USD"})
                return df
        except Exception:
            pass
    # Fallback mock
    rng = pd.date_range(end=pd.Timestamp.today(), periods=days)
    vals = [100000 + i*1500 for i in range(days)]
    return pd.DataFrame({"Fecha": rng, "BTC_USD": vals})

# ---------- Login (2 pasos) ----------
def login_phone():
    st.markdown("""
    <div class="login-container">
      <div class="login-brand">Quiero<span class="dot">.</span>Money</div>
      <h1 class="login-title">Ingresa tu número</h1>
      <p class="login-subtitle">Usa tu celular de 10 dígitos</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("phone_form", clear_on_submit=False):
        phone = st.text_input("Celular (10 dígitos)",
                              value=st.session_state.phone_tmp,
                              max_chars=10,
                              help="Solo números",
                              key="phone_input")
        cont = st.form_submit_button("Continuar", use_container_width=True)
        if cont:
            if phone.isdigit() and len(phone) == 10:
                st.session_state.phone_tmp = phone
                st.session_state.login_step = "pin"
                st.experimental_rerun()
            else:
                st.error("Ingresa un número válido de 10 dígitos.")

def login_pin():
    st.markdown("""
    <div class="login-container">
      <div class="login-brand">Quiero<span class="dot">.</span>Money</div>
      <h1 class="login-title">Escribe tu PIN</h1>
      <p class="login-subtitle">PIN de 5 dígitos</p>
    </div>
    """, unsafe_allow_html=True)

    # PIN esperado
    PIN_CORRECTO = "12345"

    # Inputs individuales tipo OTP
    cols = st.columns(5, gap="small")
    pin_digits = []
    for i, c in enumerate(cols):
        with c:
            d = st.text_input(f"{i+1}", max_chars=1, key=f"pin_{i}", label_visibility="collapsed")
            # Forzar solo número
            if d and not d.isdigit():
                st.session_state[f"pin_{i}"] = ""
                d = ""
            pin_digits.append(d or "")

    # Botones
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("Editar número", use_container_width=True):
            st.session_state.login_step = "phone"
            st.experimental_rerun()
    with c2:
        if st.button("Ingresar", use_container_width=True):
            pin = "".join(pin_digits)
            if pin == PIN_CORRECTO:
                st.session_state.authenticated = True
                st.success("Bienvenido ✅")
                time.sleep(0.4)
                st.experimental_rerun()
            else:
                st.error("PIN incorrecto. Vuelve a intentarlo.")

# ---------- UI helpers ----------
def sidebar_nav():
    with st.sidebar:
        st.markdown("<div class='brand'>Quiero.Money</div>", unsafe_allow_html=True)
        col = st.container()
        if col.button("Panel de Control", use_container_width=True): st.session_state.page = "Panel de Control"
        if col.button("Recargar", use_container_width=True): st.session_state.page = "Recargar"
        if col.button("Comprar BTC", use_container_width=True): st.session_state.page = "Comprar BTC"
        if col.button("Vender BTC", use_container_width=True): st.session_state.page = "Vender BTC"
        if col.button("Enviar", use_container_width=True): st.session_state.page = "Enviar"
        if col.button("Historial", use_container_width=True): st.session_state.page = "Historial"

def metric_card(title, value, suffix=""):
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}{suffix}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Páginas ----------
def page_panel():
    st.markdown("<h1 class='page-title'>Panel de Control</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1], gap="large")
    with c1: metric_card("Saldo COP", f"${st.session_state.saldo_cop:,.0f}")
    with c2: metric_card("Saldo BTC", f"{st.session_state.saldo_btc:,.8f}")
    with c3: metric_card("Precio BTC", f"${get_btc_price_usd():,.2f}", " USD")

    # Tarjeta con gráfico
    df = btc_history_df(7)
    if px is not None:
        fig = px.line(df, x="Fecha", y="BTC_USD", title="Evolución de Bitcoin (7 días)")
        fig.update_traces(line_color="#FFD33D")
        fig.update_layout(
            margin=dict(l=8,r=8,t=35,b=8),
            height=360,
            paper_bgcolor="#1C1F24",
            plot_bgcolor="#1C1F24",
            font_color="#EAEAF0",
            xaxis_title=None, yaxis_title="USD"
        )
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.line_chart(df.set_index("Fecha")["BTC_USD"])
        st.markdown("</div>", unsafe_allow_html=True)

def page_recargar():
    st.markdown("<h1 class='page-title'>Recargar</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### Nequi")
        monto = st.number_input("Monto a recargar desde Nequi (COP)", min_value=1, step=1000)
        if st.button("Confirmar recarga desde Nequi", use_container_width=True):
            if monto <= st.session_state.saldo_nequi:
                st.session_state.saldo_nequi -= monto
                st.session_state.saldo_cop += monto
                add_hist("Recarga", f"Desde Nequi +${monto:,.0f} COP", delta_cop=monto)
                st.success("Recarga aplicada.")
            else:
                st.error("Saldo insuficiente en Nequi.")
        metric_card("Saldo Nequi", f"${st.session_state.saldo_nequi:,.0f}")

    with c2:
        st.markdown("### Daviplata")
        monto2 = st.number_input("Monto a recargar desde Daviplata (COP)", min_value=1, step=1000, key="davim")
        if st.button("Confirmar recarga desde Daviplata", use_container_width=True, key="davic"):
            if monto2 <= st.session_state.saldo_daviplata:
                st.session_state.saldo_daviplata -= monto2
                st.session_state.saldo_cop += monto2
                add_hist("Recarga", f"Desde Daviplata +${monto2:,.0f} COP", delta_cop=monto2)
                st.success("Recarga aplicada.")
            else:
                st.error("Saldo insuficiente en Daviplata.")
        metric_card("Saldo Daviplata", f"${st.session_state.saldo_daviplata:,.0f}")

def page_comprar():
    st.markdown("<h1 class='page-title'>Comprar Bitcoin</h1>", unsafe_allow_html=True)
    precio = get_btc_price_usd()
    c1, c2 = st.columns([1,1], gap="large")
    with c1:
        monto = st.number_input("Monto en COP a comprar", min_value=1, step=1000)
        if st.button("Confirmar compra", use_container_width=True):
            if monto <= st.session_state.saldo_cop:
                btc = monto / precio
                st.session_state.saldo_cop -= monto
                st.session_state.saldo_btc += btc
                add_hist("Compra BTC", f"Comprados {btc:.8f} BTC a ${precio:,.2f} USD",
                         delta_cop=-monto, delta_btc=btc)
                st.success(f"Compra realizada: +{btc:.8f} BTC")
            else:
                st.error("Saldo COP insuficiente.")
        metric_card("Saldo COP", f"${st.session_state.saldo_cop:,.0f}")
        metric_card("Saldo BTC", f"{st.session_state.saldo_btc:,.8f}")
    with c2:
        df = btc_history_df(30)
        if px is not None:
            fig = px.line(df, x="Fecha", y="BTC_USD", title="BTC últimos 30 días")
            fig.update_traces(line_color="#FFD33D")
            fig.update_layout(margin=dict(l=8,r=8,t=35,b=8), height=360,
                              paper_bgcolor="#15171A", plot_bgcolor="#15171A", font_color="#EAEAF0")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(df.set_index("Fecha")["BTC_USD"])

def page_vender():
    st.markdown("<h1 class='page-title'>Vender Bitcoin</h1>", unsafe_allow_html=True)
    precio = get_btc_price_usd()
    c1, c2 = st.columns([1,1], gap="large")
    with c1:
        monto_btc = st.number_input("Monto en BTC a vender", min_value=0.0, step=0.0001, format="%.8f")
        if st.button("Confirmar venta", use_container_width=True):
            if monto_btc <= st.session_state.saldo_btc:
                cop = monto_btc * precio
                st.session_state.saldo_btc -= monto_btc
                st.session_state.saldo_cop += cop
                add_hist("Venta BTC", f"Vendidos {monto_btc:.8f} BTC a ${precio:,.2f} USD",
                         delta_cop=cop, delta_btc=-monto_btc)
                st.success(f"Venta realizada: +${cop:,.0f} COP")
            else:
                st.error("Saldo BTC insuficiente.")
        metric_card("Saldo BTC", f"{st.session_state.saldo_btc:,.8f}")
        metric_card("Saldo COP", f"${st.session_state.saldo_cop:,.0f}")
    with c2:
        df = btc_history_df(30)
        if px is not None:
            fig = px.line(df, x="Fecha", y="BTC_USD", title="BTC últimos 30 días")
            fig.update_traces(line_color="#FFD33D")
            fig.update_layout(margin=dict(l=8,r=8,t=35,b=8), height=360,
                              paper_bgcolor="#15171A", plot_bgcolor="#15171A", font_color="#EAEAF0")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(df.set_index("Fecha")["BTC_USD"])

def page_enviar():
    st.markdown("<h1 class='page-title'>Enviar</h1>", unsafe_allow_html=True)
    st.info("Sección demo para futuras transferencias internas.")

def page_historial():
    st.markdown("<h1 class='page-title'>Historial</h1>", unsafe_allow_html=True)
    if len(st.session_state.hist) == 0:
        st.info("No hay movimientos aún.")
        return
    df = pd.DataFrame(st.session_state.hist)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------- Render ----------
if not st.session_state.authenticated:
    # Flujo 2 pasos: primero celular, luego pin
    if st.session_state.login_step == "phone":
        login_phone()
    else:
        login_pin()
else:
    sidebar_nav()
    page = st.session_state.page
    if page == "Panel de Control": page_panel()
    elif page == "Recargar": page_recargar()
    elif page == "Comprar BTC": page_comprar()
    elif page == "Vender BTC": page_vender()
    elif page == "Enviar": page_enviar()
    elif page == "Historial": page_historial()
