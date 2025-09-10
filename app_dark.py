# app_dark.py (versión integrada con diseño y wallet page)
import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import json
import qrcode
import io
import base64
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="Quiero.Money", layout="centered")

# ---- load css
def load_local_css(file_path="styles.css"):
    p = Path(file_path)
    if p.exists():
        css = p.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
load_local_css("styles.css")

# ---- DB init
DB_FILE = "quieno_money.db"
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  phone TEXT UNIQUE,
                  pin TEXT,
                  name TEXT,
                  email TEXT,
                  saldo_cop REAL,
                  saldo_btc REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender_id INTEGER,
                  receiver_id INTEGER,
                  type TEXT,
                  amount_cop REAL,
                  amount_btc REAL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("SELECT COUNT(*) FROM users WHERE phone = '1234567890'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (phone, pin, name, email, saldo_cop, saldo_btc) VALUES (?, ?, ?, ?, ?, ?)",
                  ('1234567890', '12345', 'Usuario Demo', 'demo@quieno.money', 1000000, 0.05))
    conn.commit()
    conn.close()
init_db()

# ---- session state defaults
if "page" not in st.session_state: st.session_state.page = "login_phone"
if "user_id" not in st.session_state: st.session_state.user_id = None
if "user_phone" not in st.session_state: st.session_state.user_phone = ""
if "user_pin" not in st.session_state: st.session_state.user_pin = ""
if "btc_price" not in st.session_state: st.session_state.btc_price = 250_000_000

# ---- DB helpers
def get_user_by_phone(phone):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    u = c.fetchone()
    conn.close()
    return u

def create_user(phone, pin, name, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (phone, pin, name, email, saldo_cop, saldo_btc) VALUES (?, ?, ?, ?, ?, ?)",
                  (phone, pin, name, email, 1000000, 0.02))
        conn.commit()
        uid = c.lastrowid
        conn.close()
        return uid
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user_balance(user_id, cop_change, btc_change):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET saldo_cop = saldo_cop + ?, saldo_btc = saldo_btc + ? WHERE id = ?",
              (cop_change, btc_change, user_id))
    conn.commit()
    conn.close()

def add_transaction(sender_id, receiver_id, trans_type, amount_cop, amount_btc):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (sender_id, receiver_id, type, amount_cop, amount_btc) VALUES (?, ?, ?, ?, ?)",
              (sender_id, receiver_id, trans_type, amount_cop, amount_btc))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT saldo_cop, saldo_btc FROM users WHERE id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r if r else (0,0)

