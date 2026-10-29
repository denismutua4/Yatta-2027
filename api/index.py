from flask import Flask, request, redirect, Response
import requests
import csv, io

app = Flask(__name__)

SUPABASE_URL = "https://ccskbtbfbxysocrlzkou.supabase.co"
SUPABASE_KEY = "sb_publishable_ZizSNK8wSNHTBrnae5i-Mw_muX2QpIN"
TABLE = "supporters"
VISITOR_TABLE = "visitors"
ADMIN_PASSWORD = "Yatta2027Mutua"

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

def log_visitor(req):
    try:
        ip = req.headers.get('X-Forwarded-For', req.remote_addr) or "unknown"
        agent = req.headers.get('User-Agent','')[:150]
        ref = req.headers.get('Referer','Direct')[:100]
        payload = {"name": "VISITOR", "place": str(ip)[:50], "msg": f"VIEW | {agent} | {ref}"}
        requests.post(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}", json=payload, headers=HEADERS, timeout=3)
    except: pass

def add_supporter(name, place, msg):
    try:
        payload = {"name": name, "place": place, "msg": msg[:500]}
        requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", json=payload, headers=HEADERS, timeout=10)
    except: pass

# ===== HII NDIO USIFUTE - HII NDIO DOWNLOAD =====
@app.route('/download')
def download():
    key = request.args.get('key','')
    view = request.args.get('view','')
    if key != ADMIN_PASSWORD:
        return "<h1 style='text-align:center;margin-top:50px'>Hautaruhusiwi</h1>"
    supporters = get_supporters()
    sigs = [s for s in supporters if "SIG_ID" in str(s.get('msg',''))]
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
        return f"<html><head><meta name='viewport' content='width=device-width'><title>YATTA LIST</title></head><body style='font-family:Arial;padding:20px'><h2>SAHIHI {len(sigs)} / 1000</h2><pre style='background:#f0f0f0;padding:15px;border-radius:10px;overflow:auto;white-space:pre-wrap'>{csv_data}</pre><br><button onclick=\"navigator.clipboard.writeText(document.querySelector('pre').innerText);alert('Copied!')\" style='background:#004d26;color:#fff;padding:12px 20px;border-radius:10px;border:none;font-weight:bold'>📋 COPY YOTE</button><br><br><a href='/?admin={ADMIN_PASSWORD}'>← Rudi Admin</a></body></html>"
    csv_data = "\ufeff" + csv_data
    return Response(csv_data, mimetype="text/csv; charset=utf-8", headers={"Content-Disposition": f"attachment; filename=YATTA_SAHIHI_{len(sigs)}.csv"})

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    if request.method == 'GET' and 'favicon' not in path and 'download' not in path:
        log_visitor(request)
    is_admin = request.args.get('admin') == ADMIN_PASSWORD or request.args.get('key') == ADMIN_PASSWORD
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        place = request.form.get('place','').strip()
        msg = request.form.get('msg','').strip()
        form_type = request.form.get('form_type','')
        if form_type == 'mchango':
            amount = request.form.get('amount','').strip()
            if name and amount: add_supporter(name, f"MCHANGO {amount}", f"MCHANGO KES {amount}")
        elif form_type == 'sig':
            id_no = request.form.get('id_no','').strip()
            voter_no = request.form.get('voter_no','').strip()
            station = request.form.get('station','').strip()
            if name and id_no and voter_no: add_supporter(name, station, f"SIG_ID:{id_no} | KURA:{voter_no} | KITUO:{station} | SIG")
        else:
            if len(msg) > 200: msg = msg[:200]
            if name and msg: add_supporter(name, place, msg)
        return redirect('/')
    supporters = get_supporters()
    all_visitors = get_visitors()
    total_views = len(all_visitors)
    count_sigs = len([s for s in supporters if "SIG_ID" in str(s.get('msg',''))])
    if not is_admin:
        return f"<h1 style='text-align:center'>MUTUA WA KATANGI</h1><p style='text-align:center'>Sahihi: {count_sigs}/1000 | <a href='/?admin={ADMIN_PASSWORD}'>Admin</a></p>"
    download_btn = f"""
        <div style='margin-top:15px;display:flex;flex-direction:column;gap:10px'>
        <a href='/download?key={ADMIN_PASSWORD}' style='display:block;background:#000;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:bold;text-align:center'>📥 DOWNLOAD - KOMPYUTA ({count_sigs})</a>
        <a href='/download?key={ADMIN_PASSWORD}&view=1' style='display:block;background:#2196F3;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:bold;text-align:center'>📄 ONA & COPY - KWA SIMU ({count_sigs})</a>
        <button onclick="fetch('/download?key={ADMIN_PASSWORD}').then(r=>r.text()).then(t=>{{let b=new Blob(['\\ufeff'+t],{{type:'text/csv'}});let u=URL.createObjectURL(b);let a=document.createElement('a');a.href=u;a.download='YATTA_SAHIHI_{count_sigs}.csv';document.body.appendChild(a);a.click();a.remove();alert('Imedownload! Angalia Downloads')}})" style='background:#FFD700;color:#000;padding:14px;border-radius:10px;font-weight:bold;width:100%;border:none;cursor:pointer'>📱 DOWNLOAD KWA SIMU - BONyeza HAPA! ({count_sigs})</button>
        </div>
        """
    return f"<html><body style='font-family:Arial;padding:20px;text-align:center'><h1>ADMIN MODE - {count_sigs} sahihi</h1>{download_btn}<br><a href='/'>Home</a></body></html>"
