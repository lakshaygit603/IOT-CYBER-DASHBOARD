from flask import Flask, request, jsonify, render_template_string, redirect, session
import sqlite3, time, os, random, psutil
from functools import wraps
from collections import deque
app = Flask(__name__)
app.secret_key = "enterprise_neon_secret_key_9843"
DB = "users.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE users(
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
        """)

        default_users = [
            ("admin", "admin123", "admin"),
            ("viewer", "viewer123", "viewer"),
            ("auditor", "audit123", "auditor")
        ]

        c.executemany("INSERT INTO users VALUES (?,?,?)", default_users)
        conn.commit()
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    r = c.fetchone()
    conn.close()
    return r[0] if r else None

init_db()

def require_role(roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return redirect("/login")
            if session["role"] not in roles:
                return "<h2>ACCESS DENIED</h2>", 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

temp_history = deque(maxlen=60)
hum_history  = deque(maxlen=60)

alerts = []          
security_logs = []   
threat_score = 0     
last_seen = None

device_state = {
    "fan": "OFF",
    "ac": "OFF"
}
threat_history = []


def update_last_seen():
    global last_seen
    last_seen = time.strftime("%H:%M:%S")


@app.route("/live-data")
def live_data():
    temp = round(random.uniform(20, 40), 1)
    hum  = round(random.uniform(30, 80), 1)
    now  = time.strftime("%H:%M:%S")

    temp_history.append((now, temp))
    hum_history.append((now, hum))

    update_last_seen()

    # Auto Alert: Temperature threshold
    if temp > 32:
        alerts.append(f"🔥 High Temperature {temp}°C at {now}")
        security_logs.append(f"[ALERT] High Temp detected {temp}°C at {now}")

    return jsonify({
        "labels": [t[0] for t in temp_history],
        "temp":   [t[1] for t in temp_history],
        "hum":    [h[1] for h in hum_history]
    })

def ai_predict_next():
    """Predicts next temperature & humidity based on last value."""
    if not temp_history or not hum_history:
        return 0, 0

    last_t = temp_history[-1][1]
    last_h = hum_history[-1][1]

    next_t = last_t + random.uniform(-1.2, 1.2)
    next_h = last_h + random.uniform(-3, 3)

    return round(next_t, 1), round(next_h, 1)

@app.route("/predict")
def predict():
    t, h = ai_predict_next()
    return jsonify({"next_temp": t, "next_hum": h})

SUSPICIOUS_PATTERNS = [
    "DROP TABLE", "SELECT * FROM users", "UNION SELECT",
    "malware", "attack", "exploit", "ddos",
    "root access", "bypass", "sql injection"
]

def ids_inspect(payload):
    """Check message for threat signatures."""
    global threat_score

    msg = payload.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.lower() in msg:
            threat_score += 10
            log = f"[IDS] Threat detected: '{pattern}' in payload '{msg}' at {time.strftime('%H:%M:%S')}"
            security_logs.append(str(log))
            alerts.append("⚠ IDS Threat Detected")
            return True
    return False


@app.route("/ids-check", methods=["POST"])
def ids_check():
    data = request.json.get("payload", "")
    is_threat = ids_inspect(data)
    return jsonify({"threat": is_threat, "score": threat_score})

CYBER_ATTACKS = [
    "DDoS Attempt Blocked",
    "Port Scan Detected & Prevented",
    "Unauthorized Login Attempt Blocked",
    "Suspicious Data Spike Flagged",
    "Firewall Auto Rule Triggered",
    "Unusual Outbound Traffic Neutralized"
]

def simulate_attack():
    """Returns a random cyber event message."""
    event = random.choice(CYBER_ATTACKS)
    now = time.strftime("%H:%M:%S")

    security_logs.append(f"[SIM] {event} at {now}")
    alerts.append(f"🚨 Cyber Event: {event}")

    return event

@app.route("/cyber-sim")
def cyber_sim_api():
    return jsonify({"event": simulate_attack()})


@app.route("/system-health")
def system_health_api():
    return jsonify({
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    })

@app.route("/network-scan")
def network_scan_api():
    devices = [
        "Laptop — 192.168.1.10",
        "Phone — 192.168.1.11",
        "Smart TV — 192.168.1.12",
        "IoT Sensor — 192.168.1.15",
        "SmartWatch — 192.168.1.16"
    ]
    return jsonify({"devices": devices})

@app.route("/alerts")
def alerts_api():
    return jsonify({"alerts": alerts[-20:]})

BASE_STYLE = """
<style>

