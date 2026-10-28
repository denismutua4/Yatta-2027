from flask import Flask, request, redirect
import requests

app = Flask(__name__)

SUPABASE_URL = "https://ccskbtbfbxysocrlzkou.supabase.co"
SUPABASE_KEY = "sb_publishable_ZizSNK8wSNHTBrnae5i-Mw_muX2QpIN"
TABLE = "supporters"
ADMIN_PASSWORD = "Yatta2027Mutua"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_supporters():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=*&order=created_at.desc&limit=100", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except: pass
    return []

def add_supporter(name, place, msg):
    try:
        payload = {"name": name, "place": place, "msg": msg[:200]}
        requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", json=payload, headers=HEADERS, timeout=10)
    except: pass

def delete_supporter(sid):
    try:
        requests.delete(f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{sid}", headers=HEADERS, timeout=10)
    except: pass

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    futa_id = request.args.get('futa')
    admin_key = request.args.get('key')
    if futa_id is not None:
        if admin_key != ADMIN_PASSWORD:
            return f"<script>alert('Hautaruhusiwi!'); window.location='/';</script>"
        try:
            delete_supporter(int(futa_id))
        except: pass
        return redirect('/')

    if request.method == 'POST':
        name = request.form.get('name','').strip()
        place = request.form.get('place','').strip()
        msg = request.form.get('msg','').strip()
        form_type = request.form.get('form_type','')
        
        if form_type == 'mchango':
            amount = request.form.get('amount','').strip()
            if name and amount:
                msg = f"💰 MCHANGO KES {amount} - Thibitisho"
                add_supporter(name, f"MCHANGO {amount}", msg)
        else:
            if len(msg) > 200: msg = msg[:200]
            if name and msg:
                add_supporter(name, place, msg)
        return redirect('/')

    supporters = get_supporters()
    
    michango_html = ""
    msgs_html = ""
    total_michango = 0
    count_michango = 0
    
    for s in supporters[:100]:
        safe_msg = f"{s.get('name','')} ({s.get('place','')}) - {s.get('msg','')}"
        is_mchango = "MCHANGO" in str(s.get('place','')).upper() or "MCHANGO" in str(s.get('msg','')).upper()
        
        if is_mchango:
            count_michango += 1
            try:
                amt_str = ''.join(filter(str.isdigit, s.get('place','')))
                if amt_str: total_michango += int(amt_str)
            except: pass
            michango_html += f"<div style='background:#fff8dc;padding:10px;border-radius:10px;margin:6px 0;text-align:left;color:#222;border-left:5px solid gold;'>💰 <b>{safe_msg}</b></div>"
        else:
            msgs_html += f"<div style='background:#f0f7f0;padding:12px;border-radius:10px;margin:8px 0;text-align:left;color:#222;border-left:5px solid #004d26;display:flex;justify-content:space-between;align-items:center'><div style='flex:1'>💬 <b>{safe_msg}</b></div><a href='#' onclick=\"let p=prompt('Weka Password ya Admin:'); if(p) window.location='/?futa={s.get('id')}&key='+p; return false;\" style='background:red;color:white;padding:5px 10px;border-radius:6px;text-decoration:none;font-size:12px;margin-left:10px'>🗑️</a></div>"
    
    if not supporters:
        msgs_html = "<p style='color:#999'>Hakuna ujumbe bado</p>"
    if not michango_html:
        michango_html = "<p style='color:#999;font-size:13px'>Hakuna mchango bado</p>"

    # DROPDOWN VERSION - hapa ndipo tofauti
    michango_dropdown = f"""
    <div style="margin-top:15px">
        <button onclick="let x=document.getElementById('mchango-list'); x.style.display=x.style.display=='none'?'block':'none'; this.innerText=x.style.display=='none'?'▼ ONA WALIOTUMA WOTE ({count_michango})':'▲ FUNGA ORODHA'" 
        style="background:#FFD700;color:#000;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;cursor:pointer">
        ▼ ONA WALIOTUMA WOTE ({count_michango})
        </button>
        <div id="mchango-list" style="display:none; max-height:350px; overflow-y:auto; border:2px solid gold; border-radius:12px; margin-top:10px; padding:10px; background:#fff;">
            {michango_html}
        </div>
    </div>
    """

    return f"""
<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MUTUA WA KATANGI - YATTA MP 2027</title>
<style>
body{{margin:0;font-family:Arial;background:#004d26;color:white;text-align:center}}
.header{{padding:20px 15px}}.card{{background:white;color:#222;padding:20px;border-radius:20px;margin:15px}}
.btn{{display:block;padding:14px;margin:8px 0;border-radius:12px;text-decoration:none;font-weight:bold;color:white;cursor:pointer;border:none;width:100%;box-sizing:border-box}}
.wa{{background:#25D366}}.gold{{background:#FFD700;color:#000}}.fb{{background:#1877F2}}.tt{{background:#000}}.ig{{background:linear-gradient(45deg,#f09433,#dc2743)}}
.pochi-box{{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;padding:20px;border-radius:15px;font-weight:bold;border:3px solid #004d26}}
.copy-btn{{background:#004d26;color:white;padding:10px 15px;border-radius:8px;border:none;font-weight:bold;cursor:pointer;margin:5px}}
img{{width:160px;height:160px;border-radius:50%;border:4px solid gold;object-fit:cover;background:white}}
input,textarea,select{{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}}
.submit{{background:#004d26;color:white;border:none;font-weight:bold;cursor:pointer}}
</style>
<script>
function copyPochi() {{
  navigator.clipboard.writeText('0796069040');
  alert('Namba 0796069040 ime-COPY! Nenda M-Pesa *334#');
}}
</script>
</head><body>
<div class="header">
<img src="https://raw.githubusercontent.com/denismutua4/Yatta-2027/main/mutua.jpg">
<h1>🔥 MUTUA WA KATANGI 🔥</h1>
<h2 style="color:gold;margin:0">YATTA MP 2027</h2>
<p>Yatta Mpya, Maendeleo Kwa Wote</p>
</div>
<div class="card">
<div class="pochi-box">
<h2 style="margin:0;color:#004d26">💰 CHANGIA KAMPENI YETU</h2>
<p style="margin:5px 0">POCHI LA BIASHARA</p>
<h1 style="margin:10px 0;letter-spacing:2px">0796069040</h1>
<p style="margin:5px 0;font-size:14px">Jina: Mutua wa Katangi</p>
<button class="copy-btn" onclick="copyPochi()">📋 COPY NAMBA</button>
<a href="tel:*334%23" class="copy-btn" style="text-decoration:none;display:inline-block;background:#000">📞 LIPA *334#</a>
<p style="font-size:12px;margin-top:10px;color:#333">Lipa na M-Pesa: Lipa na Pochi -> Biashara -> 0796069040</p>
<p style="font-size:13px;background:white;padding:8px;border-radius:8px;margin-top:10px">✅ Michango: {count_michango} | 💵 Jumla: KES {total_michango}</p>
</div>
<br>
<a class="btn wa" href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH">JOIN WHATSAPP GROUP</a>
<a class="btn gold" href="https://wa.me/254796069040?text=Niko%20tayari%20Yatta%202027">WHATSAPP DIRECT</a>
</div>
<div class="card">
<h2 style="color:#004d26">💰 THIBITISHA MCHANGO</h2>
<form method="POST">
<input type="hidden" name="form_type" value="mchango">
<input name="name" placeholder="Jina lako" required>
<select name="amount" required>
<option value="">Chagua Kiasi</option>
<option value="100">100</option><option value="200">200</option><option value="500">500</option>
<option value="1000">1,000</option><option value="2000">2,000</option><option value="5000">5,000</option><option value="10000">10,000+</option>
</select>
<input class="submit btn gold" type="submit" value="THIBITISHA MCHANGO ✅">
</form>
{michango_dropdown}
</div>
<div class="card">
<h2 style="color:#004d26">✍️ ANDIKA UJUMBE WA SUPPORT</h2>
<form method="POST">
<input type="hidden" name="form_type" value="ujumbe">
<input name="name" placeholder="Jina lako" required>
<input name="place" placeholder="Mahali (Matuu)" required>
<textarea name="msg" placeholder="Ujumbe wako..." rows="3" required maxlength="200"></textarea>
<input class="submit btn" type="submit" value="TUMA UJUMBE 🔥">
</form>
</div>
<div class="card">
<h3 style="color:#004d26">💬 UJUMBE WA WANA-YATTA ({len(supporters)})</h3>
{msgs_html}
</div>
<p style="padding:15px;font-size:14px">© 2027 Mutua wa Katangi</p>
</body></html>
"""
