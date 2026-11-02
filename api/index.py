from flask import Flask, request, redirect, session, make_response
import requests, csv, io, os, re
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "yatta-2027-super-secret-12345")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
TABLE = "supporters"
VISITOR_TABLE = "visitors"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_supporters():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=*&order=created_at.desc&limit=2000", headers=HEADERS, timeout=10)
        if r.status_code == 200: return r.json()
    except: pass
    return []
def get_visitors():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}?select=*&order=created_at.desc&limit=500", headers=HEADERS, timeout=10)
        if r.status_code == 200: return r.json()
    except: pass
    return []
def get_total_views_counter():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/total_counter?id=eq.1&select=total_views", headers=HEADERS, timeout=5)
        if r.status_code == 200 and r.json(): return r.json()[0]['total_views']
    except: pass
    return 0
def increment_total_counter():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/total_counter?id=eq.1&select=total_views", headers=HEADERS, timeout=5)
        cur = r.json()[0]['total_views'] if r.status_code==200 and r.json() else 0
        requests.patch(f"{SUPABASE_URL}/rest/v1/total_counter?id=eq.1", json={"total_views": cur+1}, headers=HEADERS, timeout=3)
    except: pass
def log_visitor(req):
    try:
        ip = req.headers.get('X-Forwarded-For', req.remote_addr) or "unknown"
        agent = req.headers.get('User-Agent','')[:150]
        ref = req.headers.get('Referer','Direct')[:100]
        payload = {"name": "VISITOR", "place": str(ip)[:50], "msg": f"VIEW | {agent} | {ref}", "type": "visitor"}
        requests.post(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}", json=payload, headers=HEADERS, timeout=3)
        increment_total_counter()
    except: pass
def add_supporter(name, place, msg, s_type="ujumbe"):
    try:
        payload = {"name": name, "place": place, "msg": msg[:500], "type": s_type}
        requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", json=payload, headers=HEADERS, timeout=10)
    except: pass