body{
    margin:0;
    padding:0;
    background:#00101a;
    color:white;
    font-family:Poppins,Arial;
    overflow-x:hidden;
}

/* LIGHT MODE */
body.light{
    background:#f2f2f2;
    color:#111;
}
body.light .glass{
    background:rgba(0,0,0,0.05);
    border:1px solid #444;
    color:#000;
}
body.light a{
    color:#333;
}

/* GLASS PANELS */
.glass{
    background:rgba(0,255,255,0.09);
    border:1px solid cyan;
    border-radius:14px;
    padding:18px;
    margin-top:18px;
    box-shadow:0 0 18px cyan;
}

/* GRID LAYOUT (G3) */
.grid{
    display:grid;
    grid-template-columns:45% 25% 30%;
    padding:20px;
    gap:20px;
}

/* NAVBAR */
.navbar{
    position:fixed;
    bottom:0;
    width:100%;
    background:rgba(0,255,255,0.08);
    display:flex;
    justify-content:space-around;
    padding:12px;
    border-top:1px solid cyan;
}
.navbar a{
    text-decoration:none;
    color:cyan;
    font-size:20px;
    font-weight:bold;
}

/* THEME TOGGLE BUTTON */
.toggle-btn{
    position:fixed;
    bottom:70px;
    left:20px;
    padding:10px 15px;
    background:cyan;
    color:black;
    border-radius:8px;
    cursor:pointer;
    box-shadow:0 0 10px cyan;
}

/* -------------------------------------------------------------
   3D HOLOGRAM CHATBOT
------------------------------------------------------------- */
.holo-btn{
    position:fixed;
    bottom:120px;
    right:20px;
    width:70px;
    height:70px;
    background:rgba(0,255,255,0.18);
    border-radius:50%;
    border:2px solid cyan;
    box-shadow:0 0 25px cyan;
    display:flex;
    justify-content:center;
    align-items:center;
    cursor:pointer;
    font-size:30px;
}

.holo-window{
    position:fixed;
    bottom:200px;
    right:20px;
    width:320px;
    height:420px;
    background:rgba(0,255,255,0.14);
    border:1px solid cyan;
    border-radius:16px;
    box-shadow:0 0 25px cyan;
    backdrop-filter:blur(14px);
    display:none;
    flex-direction:column;
}

.holo-avatar{
    height:120px;
    background:url('https://i.ibb.co/ZVbWVLc/ai-holo.gif');
    background-size:contain;
    background-repeat:no-repeat;
    background-position:center;
    filter:drop-shadow(0 0 35px cyan);
}

.holo-chat{
    flex:1;
    overflow-y:auto;
    padding:10px;
    font-size:14px;
}

.holo-input{
    display:flex;
}
.holo-input input{
    flex:1;
    padding:10px;
    border:none;
    background:#003344;
    color:white;
}
.holo-input button{
    padding:10px;
    border:none;
    background:cyan;
    cursor:pointer;
}

</style>

<script>
/* ==================== THEME SWITCH ===================== */
function toggleTheme(){
    if(document.body.classList.contains("light")){
        document.body.classList.remove("light");
        localStorage.setItem("theme","dark");
    } else {
        document.body.classList.add("light");
        localStorage.setItem("theme","light");
    }
}
window.onload = () => {
    if(localStorage.getItem("theme") === "light"){
        document.body.classList.add("light");
    }
}

