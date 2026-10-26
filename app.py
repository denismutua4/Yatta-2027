from flask import Flask, render_template_string, request, send_from_directory
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
DB = 'campaign.db'
ADMIN_PIN = "denismutua2027"
DATABASE_URL = os.environ.get("DATABASE_URL")

WHATSAPP_GROUP = "https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH"
WHATSAPP_DIRECT = "https://wa.me/254796069040?text=Niko%20tayari%20na%20Yatta%202027"
FACEBOOK_LINK = "https://www.facebook.com/profile.php?id=61594277768769"
TIKTOK_LINK = "https://www.tiktok.com/@mutuawakatangi"
INSTAGRAM_LINK = "https://www.instagram.com/daudidenismutua"

def get_conn():
    if DATABASE_URL:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect(DB)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    if DATABASE_URL:
        c.execute('''CREATE TABLE IF NOT EXISTS donations
                     (id SERIAL PRIMARY KEY, name TEXT, phone TEXT, ward TEXT, mpesa_code TEXT, amount INTEGER, date TEXT)''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS donations
                     (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, ward TEXT, mpesa_code TEXT, amount INTEGER, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

HOME_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MUTUA WA KATANGI - YATTA MP 2027</title>
<style>
body{font-family:Arial;background:#e8f5e9;padding:10px;margin:0;padding-bottom:90px}
.card{background:white;border-radius:15px;padding:20px;margin:10px 0;box-shadow:0 3px 10px #ccc}
.green{background:linear-gradient(135deg,#004d26,#006633);color:white;text-align:center;padding:30px 20px}
input,select,button{padding:14px;margin:8px 0;width:100%;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}
button{background:#006633;color:white;font-weight:bold;border:none;font-size:18px}
.badge{background:#FFD700;color:#006633;padding:8px 15px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px}
.profile{width:150px;height:150px;border-radius:50%;border:4px solid #FFD700;object-fit:cover;object-position:top center;margin-bottom:15px;box-shadow:0 4px 15px rgba(0,0,0,0.4)}
.social-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:15px}
.s-btn{display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;color:white;font-size:14px}
.wa{background:#25D366}.fb{background:#1877F2}.tt{background:#000}.ig{background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)}
.float-wa{position:fixed;bottom:20px;right:20px;background:#25D366;color:white;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:32px;box-shadow:0 4px 15px rgba(0,0,0,0.4);z-index:9999;text-decoration:none}
</style></head><body>
<div class="card green">
<img src="/photo" class="profile" onerror="this.style.display='none'">
<h1 style="margin:10px 0">MUTUA WA KATANGI</h1>
<h2 style="color:#FFD700;margin:5px 0">YATTA MP 2027</h2>
<p>IG: @daudidenismutua | TikTok: @mutuawakatangi</p>
<span class="badge">POCHI LA BIASHARA: 0796069040</span>
</div>
<div class="card" style="border:3px solid #006633">
<h3 style="color:#006633;text-align:center">LIPA: *334# -> Pochi 0796069040</h3>
<form method="POST" action="/donate">
<input name="name" placeholder="Jina lako" required>
<input name="phone" placeholder="07..." required>
<select name="ward" required><option value="">Chagua Ward</option><option>Katangi</option><option>Matuu</option><option>Kithimani</option><option>Ikombe</option><option>Ndalani</option></select>
<input name="mpesa_code" placeholder="M-Pesa Code" required>
<input name="amount" type="number" placeholder="Amount" required>
<button>CONFIRM DONATION</button>
</form>
<h4 style="text-align:center;color:#006633;margin-top:20px">FOLLOW & JOIN US:</h4>
<div class="social-grid">
<a href="{{wa_group}}" class="s-btn wa">WhatsApp Group</a>
<a href="{{fb}}" class="s-btn fb">Facebook Page</a>
<a href="{{tt}}" class="s-btn tt">TikTok 50</a>
<a href="{{ig}}" class="s-btn ig">Instagram 139</a>
</div>
</div>
<div class="card" style="background:#fff9c4;text-align:center">
<h2 style="color:#006633">Supporters: {{count}}</h2>
<p>Yatta Mpya, Maendeleo Kwa Wote!</p>
</div>
<a href="{{wa_direct}}" class="float-wa">💬</a>
</body></html>
"""

ADMIN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;padding:10px;background:#e8f5e9}.card{background:white;padding:15px;border-radius:15px}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border:1px solid #ddd;font-size:11px}th{background:#006633;color:white}</style></head><body>
<div class="card"><a href="/">Home</a><h2>ADMIN - Mutua Campaign</h2>
<h3 style="color:#006633">TOTAL: KES {{total}} | Supporters: {{count}}</h3>
<table><tr><th>Date</th><th>Name</th><th>Phone</th><th>Ward</th><th>Code</th><th>Amount</th></tr>
{% for d in donations %}<tr><td>{{d[6]}}</td><td>{{d[1]}}</td><td>{{d[2]}}</td><td>{{d[3]}}</td><td>{{d[4]}}</td><td>KES {{d[5]}}</td></tr>{% endfor %}
</table></div></body></html>"""

@app.route("/")
def home():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM donations")
    count = c.fetchone()[0] or 0
    conn.close()
    return render_template_string(HOME_HTML, count=count, wa_group=WHATSAPP_GROUP, wa_direct=WHATSAPP_DIRECT, fb=FACEBOOK_LINK, tt=TIKTOK_LINK, ig=INSTAGRAM_LINK)

@app.route("/photo")
def photo():
    for name in ["mutua.jpg","mutua.png","mutua.webp"]:
        if os.path.exists(name):
            return send_from_directory(".", name)
    return "", 404

@app.route("/donate", methods=["POST"])
def donate():
    conn = get_conn()
    c = conn.cursor()
    date_now = datetime.now().strftime("%d/%m %H:%M")
    if DATABASE_URL:
        c.execute("INSERT INTO donations (name,phone,ward,mpesa_code,amount,date) VALUES (%s,%s,%s,%s,%s,%s)",
                  (request.form['name'], request.form['phone'], request.form['ward'], request.form['mpesa_code'], request.form['amount'], date_now))
    else:
        c.execute("INSERT INTO donations VALUES (NULL,?,?,?,?,?,?)",
                  (request.form['name'], request.form['phone'], request.form['ward'], request.form['mpesa_code'], request.form['amount'], date_now))
    conn.commit()
    conn.close()
    return "<h2 style='text-align:center;color:green;padding:50px'>Asante! Donation Imepokelewa<br><br><a href='/'>Rudi Nyuma</a></h2>"

@app.route("/admin")
def admin():
    pin = request.args.get('pin','')
    if pin != ADMIN_PIN:
        return f"<h3 style='text-align:center;padding:50px'>Access Denied! Tumia: /admin?pin={ADMIN_PIN}</h3>", 403
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM donations ORDER BY id DESC")
    donations = c.fetchall()
    c.execute("SELECT SUM(amount), COUNT(*) FROM donations")
    row = c.fetchone()
    total=row[0] or 0
    count=row[1] or 0
    conn.close()
    return render_template_string(ADMIN_HTML, donations=donations, total=total, count=count)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
