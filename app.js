const app = document.getElementById("app");

let state = {
  page: "login-phone", // login-phone → login-pin → panel → pages
  phone: "",
  pin: "",
  saldoCop: 1000000,
  saldoBtc: 0.05,
  btcPrice: 250000000, // precio COP
  historial: []
};

// Render principal
function render() {
  app.innerHTML = "";

  if (state.page === "login-phone") renderPhoneLogin();
  else if (state.page === "login-pin") renderPinLogin();
  else if (state.page === "panel") renderPanel();
  else if (state.page === "comprar") renderComprar();
  else if (state.page === "vender") renderVender();
  else if (state.page === "recargar") renderRecargar();
  else if (state.page === "historial") renderHistorial();
}

// Login teléfono
function renderPhoneLogin() {
  app.innerHTML = `
    <div class="header"><div class="brand">Quiero.Money</div></div>
    <div class="card">
      <div class="title">Ingresa tu celular</div>
      <div class="subtitle">Número de 10 dígitos</div>
      <input id="phone" class="input" maxlength="10" placeholder="Ej: 3001234567"/>
      <button class="btn" onclick="goPin()">Continuar</button>
    </div>
  `;
}
function goPin() {
  const phone = document.getElementById("phone").value;
  if (phone.length === 10) {
    state.phone = phone;
    state.page = "login-pin";
    render();
  } else {
    alert("Número inválido");
  }
}

// Login PIN
function renderPinLogin() {
  app.innerHTML = `
    <div class="header"><div class="brand">Quiero.Money</div></div>
    <div class="card">
      <div class="title">Ingresa tu PIN</div>
      <div class="pin-row">
        <div class="pin-box" id="p1"></div>
        <div class="pin-box" id="p2"></div>
        <div class="pin-box" id="p3"></div>
        <div class="pin-box" id="p4"></div>
        <div class="pin-box" id="p5"></div>
      </div>
      <div class="grid-3">
        ${[1,2,3,4,5,6,7,8,9,"",0,"←"].map(k => 
          `<div class="key ${k===""?"empty":""}" onclick="pressKey('${k}')">${k}</div>`
        ).join("")}
      </div>
    </div>
  `;
}
function pressKey(k) {
  if (k === "←") {
    state.pin = state.pin.slice(0, -1);
  } else if (k !== "" && state.pin.length < 5) {
    state.pin += k;
  }
  for (let i=0; i<5; i++) {
    document.getElementById("p"+(i+1)).innerText = state.pin[i] ? "•" : "";
  }
  if (state.pin.length === 5) {
    if (state.pin === "12345") {
      state.page = "panel";
      render();
    } else {
      alert("PIN incorrecto");
      state.pin = "";
      render();
    }
  }
}

// Sidebar
function sidebar() {
  return `
  <div class="sidebar">
    <button class="nav-btn" onclick="go('panel')">Panel</button>
    <button class="nav-btn" onclick="go('comprar')">Comprar</button>
    <button class="nav-btn" onclick="go('vender')">Vender</button>
    <button class="nav-btn" onclick="go('recargar')">Recargar</button>
    <button class="nav-btn" onclick="go('historial')">Historial</button>
    <div class="side-footer">
      <button class="nav-btn" onclick="connectMetaMask()">MetaMask</button>
    </div>
  </div>`;
}
function go(p) { state.page = p; render(); }

// Panel principal
function renderPanel() {
  app.innerHTML = sidebar() + `
  <div class="main">
    <div class="title">Panel de control</div>
    <div class="metric"><div class="label">Saldo COP</div><div class="value">$${state.saldoCop.toLocaleString()}</div></div>
    <div class="metric"><div class="label">Saldo BTC</div><div class="value">${state.saldoBtc} BTC</div></div>
    <div class="metric"><div class="label">Precio BTC</div><div class="value">$${state.btcPrice.toLocaleString()}</div></div>
    <div class="chart-card">
      <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=BTCUSD&interval=30&hidesidetoolbar=1&theme=dark&style=1&timezone=Etc/UTC&locale=es" 
      style="width:100%; height:400px;" frameborder="0"></iframe>
    </div>
  </div>`;
}

// Comprar BTC
function renderComprar() {
  app.innerHTML = sidebar() + `
  <div class="main">
    <div class="back" onclick="go('panel')">← Volver</div>
    <div class="title">Comprar BTC</div>
    <input id="montoCop" class="input" placeholder="Monto en COP"/>
    <button class="btn" onclick="doComprar()">Comprar</button>
  </div>`;
}
function doComprar() {
  let cop = parseFloat(document.getElementById("montoCop").value);
  if (cop>0 && state.saldoCop>=cop) {
    let btc = cop/state.btcPrice;
    state.saldoCop -= cop;
    state.saldoBtc += btc;
    state.historial.push({tipo:"Compra", cop:-cop, btc:+btc, fecha:new Date()});
    alert("Compra realizada");
    go("panel");
  } else alert("Fondos insuficientes");
}

// Vender BTC
function renderVender() {
  app.innerHTML = sidebar() + `
  <div class="main">
    <div class="back" onclick="go('panel')">← Volver</div>
    <div class="title">Vender BTC</div>
    <input id="montoBtc" class="input" placeholder="Monto en BTC"/>
    <button class="btn" onclick="doVender()">Vender</button>
  </div>`;
}
function doVender() {
  let btc = parseFloat(document.getElementById("montoBtc").value);
  if (btc>0 && state.saldoBtc>=btc) {
    let cop = btc*state.btcPrice;
    state.saldoBtc -= btc;
    state.saldoCop += cop;
    state.historial.push({tipo:"Venta", cop:+cop, btc:-btc, fecha:new Date()});
    alert("Venta realizada");
    go("panel");
  } else alert("Saldo BTC insuficiente");
}

// Recargar
function renderRecargar() {
  app.innerHTML = sidebar() + `
  <div class="main">
    <div class="back" onclick="go('panel')">← Volver</div>
    <div class="title">Recargar COP</div>
    <input id="recarga" class="input" placeholder="Monto COP"/>
    <div style="display:flex; gap:10px; margin-top:10px;">
      <button class="btn" onclick="doRecargar('Nequi')">Recargar con Nequi</button>
      <button class="btn" onclick="doRecargar('Daviplata')">Recargar con Daviplata</button>
    </div>
  </div>`;
}
function doRecargar(metodo) {
  let cop = parseFloat(document.getElementById("recarga").value);
  if (cop>0) {
    state.saldoCop += cop;
    state.historial.push({tipo:`Recarga ${metodo}`, cop:+cop, btc:0, fecha:new Date()});
    alert(`Recarga con ${metodo} realizada`);
    go("panel");
  }
}

// Historial
function renderHistorial() {
  app.innerHTML = sidebar() + `
  <div class="main">
    <div class="back" onclick="go('panel')">← Volver</div>
    <div class="title">Historial</div>
    <table class="table">
      <tr><th>Fecha</th><th>Tipo</th><th>COP</th><th>BTC</th></tr>
      ${state.historial.map(h=>`
        <tr>
          <td>${h.fecha.toLocaleString()}</td>
          <td>${h.tipo}</td>
          <td>${h.cop.toLocaleString()}</td>
          <td>${h.btc}</td>
        </tr>
      `).join("")}
    </table>
  </div>`;
}

// MetaMask (redirige a la web oficial)
function connectMetaMask() {
  window.open("https://metamask.io/es", "_blank");
}

render();