/* ==================== HOLOGRAM CHATBOT ===================== */
function toggleHolo(){
    let w=document.getElementById("holoWindow");
    w.style.display = (w.style.display==="flex") ? "none" : "flex";
}

function addHolo(msg,sender){
    let box=document.getElementById("holoChat");
    let d=document.createElement("div");
    d.style.margin="8px 0";
    d.innerHTML="<b>"+sender+":</b> "+msg;
    box.appendChild(d);
    box.scrollTop=box.scrollHeight;
}

async function sendHolo(){
    let text=document.getElementById("holoText").value;
    if(!text) return;
    addHolo(text,"You");
    document.getElementById("holoText").value="";

    let r=await fetch("/chatbot",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({msg:text})
    });
    let j=await r.json();
    addHolo(j.reply,"Bot");
}
</script>
"""
HOME_HTML = BASE_STYLE + """
<div class='toggle-btn' onclick='toggleTheme()'>🌙/☀️</div>
<div class='holo-btn' onclick='toggleHolo()'>🤖</div>

<!-- CHATBOT -->
<div id='holoWindow' class='holo-window'>
    <div class='holo-avatar'></div>
    <div id='holoChat' class='holo-chat'></div>
    <div class='holo-input'>
        <input id='holoText' placeholder='Ask something...'>
        <button onclick='sendHolo()'>Send</button>
    </div>
</div>

<h2 style='padding-left:20px;'>🚀 IoT Cyber Dashboard</h2>

<div class='grid'>

    <!-- COLUMN 1 -->
    <div>
        <div class='glass'>
            <h3>📈 Live Charts</h3>
            <canvas id='liveChart' height='120'></canvas>
        </div>

        <div class='glass'>
            <h3>📊 Analytics</h3>
            <div id='analyticsBox'>Loading...</div>
        </div>
    </div>

    <!-- COLUMN 2 -->
    <div>
        <div class='glass'>
            <h3>💠 System Health</h3>
            <div id='sysBox'>Loading...</div>
        </div>

        <div class='glass'>
            <h3>📡 Network Scan</h3>
            <div id='netBox'>Loading...</div>
        </div>

        <div class='glass'>
            <h3>🚨 Alerts</h3>
            <div id='alertBox' style='height:120px; overflow-y:auto;'>Loading...</div>
        </div>
    </div>

    <!-- COLUMN 3 -->
    <div>
        <div class='glass'>
            <h3>🔮 AI Prediction</h3>
            <div id='predBox'>Loading...</div>
        </div>

        <div class='glass'>
            <h3>🛡 Cyberattack Simulator</h3>
            <button onclick='simulateAttack()' 
                style='padding:10px; background:cyan; border:none; cursor:pointer;'>
                Trigger Attack
            </button>
            <div id='attackResult' style='margin-top:10px;'></div>
        </div>

        <div class='glass'>
            <h3>⚠ Threat Level</h3>
            <div id='threatBox'>Loading...</div>
        </div>
    </div>

</div>

<!-- NAVBAR -->
<div class='navbar'>
  <a href='/'>🏠 Home</a>
  <a href='/security'>🛡 Security Center</a>
  <a href='/control'>⚙ Control</a>
  <a href='/logout' style='color:#ff8a8a;'>Logout</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>

let ctx = document.getElementById('liveChart').getContext('2d');
let chart = new Chart(ctx,{
    type:'line',
    data:{labels:[],datasets:[
        { label:'Temp °C', borderColor:'cyan', data:[], fill:false },
        { label:'Humidity %', borderColor:'yellow', data:[], fill:false }
    ]}
});

/* AUTO LOADER FUNCTIONS */