def get_user_transactions(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""SELECT id, timestamp, type, sender_id, receiver_id, amount_cop, amount_btc
                 FROM transactions
                 WHERE sender_id = ? OR receiver_id = ?
                 ORDER BY timestamp DESC""", (user_id, user_id))
    rows = c.fetchall()
    conn.close()
    return rows

# ---- BTC price real time + history
def get_btc_price_and_series(days=7):
    try:
        # prefer CoinGecko for current price
        resp = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=cop&days="+str(days), timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            prices = [p[1] for p in data.get("prices",[])]
            current = prices[-1] if prices else st.session_state.btc_price
            series = prices
            st.session_state.btc_price = current
            return current, series
    except Exception:
        pass
    # fallback to yfinance for approximate USD -> COP
    try:
        ticker = yf.Ticker("BTC-USD")
        hist = ticker.history(period=f"{days}d", interval="1d")["Close"]
        usd_to_cop = 4100
        series = (hist.astype(float) * usd_to_cop).tolist()
        current = series[-1] if series else st.session_state.btc_price
        st.session_state.btc_price = current
        return current, series
    except Exception:
        return st.session_state.btc_price, [st.session_state.btc_price]*days

# ---- QR gen
def generate_qr_base64(payload):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ---- UI pages
def login_phone():
    st.markdown('<div class="brand">Quiero.Money</div>', unsafe_allow_html=True)
    st.subheader("Inicio de sesión")
    phone = st.text_input("Celular (10 dígitos)", max_chars=10, key="login_phone")
    c1, c2 = st.columns([2,1])
    with c1:
        if st.button("Iniciar sesión", key="btn_login", use_container_width=True):
            if len(phone)==10 and phone.isdigit():
                u = get_user_by_phone(phone)
                if u:
                    st.session_state.user_phone = phone
                    st.session_state.page = "login_pin"
                    st.experimental_rerun()
                else:
                    st.error("Usuario no registrado. Haz click en Crear cuenta.")
            else:
                st.error("Número inválido")
    with c2:
        if st.button("Crear cuenta", key="btn_to_register", use_container_width=True):
            st.session_state.page = "register"
            st.experimental_rerun()

def register():
    st.title("Crear cuenta")
    with st.form("form_reg"):
        phone = st.text_input("Celular (10 dígitos)", max_chars=10)
        name = st.text_input("Nombre completo")
        email = st.text_input("Email")
        pin = st.text_input("PIN (5 dígitos)", type="password", max_chars=5)
        if st.form_submit_button("Crear cuenta"):
            if len(phone)==10 and phone.isdigit() and len(pin)==5 and pin.isdigit():
                uid = create_user(phone, pin, name, email)
                if uid:
                    st.success("Cuenta creada. Ahora inicia sesión.")
                    st.session_state.page = "login_phone"
                    st.experimental_rerun()
                else:
                    st.error("El celular ya está registrado.")
            else:
                st.error("Completa correctamente los campos.")

    if st.button("← Volver"):
        st.session_state.page = "login_phone"
        st.experimental_rerun()

def login_pin():
    st.title("Ingrese PIN")
    st.write("Introduce tu PIN de 5 dígitos")
    user = get_user_by_phone(st.session_state.user_phone)
    # keypad simple
    if "pin_buffer" not in st.session_state: st.session_state.pin_buffer = ""
    cols = st.columns(3)
    for row in [["1","2","3"],["4","5","6"],["7","8","9"],["←","0","OK"]]:
        cols = st.columns(3)
        for key in row:
            if cols[row.index(key)].button(key, use_container_width=True):
                if key == "←":
                    st.session_state.pin_buffer = st.session_state.pin_buffer[:-1]
                elif key == "OK":
                    # verify
                    if user and st.session_state.pin_buffer == user[2]:
                        st.session_state.user_id = user[0]
                        st.session_state.page = "panel"
                        st.session_state.pin_buffer = ""
                        st.experimental_rerun()
                    else:
                        st.error("PIN incorrecto")
                        st.session_state.pin_buffer = ""
                else:
                    if len(st.session_state.pin_buffer) < 5:
                        st.session_state.pin_buffer += key
    st.write("PIN:", "*" * len(st.session_state.pin_buffer))

def render_sidebar():
    st.sidebar.title("Menú")
    options = ["Panel","Enviar","Recibir","Comprar BTC","Vender BTC","Recargar","Historial","Wallet","Cerrar sesión"]
    choice = st.sidebar.radio("Navegación", options)
    # map
    mapping = {
        "Panel":"panel",
        "Enviar":"send_money",
        "Recibir":"receive_money",
        "Comprar BTC":"comprar",
        "Vender BTC":"vender",
        "Recargar":"recargar",
        "Historial":"historial",
        "Wallet":"wallet",
        "Cerrar sesión":"logout"
    }
    st.session_state.page = mapping.get(choice, "panel")

def panel():
    current_price, series = get_btc_price_and_series(days=7)
    s_cop, s_btc = get_user_balance(st.session_state.user_id)
    st.markdown('<div class="brand">Quiero.Money</div>', unsafe_allow_html=True)
    st.subheader("Panel de control")
    c1,c2,c3 = st.columns([1,1,1])
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Saldo COP</div><div class="metric-value">${s_cop:,.0f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Saldo BTC</div><div class="metric-value">{s_btc:.6f} BTC</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Precio BTC</div><div class="metric-value">${current_price:,.0f} COP</div></div>', unsafe_allow_html=True)

    st.subheader("Gráfico BTC (últimos 7 días)")
    df = pd.DataFrame({"Precio": series})
    st.line_chart(df)

def send_money():
    st.title("Enviar dinero")
    s_cop, s_btc = get_user_balance(st.session_state.user_id)
    recipient = st.text_input("Teléfono destinatario", max_chars=10)
    amount = st.number_input("Monto (COP)", min_value=0, max_value=int(s_cop), step=5000)
    if st.button("Enviar", use_container_width=True):
        if amount > 0 and recipient:
            r = get_user_by_phone(recipient)
            if r:
                if r[0] != st.session_state.user_id:
                    update_user_balance(st.session_state.user_id, -amount, 0)
                    update_user_balance(r[0], amount, 0)
                    add_transaction(st.session_state.user_id, r[0], "Envío", -amount, 0)
                    add_transaction(r[0], st.session_state.user_id, "Recepción", amount, 0)
                    st.success("Envío exitoso")
                else:
                    st.error("No puedes enviarte a ti mismo")
            else:
                st.error("Destinatario no encontrado")
        else:
            st.error("Monto o destinatario inválido")

def receive_money():
    st.title("Recibir dinero")
    amount = st.number_input("Monto a recibir (COP)", min_value=0, step=5000)
    if st.button("Generar QR"):
        payload = {"user_id": st.session_state.user_id, "amount_cop": amount, "ts": datetime.now().isoformat()}
        img_b64 = generate_qr_base64(payload)
        st.image(f"data:image/png;base64,{img_b64}", caption="Escanea para pagar", use_column_width=False)

def comprar():
    st.title("Comprar BTC")
    s_cop, s_btc = get_user_balance(st.session_state.user_id)
    monto = st.number_input("Monto en COP", min_value=0, max_value=int(s_cop), step=5000)
    if st.button("Comprar"):
        if monto>0:
            price, _ = get_btc_price_and_series(days=1)
            btc_amount = monto/price
            update_user_balance(st.session_state.user_id, -monto, btc_amount)
            add_transaction(st.session_state.user_id, None, "Compra BTC", -monto, btc_amount)
            st.success(f"Comprado {btc_amount:.6f} BTC")

def vender():
    st.title("Vender BTC")
    s_cop,s_btc = get_user_balance(st.session_state.user_id)
    btc_amount = st.number_input("Monto en BTC", min_value=0.0, max_value=float(s_btc), step=0.001, format="%.6f")
    if st.button("Vender"):
        if btc_amount>0:
            price, _ = get_btc_price_and_series(days=1)
            cop = btc_amount*price
            update_user_balance(st.session_state.user_id, cop, -btc_amount)
            add_transaction(st.session_state.user_id, None, "Venta BTC", cop, -btc_amount)
            st.success(f"Vendiste {btc_amount:.6f} BTC -> ${cop:,.0f} COP")

def recargar():
    st.title("Recargar saldo")
    st.markdown("Selecciona método de recarga:")
    c1, c2 = st.columns(2)
    # assets/daviplata.png and assets/nequi.png expected
    dav_path = Path("assets/daviplata.png")
    nequi_path = Path("assets/nequi.png")
    with c1:
        if dav_path.exists():
            st.image(str(dav_path), width=160)
        st.markdown("**Daviplata**")
        if st.button("Recargar con Daviplata"):
            st.info("Instrucciones: transfiera a la cuenta... (simulado)")
    with c2:
        if nequi_path.exists():
            st.image(str(nequi_path), width=160)
        st.markdown("**Nequi**")
        if st.button("Recargar con Nequi"):
            st.info("Instrucciones: transfiera a la cuenta... (simulado)")

    # input para simular recarga
    monto = st.number_input("Monto a recargar (COP)", min_value=0, step=5000)
    if st.button("Simular recarga"):
        if monto>0:
            update_user_balance(st.session_state.user_id, monto, 0)
            add_transaction(None, st.session_state.user_id, "Recarga", monto, 0)
            st.success(f"Recargaste ${monto:,.0f} COP")

def historial():
    st.title("Historial")
    rows = get_user_transactions(st.session_state.user_id)
    if not rows:
        st.info("No hay movimientos.")
        return
    df = pd.DataFrame(rows, columns=["id","ts","tipo","sender","receiver","monto_cop","monto_btc"])
    df['ts'] = pd.to_datetime(df['ts'])
    st.dataframe(df.sort_values('ts', ascending=False))

def wallet():
    st.title("Wallet / MetaMask")
    st.markdown("**Conectar MetaMask** (instrucciones):")
    st.markdown("""
    1. Abre https://metamask.io/es y instala la extensión si no la tienes.  
    2. Abre MetaMask en el navegador y copia tu dirección pública.  
    3. Pega la dirección abajo para que la aplicación la muestre (esto **no** firma ni conecta la extensión).
    """)
    if st.button("Abrir MetaMask (sitio oficial)", use_container_width=True):
        js = "window.open('https://metamask.io/es', '_blank').focus();"
        st.components.v1.html(f"<script>{js}</script>", height=0)
    address = st.text_input("Pega aquí tu dirección pública (opcional)")
    if address:
        st.markdown(f"Dirección: `{address}`")

def logout():
    st.session_state.user_id = None
    st.session_state.user_phone = ""
    st.session_state.page = "login_phone"
    st.experimental_rerun()

# ---- main router
def main():
    if not st.session_state.user_id:
        # show login / register flows
        if st.session_state.page == "login_phone": login_phone()
        elif st.session_state.page == "register": register()
        elif st.session_state.page == "login_pin": login_pin()
        return

    # authenticated
    render_sidebar()
    page = st.session_state.page
    if page == "panel": panel()
    elif page == "send_money" or page == "send": send_money()
    elif page == "receive_money" or page == "recibir": receive_money()
    elif page == "comprar": comprar()
    elif page == "vender": vender()
    elif page == "recargar": recargar()
    elif page == "historial": historial()
    elif page == "wallet": wallet()
    elif page == "logout": logout()
    else:
        panel()

if __name__ == "__main__":
    main()
