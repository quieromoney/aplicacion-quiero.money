import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import sqlite3
import json
import qrcode
import io
import base64
import requests
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Quiero.Money", layout="centered")

# Inicialización de la base de datos
def init_db():
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  phone TEXT UNIQUE,
                  pin TEXT,
                  name TEXT,
                  email TEXT,
                  saldo_cop REAL,
                  saldo_btc REAL)''')
    
    # Tabla de transacciones
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender_id INTEGER,
                  receiver_id INTEGER,
                  type TEXT,
                  amount_cop REAL,
                  amount_btc REAL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insertar usuario demo si no existe
    c.execute("SELECT COUNT(*) FROM users WHERE phone = '1234567890'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (phone, pin, name, email, saldo_cop, saldo_btc) VALUES (?, ?, ?, ?, ?, ?)",
                  ('1234567890', '12345', 'Usuario Demo', 'demo@quieno.money', 1000000, 0.05))
    
    conn.commit()
    conn.close()

# Inicializar la base de datos
init_db()

# Estado de la sesión
if "page" not in st.session_state:
    st.session_state.page = "login_phone"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_pin" not in st.session_state:
    st.session_state.user_pin = ""
if "btc_price" not in st.session_state:
    st.session_state.btc_price = 250_000_000

# ======================
# Funciones de base de datos
# ======================
def get_user_by_phone(phone):
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(phone, pin, name, email):
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (phone, pin, name, email, saldo_cop, saldo_btc) VALUES (?, ?, ?, ?, ?, ?)",
                  (phone, pin, name, email, 1000000, 0.02))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user_balance(user_id, cop_change, btc_change):
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    c.execute("UPDATE users SET saldo_cop = saldo_cop + ?, saldo_btc = saldo_btc + ? WHERE id = ?",
              (cop_change, btc_change, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    c.execute("SELECT saldo_cop, saldo_btc FROM users WHERE id = ?", (user_id,))
    balance = c.fetchone()
    conn.close()
    return balance

def add_transaction(sender_id, receiver_id, trans_type, amount_cop, amount_btc):
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (sender_id, receiver_id, type, amount_cop, amount_btc) VALUES (?, ?, ?, ?, ?)",
              (sender_id, receiver_id, trans_type, amount_cop, amount_btc))
    conn.commit()
    conn.close()

def get_user_transactions(user_id):
    conn = sqlite3.connect('quieno_money.db')
    c = conn.cursor()
    c.execute('''SELECT t.timestamp, t.type, u.name, t.amount_cop, t.amount_btc 
                 FROM transactions t 
                 LEFT JOIN users u ON (t.sender_id = u.id OR t.receiver_id = u.id) 
                 WHERE t.sender_id = ? OR t.receiver_id = ? 
                 ORDER BY t.timestamp DESC''', (user_id, user_id))
    transactions = c.fetchall()
    conn.close()
    return transactions

# ======================
# Precio BTC en tiempo real
# ======================
def get_btc_price_cop():
    try:
        # Intentar con CoinGecko primero
        try:
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5)
            if response.status_code == 200:
                precio_usd = response.json()['bitcoin']['usd']
                # Tasa de cambio aproximada USD a COP
                tasa_usd_cop = 4100
                return precio_usd * tasa_usd_cop
        except:
            # Fallback a Yahoo Finance
            btc = yf.Ticker("BTC-USD")
            precio_usd = btc.history(period="1d")["Close"][-1]
            tasa_usd_cop = 4100
            return precio_usd * tasa_usd_cop
    except:
        return st.session_state.btc_price

# ======================
# Generación de QR
# ======================
def generate_qr(user_id, amount_cop=0, amount_btc=0):
    # Crear datos para el QR
    qr_data = {
        "user_id": user_id,
        "amount_cop": amount_cop,
        "amount_btc": amount_btc,
        "timestamp": datetime.now().isoformat()
    }
    
    # Convertir a string JSON
    qr_data_str = json.dumps(qr_data)
    
    # Generar QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data_str)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a base64 para mostrar en Streamlit
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

# ======================
# Páginas de la aplicación
# ======================
def login_phone():
    st.title("Quiero.Money")
    st.subheader("Ingresa tu celular (10 dígitos)")
    phone = st.text_input("Celular", max_chars=10)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Iniciar sesión", use_container_width=True):
            if len(phone) == 10 and phone.isdigit():
                user = get_user_by_phone(phone)
                if user:
                    st.session_state.user_phone = phone
                    st.session_state.page = "login_pin"
                    st.rerun()
                else:
                    st.error("Usuario no encontrado. Regístrate primero.")
            else:
                st.error("Número inválido")
    
    with col2:
        if st.button("Crear cuenta", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

def register():
    st.title("Crear cuenta")
    
    with st.form("register_form"):
        phone = st.text_input("Celular (10 dígitos)", max_chars=10)
        name = st.text_input("Nombre completo")
        email = st.text_input("Email")
        pin = st.text_input("PIN (5 dígitos)", type="password", max_chars=5)
        
        submitted = st.form_submit_button("Crear cuenta")
        if submitted:
            if len(phone) == 10 and phone.isdigit() and len(pin) == 5 and pin.isdigit():
                user_id = create_user(phone, pin, name, email)
                if user_id:
                    st.success("Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
                    st.session_state.page = "login_phone"
                    st.rerun()
                else:
                    st.error("El número de celular ya está registrado.")
            else:
                st.error("Por favor, completa todos los campos correctamente.")
    
    if st.button("← Volver al login", use_container_width=True):
        st.session_state.page = "login_phone"
        st.rerun()

def login_pin():
    st.title("Quiero.Money")
    st.subheader("Ingresa tu PIN (5 dígitos)")
    
    user = get_user_by_phone(st.session_state.user_phone)
    
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(st.session_state.user_pin[i] if i < len(st.session_state.user_pin) else "")
    
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
                        st.session_state.user_pin = st.session_state.user_pin[:-1]
                    elif len(st.session_state.user_pin) < 5:
                        st.session_state.user_pin += key
    
    if len(st.session_state.user_pin) == 5:
        if user and st.session_state.user_pin == user[2]:  # user[2] es el PIN
            st.session_state.user_id = user[0]
            st.session_state.user_pin = ""
            st.session_state.page = "panel"
            st.rerun()
        else:
            st.error("PIN incorrecto")
            st.session_state.user_pin = ""

def panel():
    # Actualizar precio de BTC
    st.session_state.btc_price = get_btc_price_cop()
    
    # Obtener saldo actualizado
    saldo_cop, saldo_btc = get_user_balance(st.session_state.user_id)
    
    st.sidebar.title("Menú")
    if st.sidebar.button("Panel", use_container_width=True): 
        st.session_state.page = "panel"
        st.rerun()
    if st.sidebar.button("Enviar dinero", use_container_width=True): 
        st.session_state.page = "send_money"
        st.rerun()
    if st.sidebar.button("Recibir dinero", use_container_width=True): 
        st.session_state.page = "receive_money"
        st.rerun()
    if st.sidebar.button("Comprar BTC", use_container_width=True): 
        st.session_state.page = "comprar"
        st.rerun()
    if st.sidebar.button("Vender BTC", use_container_width=True): 
        st.session_state.page = "vender"
        st.rerun()
    if st.sidebar.button("Historial", use_container_width=True): 
        st.session_state.page = "historial"
        st.rerun()
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.user_phone = ""
        st.session_state.page = "login_phone"
        st.rerun()

    st.title("Quiero.Money")

    # Mostrar saldos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Saldo COP")
        st.info(f"${saldo_cop:,.0f}")
    with col2:
        st.subheader("Saldo BTC")
        st.info(f"{saldo_btc:.6f} BTC")

    st.subheader("Precio BTC en tiempo real")
    st.success(f"${st.session_state.btc_price:,.0f} COP")
    
    # Mini gráfico de precio (simplificado)
    st.line_chart(pd.DataFrame({
        'Precio BTC': [st.session_state.btc_price * 0.99, 
                       st.session_state.btc_price * 1.01, 
                       st.session_state.btc_price * 0.995, 
                       st.session_state.btc_price]
    }))

def send_money():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"
        st.rerun()
    
    st.title("Enviar dinero")
    
    # Obtener saldo actualizado
    saldo_cop, saldo_btc = get_user_balance(st.session_state.user_id)
    
    recipient_phone = st.text_input("Número de celular del destinatario", max_chars=10)
    amount = st.number_input("Monto a enviar (COP)", min_value=0, max_value=int(saldo_cop), step=10000)
    
    if st.button("Enviar", use_container_width=True):
        if amount > 0 and recipient_phone:
            # Verificar que el destinatario existe
            recipient = get_user_by_phone(recipient_phone)
            if recipient:
                if recipient[0] != st.session_state.user_id:  # No enviarse a sí mismo
                    # Actualizar saldos
                    update_user_balance(st.session_state.user_id, -amount, 0)
                    update_user_balance(recipient[0], amount, 0)
                    
                    # Registrar transacción
                    add_transaction(st.session_state.user_id, recipient[0], "Envío", -amount, 0)
                    add_transaction(recipient[0], st.session_state.user_id, "Recepción", amount, 0)
                    
                    st.success(f"Has enviado ${amount:,.0f} COP a {recipient[3]}")
                    st.session_state.page = "panel"
                    st.rerun()
                else:
                    st.error("No puedes enviarte dinero a ti mismo")
            else:
                st.error("El número de celular no está registrado")
        else:
            st.error("Monto inválido o destinatario no especificado")

def receive_money():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"
        st.rerun()
    
    st.title("Recibir dinero")
    
    amount = st.number_input("Monto a recibir (COP)", min_value=0, step=10000)
    
    # Generar QR
    qr_img_str = generate_qr(st.session_state.user_id, amount, 0)
    st.image(f"data:image/png;base64,{qr_img_str}", caption="Código QR para recibir pagos", use_column_width=True)
    
    st.info("Comparte este código QR para recibir pagos")

def comprar():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"
        st.rerun()

    st.title("Comprar BTC")
    
    # Obtener saldo actualizado
    saldo_cop, saldo_btc = get_user_balance(st.session_state.user_id)
    
    monto = st.number_input("Monto en COP", min_value=0, max_value=int(saldo_cop), step=10000)
    if st.button("Comprar", use_container_width=True):
        if monto > 0:
            btc = monto / st.session_state.btc_price
            update_user_balance(st.session_state.user_id, -monto, btc)
            add_transaction(st.session_state.user_id, None, "Compra BTC", -monto, btc)
            st.success(f"Compra realizada: {btc:.6f} BTC")
            st.session_state.page = "panel"
            st.rerun()
        else:
            st.error("Monto inválido")

def vender():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"
        st.rerun()

    st.title("Vender BTC")
    
    # Obtener saldo actualizado
    saldo_cop, saldo_btc = get_user_balance(st.session_state.user_id)
    
    monto_btc = st.number_input("Monto en BTC", min_value=0.0, max_value=float(saldo_btc), step=0.001, format="%.6f")
    if st.button("Vender", use_container_width=True):
        if monto_btc > 0:
            cop = monto_btc * st.session_state.btc_price
            update_user_balance(st.session_state.user_id, cop, -monto_btc)
            add_transaction(st.session_state.user_id, None, "Venta BTC", cop, -monto_btc)
            st.success(f"Venta realizada: ${cop:,.0f} COP")
            st.session_state.page = "panel"
            st.rerun()
        else:
            st.error("Monto inválido")

def historial():
    if st.button("← Volver", use_container_width=True):
        st.session_state.page = "panel"
        st.rerun()

    st.title("Historial de Transacciones")
    
    transactions = get_user_transactions(st.session_state.user_id)
    
    if transactions:
        df = pd.DataFrame(transactions, columns=['Fecha', 'Tipo', 'Usuario', 'Monto COP', 'Monto BTC'])
        st.dataframe(df)
    else:
        st.info("No hay transacciones registradas aún.")

# ======================
# Router
# ======================
if st.session_state.page == "login_phone":
    login_phone()
elif st.session_state.page == "register":
    register()
elif st.session_state.page == "login_pin":
    login_pin()
elif st.session_state.page == "panel":
    panel()
elif st.session_state.page == "send_money":
    send_money()
elif st.session_state.page == "receive_money":
    receive_money()
elif st.session_state.page == "comprar":
    comprar()
elif st.session_state.page == "vender":
    vender()
elif st.session_state.page == "historial":
    historial()