async function loadChart(){
    let r=await fetch('/live-data');
    let j=await r.json();
    chart.data.labels=j.labels;
    chart.data.datasets[0].data=j.temp;
    chart.data.datasets[1].data=j.hum;
    chart.update();

    document.getElementById('analyticsBox').innerHTML=
        "Max: "+Math.max(...j.temp)+
        "°C<br>Min: "+Math.min(...j.temp)+
        "°C<br>Average: "+(j.temp.reduce((a,b)=>a+b)/j.temp.length).toFixed(1)+"°C";
}

async function loadHealth(){
    let r=await fetch('/system-health');
    let j=await r.json();
    document.getElementById('sysBox').innerHTML=
        "CPU: "+j.cpu+"%<br>RAM: "+j.ram+"%<br>Disk: "+j.disk+"%";
}

async function loadNetwork(){
    let r=await fetch('/network-scan');
    let j=await r.json();
    document.getElementById('netBox').innerHTML=j.devices.join("<br>");
}

async function loadAlerts(){
    let r=await fetch('/alerts');
    let j=await r.json();
    document.getElementById('alertBox').innerHTML=j.alerts.join("<br>");
}

async function loadPrediction(){
    let r=await fetch('/predict');
    let j=await r.json();
    document.getElementById('predBox').innerHTML=
        "Next Temp: "+j.next_temp+"°C<br>"+
        "Next Humidity: "+j.next_hum+"%";
}

async function loadThreat(){
    let r = await fetch('/threat-level');
    let j = await r.json();

    document.getElementById('threatBox').innerHTML = j.level + "%";

    attackChart.data.labels = [...Array(j.history.length).keys()];
    attackChart.data.datasets[0].data = j.history;
    attackChart.update();
}


async function simulateAttack(){
    let r=await fetch('/cyber-sim');
    let j=await r.json();
    document.getElementById('attackResult').innerHTML=j.event;
}

/* AUTO REFRESH */
setInterval(()=>{
    loadChart();
    loadHealth();
    loadAlerts();
    loadPrediction();
    loadThreat();
},2000);

setInterval(()=>{ loadNetwork(); },4000);

/* INITIAL LOAD */
loadChart();
loadHealth();
loadNetwork();
loadAlerts();
loadPrediction();
loadThreat();

</script>
"""
@app.route("/")
@require_role(["admin", "viewer", "auditor"])
def home():
    return HOME_HTML

LOGIN_HTML = """
<style>
body{
    background:#00101a;
    font-family:Poppins,Arial;
    color:white;
    text-align:center;
    padding-top:120px;
}
input{
    padding:10px;
    width:220px;
    margin:5px;
    border-radius:8px;
    border:none;
    background:#003344;
    color:white;
}
button{
    padding:10px 20px;
    border:none;
    background:cyan;
    border-radius:6px;
    cursor:pointer;
}
a{ color:cyan; }
</style>

<h2>🔐 IoT Login</h2>

<form method="POST">
    <input name="username" placeholder="Username"><br>
    <input type="password" name="password" placeholder="Password"><br>
    <button>Login</button>
</form>
"""
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        role = check_user(username, password)
        if role:
            session["user"] = username
            session["role"] = role
            security_logs.append(
                f"[{time.strftime('%H:%M:%S')}] LOGIN: {username} ({role})"
            )
            return redirect("/")
        else:
            return "<h3 style='color:red;'>Invalid Credentials</h3>" + LOGIN_HTML

    return LOGIN_HTML

CONTROL_HTML = BASE_STYLE + """
<h2 style='padding-left:20px;'>⚙ Device Control Panel</h2>

<div style='padding:20px;'>

    <div class='glass'>
        <h3>Fan</h3>
        Status: <b style='color:cyan;'>{{fan}}</b><br><br>
        <a href='/toggle/fan' style='color:cyan;'>Toggle Fan</a>
    </div>

    <div class='glass'>
        <h3>Air Conditioner</h3>
        Status: <b style='color:cyan;'>{{ac}}</b><br><br>
        <a href='/toggle/ac' style='color:cyan;'>Toggle AC</a>
    </div>

</div>