def delete_supporter(sid):
    try:
        requests.delete(f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{sid}", headers=HEADERS, timeout=10)
    except: pass

def handle_download():
    key = request.args.get('key','')
    view = request.args.get('view','')
    # Ruhusu kama ako na session au key
    is_admin_session = session.get('is_admin') == True
    if key != ADMIN_PASSWORD and not is_admin_session:
        return "<h1 style='text-align:center;margin-top:50px'>Hautaruhusiwi</h1>", 401
    supporters = get_supporters()
    sigs = [s for s in supporters if s.get('type') == 'sahihi' or "SIG_ID" in str(s.get('msg',''))]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No", "Jina", "ID Number", "Kura Number", "Kituo"])
    for i, s in enumerate(sigs, 1):
        msg = s.get('msg','')
        id_no = ""; kura_no = ""; kituo = s.get('place','')
        try:
            if "SIG_ID:" in msg: id_no = msg.split("SIG_ID:")[1].split("|")[0].strip()
            if "KURA:" in msg: kura_no = msg.split("KURA:")[1].split("|")[0].strip()
        except: pass
        writer.writerow([i, s.get('name',''), id_no, kura_no, kituo])
    csv_data = output.getvalue()
    if view == "1":
        return f"<html><head><meta name='viewport' content='width=device-width'><title>YATTA LIST</title></head><body style='font-family:Arial;padding:20px'><h2>SAHIHI {len(sigs)} / 1000</h2><pre style='background:#f0f0f0;padding:15px;border-radius:10px;overflow:auto;white-space:pre-wrap'>{csv_data}</pre><br><button onclick=\"navigator.clipboard.writeText(document.querySelector('pre').innerText);alert('Copied!')\" style='background:#004d26;color:#fff;padding:12px 20px;border-radius:10px;border:none;font-weight:bold'>📋 COPY YOTE</button><br><br><a href='/'>← Rudi Home</a></body></html>"
    resp = make_response("\ufeff" + csv_data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f'attachment; filename="YATTA_SAHIHI_{len(sigs)}.csv"'
    return resp

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        pwd = request.form.get('password','')
        if pwd == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect('/')
        else:
            return "<h1 style='text-align:center;color:red;margin-top:50px'>Password si sahihi!</h1><div style='text-align:center'><a href='/admin'>Jaribu tena</a></div>"
    return """
    <html><head><meta name="viewport" content="width=device-width"><title>Admin Login</title></head>
    <body style="font-family:Arial;text-align:center;padding:30px;background:#004d26;color:white">
    <div style="background:white;color:#222;padding:30px;border-radius:20px;max-width:350px;margin:50px auto">
    <h2 style="color:#004d26">🔐 ADMIN LOGIN</h2>
    <form method="POST">
    <input type="password" name="password" placeholder="Weka Password ya Admin" required style="width:100%;padding:14px;border-radius:10px;border:1px solid #ccc;box-sizing:border-box">
    <button type="submit" style="width:100%;padding:14px;background:#004d26;color:white;border:none;border-radius:10px;margin-top:15px;font-weight:bold;cursor:pointer">INGIA ADMIN</button>
    </form>
    <br><a href="/" style="font-size:13px">← Rudi Home</a>
    </div></body></html>
    """

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect('/')

@app.route('/download')
def download_route():
    return handle_download()

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    if 'download' in path or 'download' in request.path:
        return handle_download()
    if 'admin' in path: return redirect('/admin')
    if request.method == 'GET' and 'favicon' not in path:
        log_visitor(request)
    
    # ADMIN CHECK - KWANZA SESSION, KISHA KEY (kwa backward compat)
    is_admin = session.get('is_admin') == True or request.args.get('admin') == ADMIN_PASSWORD or request.args.get('key') == ADMIN_PASSWORD
    
    futa_id = request.args.get('futa')
    admin_key = request.args.get('key')
    if futa_id is not None:
        if not is_admin and admin_key != ADMIN_PASSWORD:
            return f"<script>alert('Hautaruhusiwi!'); window.location='/';</script>"
        try: delete_supporter(int(futa_id))
        except: pass
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        place = request.form.get('place','').strip()
        msg = request.form.get('msg','').strip()
        form_type = request.form.get('form_type','')
        if form_type == 'mchango':
            amount = request.form.get('amount','').strip()
            if name and amount: add_supporter(name, f"MCHANGO {amount}", f"KES {amount}", "mchango")
        elif form_type == 'sig':
            id_no = request.form.get('id_no','').strip()
            voter_no = request.form.get('voter_no','').strip()
            station = request.form.get('station','').strip()
            if name and id_no and voter_no: add_supporter(name, station, f"SIG_ID:{id_no} | KURA:{voter_no} | KITUO:{station}", "sahihi")
        else:
            if len(msg) > 200: msg = msg[:200]
            if name and msg: add_supporter(name, place, msg, "ujumbe")
        return redirect('/')
    
    supporters = get_supporters()
    all_visitors = get_visitors() if is_admin else []
    total_views = get_total_views_counter()
    visitors = all_visitors
    michango_html = ""; msgs_html = ""; sigs_html = ""; visitors_html = ""
    total_michango = 0; count_michango = 0; count_msgs = 0; count_sigs = 0

    for v in visitors[:100]:
        visitors_html += f"<div style='background:#e3f2fd;padding:8px;margin:4px 0;border-radius:8px;font-size:11px;text-align:left'>👁️ {str(v.get('created_at',''))[:19]} | IP: {v.get('place','')} | {v.get('msg','')[:80]}</div>"
    if not visitors_html and is_admin: visitors_html = "<p style='color:#999'>Hakuna visitors bado</p>"

    def futa_link(sid):
        if is_admin:
            return f" <a href='/?futa={sid}&key={ADMIN_PASSWORD}' style='color:red;font-size:11px'>[FUTA]</a>"
        return ""

    for s in supporters:
        s_type = s.get('type','')
        if s_type == 'sahihi' or "SIG_ID" in str(s.get('msg','')):
            count_sigs += 1
            if is_admin:
                sigs_html += f"<div style='background:#e8f5e9;padding:10px;border-radius:10px;margin:6px 0;text-align:left;color:#222;border-left:5px solid #25D366;'>✅ <b>{s.get('name')} - {s.get('msg')} - {s.get('place')}</b>{futa_link(s.get('id'))}</div>"
            continue
        if s_type == 'mchango' or "MCHANGO" in str(s.get('msg','')).upper() or "MCHANGO" in str(s.get('place','')).upper():
            count_michango += 1
            try:
                m = re.search(r'\d+', s.get('place','') or s.get('msg',''))
                if m: total_michango += int(m.group(0))
            except: pass
            michango_html += f"<div style='background:#fff8dc;padding:10px;border-radius:10px;margin:6px 0;text-align:left;color:#222;border-left:5px solid gold;'>💰 <b>{s.get('name','')} - {s.get('place','')} - {s.get('msg','')}</b>{futa_link(s.get('id'))}</div>"
        else:
            count_msgs += 1
            if count_msgs <= 100: 
                msgs_html += f"<div style='background:#f0f7f0;padding:12px;border-radius:10px;margin:8px 0;text-align:left;color:#222;border-left:5px solid #004d26;'>💬 <b>{s.get('name','')} ({s.get('place','')}) - {s.get('msg','')}</b>{futa_link(s.get('id'))}</div>"

    if not msgs_html: msgs_html = "<p style='color:#999'>Hakuna ujumbe bado</p>"
    if not michango_html: michango_html = "<p style='color:#999'>Hakuna mchango bado</p>"
    if not sigs_html: sigs_html = "<p style='color:#999'>Hakuna sahihi bado</p>" if is_admin else ""

    michango_dropdown = f"<div style='margin-top:15px'><button onclick=\"let x=document.getElementById('mchango-list'); x.style.display=x.style.display=='none'?'block':'none'\" style='background:#FFD700;color:#000;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;cursor:pointer'>▼ ONA WALIOTUMA WOTE ({count_michango})</button><div id='mchango-list' style='display:none; max-height:350px; overflow-y:auto; border:2px solid gold; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{michango_html}</div></div>"
    msgs_dropdown = f"<div style='margin-top:10px'><button onclick=\"let x=document.getElementById('msg-list'); x.style.display=x.style.display=='none'?'block':'none'\" style='background:#004d26;color:white;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;cursor:pointer'>▼ ONA UJUMBE WOTE ({count_msgs})</button><div id='msg-list' style='display:none; max-height:350px; overflow-y:auto; border:2px solid #004d26; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{msgs_html}</div></div>"

    if is_admin:
        sigs_dropdown = f"<div style='margin-top:10px'><div style='background:#25D366;color:white;padding:12px 15px;border-radius:10px;font-weight:bold;'>▼ SAHIHI ZOTE ({count_sigs}) - ADMIN</div><div style='max-height:500px; overflow-y:auto; border:2px solid #25D366; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{sigs_html}</div></div>"
        visitors_dropdown = f"<div style='margin-top:15px'><div style='background:#2196F3;color:white;padding:12px 15px;border-radius:10px;font-weight:bold;'>▼ WALIOTEMBELEA ({total_views})</div><div style='max-height:400px; overflow-y:auto; border:2px solid #2196F3; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{visitors_html}</div></div>"
        download_btn = f"""<div style='margin-top:15px;display:flex;flex-direction:column;gap:10px'><a href='/download?key={ADMIN_PASSWORD}' style='display:block;background:#000;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:bold;text-align:center'>📥 DOWNLOAD - KOMPYUTA ({count_sigs})</a><a href='/download?key={ADMIN_PASSWORD}&view=1' style='display:block;background:#2196F3;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:bold;text-align:center'>📄 ONA & COPY - KWA SIMU ({count_sigs})</a><br><a href='/logout' style='display:block;background:red;color:#fff;padding:10px;border-radius:10px;text-decoration:none;text-align:center'>🚪 LOGOUT ADMIN</a></div>"""
        admin_banner = f"<p style='background:red;padding:10px;border-radius:10px'>🔓 ADMIN MODE - {count_sigs} sahihi | <a href='/logout' style='color:white'>Logout</a></p>"
    else:
        sigs_dropdown = f"<p style='font-size:12px;color:#666;background:#e8f5e9;padding:12px;border-radius:8px;text-align:center'>🔒 Asante! Sahihi yako imehifadhiwa kwa siri.<br>📊 <b>{count_sigs} / 1000</b> zimesajiliwa.</p>"
        visitors_dropdown = ""
        download_btn = f"<div style='text-align:center;margin-top:15px'><a href='/admin' style='font-size:12px;color:#666;text-decoration:none'>🔐 Admin Login</a></div>"
        admin_banner = ""

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MUTUA WA KATANGI</title>
<style>body{{margin:0;font-family:Arial;background:#004d26;color:white;text-align:center}}.header{{padding:20px 15px}}.card{{background:white;color:#222;padding:20px;border-radius:20px;margin:15px}}.btn{{display:block;padding:14px;margin:8px 0;border-radius:12px;text-decoration:none;font-weight:bold;color:white;cursor:pointer;border:none;width:100%;box-sizing:border-box}}.wa{{background:#25D366}}.gold{{background:#FFD700;color:#000}}.pochi-box{{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;padding:20px;border-radius:15px;font-weight:bold;border:3px solid #004d26}}.copy-btn{{background:#004d26;color:white;padding:10px 15px;border-radius:8px;border:none;font-weight:bold;cursor:pointer;margin:5px}}img{{width:160px;height:160px;border-radius:50%;border:4px solid gold;object-fit:cover;background:white}}input,textarea,select{{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}}.submit{{background:#004d26;color:white;border:none;font-weight:bold;cursor:pointer}}</style>
<script>function copyPochi(){{navigator.clipboard.writeText('0796069040');alert('Namba 0796069040 ime-COPY!');}}</script>
</head><body>
<div style="background:#111;padding:12px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;position:sticky;top:0;z-index:999"><a href="https://www.facebook.com/share/1A5o1f48R6/" target="_blank" style="background:#1877F2;color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">📘 Facebook</a><a href="https://www.instagram.com/daudidenismutua" target="_blank" style="background:linear-gradient(45deg,#feda75,#fa7e1e,#d62976,#962fbf,#4f5bd5);color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">📸 Instagram</a><a href="https://www.tiktok.com/@mutuawakatangi" target="_blank" style="background:#000;color:white;border:1px solid #444;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">🎵 TikTok</a><a href="https://x.com/denis_mutua_d" target="_blank" style="background:white;color:black;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">🐦 Twitter</a><a href="https://wa.me/254796069040" target="_blank" style="background:#25D366;color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">💬 WhatsApp</a><a href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH" target="_blank" style="background:#128C7E;color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">👥 Group</a></div>
<div class="header"><img src="https://raw.githubusercontent.com/denismutua4/Yatta-2027/main/mutua.jpg"><h1>🔥 MUTUA WA KATANGI 🔥</h1><h2 style="color:gold;margin:0">YATTA MP 2027 - INDEPENDENT</h2><p>Yatta Mpya, Maendeleo Kwa Wote</p>{admin_banner}</div>
<div class="card" style="border:3px solid #25D366;background:#f0fff0"><h2 style="color:#004d26;margin:0">✅ SAJILI SAHIHI YA IEBC</h2><p style="font-size:13px">Tunahitaji sahihi 1000 za Yatta</p><p style="font-size:14px;background:#004d26;color:white;padding:10px;border-radius:10px">📊 Sahihi: <b>{count_sigs} / 1000</b> | 👁️ Views: <b>{total_views}</b></p><form method="POST"><input type="hidden" name="form_type" value="sig"><input name="name" placeholder="Jina kamili kama ID" required><input name="id_no" placeholder="Namba ya ID" required type="number"><input name="voter_no" placeholder="Namba ya Kura" required><input name="station" placeholder="Kituo cha Kura" required><input class="submit btn wa" type="submit" value="SAJILI SAHIHI YANGU ✅"></form>{sigs_dropdown}{visitors_dropdown}{download_btn}</div>
<div class="card"><div class="pochi-box"><h2 style="margin:0;color:#004d26">💰 CHANGIA KAMPENI YETU</h2><p>POCHI LA BIASHARA</p><h1>0796069040</h1><button class="copy-btn" onclick="copyPochi()">📋 COPY</button><a href="tel:*334%23" class="copy-btn" style="text-decoration:none;display:inline-block;background:#000">📞 LIPA *334#</a><p style="font-size:13px;background:white;padding:8px;border-radius:8px;margin-top:10px">✅ Michango: {count_michango} | 💵 Jumla: KES {total_michango}</p></div><br><a class="btn wa" href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH">JOIN WHATSAPP GROUP</a></div>
<div class="card"><h2 style="color:#004d26">💰 THIBITISHA MCHANGO</h2><form method="POST"><input type="hidden" name="form_type" value="mchango"><input name="name" placeholder="Jina lako" required><select name="amount" required><option value="">Chagua Kiasi</option><option value="100">100</option><option value="200">200</option><option value="500">500</option><option value="1000">1,000</option><option value="2000">2,000</option><option value="5000">5,000</option></select><input class="submit btn gold" type="submit" value="THIBITISHA MCHANGO ✅"></form>{michango_dropdown}</div>
<div class="card"><h2 style="color:#004d26">✍️ ANDIKA UJUMBE</h2><form method="POST"><input type="hidden" name="form_type" value="ujumbe"><input name="name" placeholder="Jina lako" required><input name="place" placeholder="Mahali (Matuu)" required><textarea name="msg" placeholder="Ujumbe wako..." rows="3" required maxlength="200"></textarea><input class="submit btn" type="submit" value="TUMA UJUMBE 🔥"></form></div>
<div class="card"><h3 style="color:#004d26">💬 UJUMBE WA WANA-YATTA ({count_msgs})</h3>{msgs_dropdown}</div>
</body></html>
"""
