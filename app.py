from flask import Flask, render_template_string, request, send_from_directory
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
DB = 'campaign.db'
ADMIN_PIN = "2027"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS donations
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, ward TEXT, mpesa_code TEXT, amount INTEGER, date TEXT)''')
    conn.commit(); conn.close()
init_db()

HOME_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MUTUA WA KATANGI - YATTA MP 2027</title>
<style>
body{font-family:Arial;background:#e8f5e9;padding:10px;margin:0}
.card{background:white;border-radius:15px;padding:20px;margin:10px 0;box-shadow:0 3px 10px #ccc}
.green{background:linear-gradient(135deg,#004d26,#006633);color:white;text-align:center;padding:30px 20px}
input,select,button{padding:14px;margin:8px 0;width:100%;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}
button{background:#006633;color:white;font-weight:bold;border:none;font-size:18px}
.badge{background:#FFD700;color:#006633;padding:8px 15px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px}
.profile{width:150px;height:150px;border-radius:50%;border:4px solid #FFD700;object-fit:cover;object-position:top center;margin-bottom:15px;box-shadow:0 4px 15px rgba(0,0,0,0.4)}
</style></head><body>
<div class="card green">
<img src="/photo" class="profile" onerror="this.style.display='none'">
<h1 style="margin:10px 0">MUTUA WA KATANGI</h1>
<h2 style="color:#FFD700;margin:5px 0">YATTA MP 2027</h2>
<p style="margin:5px 0;font-size:13px;letter-spacing:2px">MEMBER OF PARLIAMENT</p>
<span class="badge">POCHI: 0796069040</span>
<p style="font-size:11px;margin-top:10px;opacity:0.9;letter-spacing:1px">Kamati Rasmi ya Campaign - Yatta 2027</p>
</div>
<div class="card" style="border:3px solid #006633">
<h3 style="color:#006633;text-align:center">LIPA: DIAL *334# -> Pochi 0796069040</h3>
<form method="POST" action="/donate">
<input name="name" placeholder="Jina lako" required>
<input name="phone" placeholder="07..." required>
<select name="ward" required>
<option value="">Chagua Ward</option>
<option>Katangi</option><option>Matuu</option><option>Kithimani</option><option>Ikombe</option><option>Ndalani</option>
</select>
<input name="mpesa_code" placeholder="M-Pesa Code" required>
<input name="amount" type="number" placeholder="Amount" required>
<button>CONFIRM DONATION</button>
</form>
</div>
<div class="card" style="background:#fff9c4;text-align:center">
<h2 style="color:#006633">Supporters: {{count}} 🎉</h2>
<p>Asanteni Sana kwa Support Yenu!</p>
</div>
</body></html>
"""

ADMIN_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;padding:10px;background:#e8f5e9}
.card{background:white;padding:15px;border-radius:15px}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border:1px solid #ddd;font-size:12px}
th{background:#006633;color:white}</style></head><body>
<div class="card">
<a href="/">← Home</a>
<h2>ADMIN - Mutua Campaign</h2>
<h3 style="color:#006633">TOTAL: KES {{total}} | Supporters: {{count}}</h3>
<table><tr><th>Date</th><th>Name</th><th>Phone</th><th>Ward</th><th>Code</th><th>Amount</th></tr>
{% for d in donations %}
<tr><td>{{d[6]}}</td><td>{{d[1]}}</td><td>{{d[2]}}</td><td>{{d[3]}}</td><td>{{d[4]}}</td><td>KES {{d[5]}}</td></tr>
{% endfor %}
</table>
</div>
</body></html>
"""

@app.route("/")
def home():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM donations")
    count = c.fetchone()[0] or 0
    conn.close()
    return render_template_string(HOME_HTML, count=count)

@app.route("/photo")
def photo():
    for name in ["mutua.jpg","mutua.png","mutua.webp","image_20261025_135651.webp","image_20261025_134551.webp"]:
        if os.path.exists(name):
            return send_from_directory(".", name)
    return "", 404

@app.route("/donate", methods=["POST"])
def donate():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO donations VALUES (NULL,?,?,?,?,?,?)",
              (request.form['name'], request.form['phone'], request.form['ward'], request.form['mpesa_code'], request.form['amount'], datetime.now().strftime("%d/%m %H:%M")))
    conn.commit(); conn.close()
    return "<h2 style='text-align:center;color:green;padding:50px'>Asante! Donation Yako Imepokelewa<br><br><a href='/'>Rudi Nyuma</a></h2>"

@app.route("/admin")
def admin():
    pin = request.args.get('pin','')
    if pin != ADMIN_PIN:
        return "<h3 style='text-align:center;padding:50px'>Access Denied! Weka ?pin=2027</h3>", 403
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT * FROM donations ORDER BY id DESC")
    donations = c.fetchall()
    c.execute("SELECT SUM(amount), COUNT(*) FROM donations")
    row = c.fetchone(); total=row[0] or 0; count=row[1] or 0
    conn.close()
    return render_template_string(ADMIN_HTML, donations=donations, total=total, count=count)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)