<div class='navbar'>
  <a href='/'>🏠 Home</a>
  <a href='/security'>🛡 Security Center</a>
  <a href='/control'>⚙ Control</a>
  <a href='/logout' style='color:#ff8a8a;'>Logout</a>
</div>
"""
def chatbot_reply(msg):
    msg = msg.lower()

    # Greetings
    if "hi" in msg or "hello" in msg:
        return "Hello! I am your Neon Hologram AI assistant."

    # Temperature
    if "temperature" in msg:
        return f"Current temperature is {temp_history[-1][1]}°C" if temp_history else "No data yet."

    # Humidity
    if "humidity" in msg:
        return f"Current humidity is {hum_history[-1][1]}%" if hum_history else "No data yet."

    # Fan
    if "fan" in msg:
        return f"Fan is {device_state['fan']}."

    # AC
    if "ac" in msg or "air conditioner" in msg:
        return f"AC is {device_state['ac']}."

    # Toggle Devices
    if "toggle fan" in msg:
        device_state["fan"] = "ON" if device_state["fan"] == "OFF" else "OFF"
        return f"Fan turned {device_state['fan']}."

    if "toggle ac" in msg:
        device_state["ac"] = "ON" if device_state["ac"] == "OFF" else "OFF"
        return f"AC turned {device_state['ac']}."

    # Prediction
    if "predict" in msg or "future" in msg:
        t, h = ai_predict_next()
        return f"Future Temp ≈ {t}°C, Future Humidity ≈ {h}%."

    # Cyberattack
    if "attack" in msg:
        e = simulate_attack()
        return f"Cyberattack simulation triggered: {e}"

    # Threat Level
    if "threat" in msg:
        return f"Current threat score: {threat_score}%"

    # Help
    if "help" in msg:
        return ("Commands: temperature, humidity, fan, ac, toggle fan, toggle ac, "
                "predict, attack, threat level")

    return "I didn't understand that. Try typing 'help'."

IDS_PATTERNS = [
    ("PORT_SCAN", "Multiple sequential ports accessed"),
    ("DDOS", "High frequency of requests detected"),
    ("BRUTE_FORCE", "Repeated login failures"),
    ("MALWARE_TRAFFIC", "Suspicious outbound traffic spike"),
    ("ANOMALY", "Unexpected sensor spike pattern"),
]

def run_ids(event_type):
    """Simulated IDS detection engine."""
    for code, desc in IDS_PATTERNS:
        if code == event_type:
            timestamp = time.strftime("%H:%M:%S")
            log = f"[{timestamp}] IDS DETECTED: {desc}"
            security_logs.append(log)
            return log
    return None


def run_ips(event_type):
    """Simulated IPS prevention engine."""
    timestamp = time.strftime("%H:%M:%S")

    action = f"[{timestamp}] IPS ACTION: Blocked {event_type}"
    security_logs.append(action)

    # Increase global threat score
    global threat_score
    threat_score = min(threat_score + random.randint(5, 15), 100)

    return action

SECURITY_HTML = BASE_STYLE + """
<h2 style='padding-left:20px;'>🛡 Cybersecurity Center (IDS + IPS)</h2>

<div class="grid">

    <!-- ======================= COLUMN 1 ======================= -->
    <div>

        <div class="glass">
            <h3>🚨 Threat Level</h3>
            <div id="threatBox" style="font-size:26px; color:cyan;">Loading...</div>
        </div>

        <div class="glass">
            <h3>📊 Attack Graph</h3>
            <canvas id="attackChart" height="120"></canvas>
        </div>

    </div>

    <!-- ======================= COLUMN 2 ======================= -->
    <div>

        <div class="glass">
            <h3>🔍 IDS Alerts</h3>
            <div id="idsBox" style="height:160px; overflow-y:auto;">Loading...</div>
        </div>

        <div class="glass">
            <h3>🛑 IPS Actions</h3>
            <div id="ipsBox" style="height:160px; overflow-y:auto;">Loading...</div>
        </div>

    </div>

    <!-- ======================= COLUMN 3 ======================= -->
    <div>

        <div class="glass">
            <h3>📁 System Security Logs</h3>
            <div id="logBox" style="height:350px; overflow-y:auto;">Loading...</div>
        </div>

        <div class="glass">
            <h3>⚔ Simulate Attack</h3>
            <button onclick="triggerIDS('PORT_SCAN')" class="sec-btn">Port Scan</button>
            <button onclick="triggerIDS('DDOS')" class="sec-btn">DDoS</button>
            <button onclick="triggerIDS('BRUTE_FORCE')" class="sec-btn">Brute Force</button>
            <button onclick="triggerIDS('MALWARE_TRAFFIC')" class="sec-btn">Malware</button>
        </div>

    </div>

