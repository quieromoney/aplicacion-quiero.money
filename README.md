# 💳 Quiero.Money

Aplicación demo para manejo de saldos en COP y BTC con login en 2 pasos, diseño moderno y responsivo.  
Construida en **Streamlit**, lista para desplegar en **Railway / Render / Fly.io**.

---

## 🚀 Características
- Login en **2 pasos**:
  1. Número de celular (10 dígitos).
  2. PIN de acceso (`12345`).
- Dashboard con:
  - Tarjeta Saldo COP.
  - Tarjeta Saldo BTC.
  - Tarjeta Precio BTC en tiempo real.
  - **Gráfico de evolución del BTC (7 días)**.
- Secciones:
  - Panel de Control
  - Recargar (Nequi / Daviplata)
  - Comprar BTC
  - Vender BTC
  - Enviar
  - Historial de transacciones
- **Diseño responsivo** (mobile-first, compatible con escritorio y celular).

---

## 📂 Estructura del proyecto
```
alvaro/
│── app_dark.py        # App principal en Streamlit
│── styles.css         # Estilos modernos
│── requirements.txt   # Dependencias para despliegue
│── Procfile           # Comando de ejecución en Railway/Render
│── assets/            # Carpeta de imágenes (opcional)
```

---

## 🖥️ Ejecutar en local
1. Clona este repo:
   ```bash
   git clone https://github.com/tu-usuario/quiero-money.git
   cd quiero-money
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la app:
   ```bash
   streamlit run app_dark.py
   ```

Accede en tu navegador: [http://localhost:8501](http://localhost:8501)

---

## 🌐 Despliegue en Railway
1. Crea una cuenta en [Railway](https://railway.app/).  
2. Conecta tu repo de GitHub.  
3. Railway instalará automáticamente dependencias de `requirements.txt` y usará el comando del `Procfile`:
   ```bash
   web: streamlit run app_dark.py --server.port=$PORT --server.address=0.0.0.0
   ```
4. Al finalizar, Railway te dará una URL pública como:
   ```
   https://quiero-money.up.railway.app
   ```

---

## 📱 Uso en celular
- Abre la URL pública en el navegador de tu celular.  
- La interfaz está optimizada para móvil.  

---

## 🔑 Credenciales de prueba
- Número de celular: cualquier número válido de **10 dígitos**  
- PIN: `12345`

---
✨ Desarrollado con **Streamlit** y ❤️