</div>

<style>
.sec-btn{
    padding:8px 15px;
    margin:5px;
    background:cyan;
    border:none;
    border-radius:8px;
    cursor:pointer;
    color:black;
    font-weight:bold;
    box-shadow:0 0 10px cyan;
}
</style>

<div class='navbar'>
  <a href='/'>🏠 Home</a>
  <a href='/security'>🛡 Security</a>
  <a href='/control'>⚙ Control</a>
  <a href='/logout' style='color:#ff8a8a;'>Logout</a>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
let actx = document.getElementById('attackChart').getContext('2d');
let attackChart = new Chart(actx, {
    type:'bar',
    data:{
        labels:[],
        datasets:[{
            label:'Threat Score',
            borderColor:'cyan',
            backgroundColor:'rgba(0,255,255,0.3)',
            data:[]
        }]
    }
});

async function loadThreat(){
    let r = await fetch('/threat-level');
    let j = await r.json();
    document.getElementById('threatBox').innerHTML = j.level + "%";
    attackChart.data.labels = [...Array(j.history.length).keys()];
attackChart.data.datasets[0].data = j.history;
attackChart.update();
}


async function loadIDS(){
    let r = await fetch('/ids-log');
    let j = await r.json();
    document.getElementById('idsBox').innerHTML = j.logs.join("<br>");
}

async function loadIPS(){
    let r = await fetch('/ips-log');
    let j = await r.json();
    document.getElementById('ipsBox').innerHTML = j.logs.join("<br>");
}

async function loadSystemLogs(){
    let r = await fetch('/security-logs');
    let j = await r.json();
    document.getElementById('logBox').innerHTML = j.logs.join("<br>");
}

async function triggerIDS(type){
    let r = await fetch('/trigger-ids/'+type);
    let j = await r.json();
    alert(j.status);
}

// Auto-refresh each 2 sec
setInterval(()=>{
    loadThreat();
    loadIDS();
    loadIPS();
    loadSystemLogs();
},2000);

loadThreat();
loadIDS();
loadIPS();
loadSystemLogs();
</script>
"""
@app.route("/security")
@require_role(["admin","auditor"])
def security_page():
    return SECURITY_HTML

@app.route("/threat-level")
def threat_level():
    global threat_history
    threat_history.append(threat_score)

    # Keep only last 20 values
    threat_history = threat_history[-20:]

    return jsonify({
        "level": threat_score,
        "history": threat_history
    })

@app.route("/trigger-ids/<etype>")
def trigger_ids(etype):
    ids_log = run_ids(etype)
    ips_log = run_ips(etype)

    return jsonify({"status": f"IDS+IPS triggered for {etype}"})

@app.route("/ids-log")
def ids_log():
    safe_logs = [str(x) for x in security_logs if isinstance(x, str) and "IDS" in x]
    return jsonify({"logs": safe_logs[-30:]})


@app.route("/ips-log")
def ips_log():
    safe_logs = [str(x) for x in security_logs if isinstance(x, str) and "IPS" in x]
    return jsonify({"logs": safe_logs[-30:]})


@app.route("/security-logs")
def sec_logs():
    safe_logs = [str(x) for x in security_logs if isinstance(x, str)]
    return jsonify({"logs": safe_logs[-30:]})


@app.route("/logout")
def logout():
    user = session.get("user", "Unknown")
    security_logs.append("Log entry added")
    session.clear()
    return redirect("/login")

LOGIN_HTML = """
<style>
body{
    background:#001428;
    font-family:Poppins,Arial;
    color:white;
    text-align:center;
    padding-top:120px;
}
input{
    padding:10px;
    width:220px;
    margin:5px;
    border-radius:8px;
    border:none;
    background:#003344;
    color:white;
}
button{
    padding:10px 20px;
    border:none;
    background:cyan;
    border-radius:6px;
    cursor:pointer;
}
a{ color:cyan; }
</style>

<h2>🔐 IoT Login</h2>

<form method="POST">
    <input name="username" placeholder="Username"><br>
    <input type="password" name="password" placeholder="Password"><br>
    <button>Login</button>
</form>
"""
CONTROL_HTML = BASE_STYLE + """
<h2 style='padding-left:20px;'>⚙ Device Control</h2>

<div style='padding:20px;'>

<div class='glass'>
<h3>Fan</h3>
Status: <b>{{fan}}</b><br><br>
<a href='/toggle/fan' style='color:cyan;'>Toggle Fan</a>
</div>

<div class='glass'>
<h3>Air Conditioner</h3>
Status: <b>{{ac}}</b><br><br>
<a href='/toggle/ac' style='color:cyan;'>Toggle AC</a>
</div>

</div>

<div class='navbar'>
  <a href='/'>🏠 Home</a>
  <a href='/security'>🛡 Security</a>
  <a href='/control'>⚙ Control</a>
  <a href='/logout' style='color:#ff8a8a;'>Logout</a>
</div>
"""

@app.route("/control")
@require_role(["admin"])
def control():
    return render_template_string(
        CONTROL_HTML,
        fan=device_state["fan"],
        ac=device_state["ac"]
    )


@app.route("/toggle/<dev>")
@require_role(["admin"])
def toggle(dev):
    device_state[dev] = "ON" if device_state[dev] == "OFF" else "OFF"
    alerts.append(f"{dev.upper()} toggled to {device_state[dev]}")
    security_logs.append(
        f"[{time.strftime('%H:%M:%S')}] ADMIN CHANGE: {dev.upper()} -> {device_state[dev]}"
    )
    return redirect("/control")

def chatbot_reply(message):
    msg = message.lower()

    if "hi" in msg or "hello" in msg:
        return "Hello! I am your Neon AI Assistant."

    if "temperature" in msg:
        return f"Current temperature: {temp_history[-1][1]}°C" if temp_history else "No data yet."

    if "humidity" in msg:
        return f"Current humidity: {hum_history[-1][1]}%" if hum_history else "No data yet."

    if "fan" in msg:
        return f"Fan is {device_state['fan']}"

    if "ac" in msg:
        return f"AC is {device_state['ac']}"

    if "predict" in msg:
        t, h = ai_predict_next()
        return f"Next Temp ≈ {t}°C, Next Humidity ≈ {h}%"

    if "attack" in msg:
        e = random.choice([
            "Firewall Blocked Intrusion",
            "Suspicious Traffic Detected",
            "Access Denied Attempt Logged"
        ])
        return f"Cyber Event: {e}"

    if "help" in msg:
        return "Commands: temperature, humidity, fan, ac, predict, attack"

    return "I'm not sure. Try asking 'help'."

@app.route("/chatbot", methods=["POST"])
def chatbot_api():
    msg = request.json.get("msg", "")
    reply = chatbot_reply(msg)
    return jsonify({"reply": reply})
if __name__ == "__main__":
    print("\n🚀 CYBER-NEON DASHBOARD READY")
    print("🔐 Login: admin/admin123")
    print("🌐 Open http://127.0.0.1:5000\n")
    app.run(debug=True)