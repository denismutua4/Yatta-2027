from flask import Flask, request, redirect, Response
import requests, csv, io, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ccskbtbfbxysocrlzkou.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Yatta2027Mutua")
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
        if r.status_code == 200 and r.json():
            return r.json()[0]['total_views']
    except: pass
    return 0

def increment_total_counter():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/total_counter?id=eq.1&select=total_views", headers=HEADERS, timeout=5)
        cur = r.json()[0]['total_views'] if r.status_code==200 and r.json() else 0
        requests.patch(f"{SUPABASE_URL}/rest/v1/total_counter?id=eq.1", json={"total_views": cur+1}, headers=HEADERS, timeout=3)
    except: pass

def cleanup_old_visitors():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}?select=id", headers={**HEADERS, "Prefer": "count=exact"}, timeout=5)
        total = int(r.headers.get('Content-Range','').split('/')[-1]) if r.headers.get('Content-Range') else 0
        if total >= 10000:
            r2 = requests.get(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}?select=id&order=created_at.desc&limit=8000", headers=HEADERS, timeout=10)
            if r2.status_code == 200 and r2.json():
                keep = ",".join([str(x['id']) for x in r2.json()])
                requests.delete(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}?id=not.in.({keep})", headers=HEADERS, timeout=15)
    except: pass

def log_visitor(req):
    try:
        ip = req.headers.get('X-Forwarded-For', req.remote_addr) or "unknown"
        agent = req.headers.get('User-Agent','')[:150]
        ref = req.headers.get('Referer','Direct')[:100]
        payload = {"name": "VISITOR", "place": str(ip)[:50], "msg": f"VIEW | {agent} | {ref}"}
        requests.post(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}", json=payload, headers=HEADERS, timeout=3)
        increment_total_counter()
        cleanup_old_visitors()
    except: pass

def add_supporter(name, place, msg):
    try:
        payload = {"name": name, "place": place, "msg": msg[:500]}
        requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", json=payload, headers=HEADERS, timeout=10)
    except: pass

def delete_supporter(sid):
    try:
        requests.delete(f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{sid}", headers=HEADERS, timeout=10)
    except: pass

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
    futa_id = request.args.get('futa')
    admin_key = request.args.get('key')
    if futa_id is not None:
        if admin_key != ADMIN_PASSWORD:
            return f"<script>alert('Hautaruhusiwi!'); window.location='/';</script>"
        try: delete_supporter(int(futa_id))
        except: pass
        return redirect(f'/?admin={ADMIN_PASSWORD}' if is_admin else '/')
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
    total_views = get_total_views_counter()
    visitors = all_visitors if is_admin else []
    michango_html = ""; msgs_html = ""; sigs_html = ""; visitors_html = ""
    total_michango = 0; count_michango = 0; count_msgs = 0; count_sigs = 0
    for v in visitors[:100]:
        visitors_html += f"<div style='background:#e3f2fd;padding:8px;margin:4px 0;border-radius:8px;font-size:11px;text-align:left'>👁️ {str(v.get('created_at',''))[:19]} | IP: {v.get('place','')} | {v.get('msg','')[:80]}</div>"
    if not visitors_html and is_admin: visitors_html = "<p style='color:#999'>Hakuna visitors bado</p>"
    for s in supporters:
        if "SIG_ID" in str(s.get('msg','')):
            count_sigs += 1
            if is_admin: sigs_html += f"<div style='background:#e8f5e9;padding:10px;border-radius:10px;margin:6px 0;text-align:left;color:#222;border-left:5px solid #25D366;'>✅ <b>{s.get('name')} - {s.get('msg')} - {s.get('place')}</b></div>"
            continue
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
            count_msgs += 1
            if count_msgs <= 100: msgs_html += f"<div style='background:#f0f7f0;padding:12px;border-radius:10px;margin:8px 0;text-align:left;color:#222;border-left:5px solid #004d26;'>💬 <b>{safe_msg}</b></div>"
    if not msgs_html: msgs_html = "<p style='color:#999'>Hakuna ujumbe bado</p>"
    if not michango_html: michango_html = "<p style='color:#999'>Hakuna mchango bado</p>"
    if not sigs_html: sigs_html = "<p style='color:#999'>Hakuna sahihi bado</p>" if is_admin else ""
    michango_dropdown = f"<div style='margin-top:15px'><button onclick=\"let x=document.getElementById('mchango-list'); x.style.display=x.style.display=='none'?'block':'none'\" style='background:#FFD700;color:#000;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;cursor:pointer'>▼ ONA WALIOTUMA WOTE ({count_michango})</button><div id='mchango-list' style='display:none; max-height:350px; overflow-y:auto; border:2px solid gold; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{michango_html}</div></div>"
    msgs_dropdown = f"<div style='margin-top:10px'><button onclick=\"let x=document.getElementById('msg-list'); x.style.display=x.style.display=='none'?'block':'none'\" style='background:#004d26;color:white;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;cursor:pointer'>▼ ONA UJUMBE WOTE ({count_msgs})</button><div id='msg-list' style='display:none; max-height:350px; overflow-y:auto; border:2px solid #004d26; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{msgs_html}</div></div>"
    if is_admin:
        sigs_dropdown = f"<div style='margin-top:10px'><div style='background:#25D366;color:white;padding:12px 15px;border-radius:10px;font-weight:bold;'>▼ SAHIHI ZOTE ({count_sigs}) - ADMIN</div><div style='max-height:500px; overflow-y:auto; border:2px solid #25D366; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{sigs_html}</div></div>"
        download_btn = f"""<div style='margin-top:15px;display:flex;flex-direction:column;gap:10px'><a href='/download?key={ADMIN_PASSWORD}' style='display:block;background:#000;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:bold;text-align:center'>📥 DOWNLOAD - KOMPYUTA ({count_sigs})</a><a href='/download?key={ADMIN_PASSWORD}&view=1' style='display:block;background:#2196F3;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:bold;text-align:center'>📄 ONA & COPY - KWA SIMU ({count_sigs})</a></div>"""
        visitors_dropdown = f"<div style='margin-top:15px'><div style='background:#2196F3;color:white;padding:12px 15px;border-radius:10px;font-weight:bold;'>▼ WALIOTEMBELEA ({total_views})</div><div style='max-height:400px; overflow-y:auto; border:2px solid #2196F3; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{visitors_html}</div></div>"
    else:
        sigs_dropdown = "<p style='font-size:12px;color:#666;background:#e8f5e9;padding:10px;border-radius:8px'>🔒 <b>Data yako ni siri</b></p>"
        download_btn = "<a href='#' onclick=\"let p=prompt('Weka Password:'); if(p) window.location='/download?key='+p; return false;\" style='display:block;margin-top:15px;background:#444;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold'>🔒 DOWNLOAD - Admin Tu</a>"
        visitors_dropdown = ""
    admin_banner = f"<p style='background:red;padding:10px;border-radius:10px'>🔓 ADMIN MODE - {count_sigs} sahihi</p>" if is_admin else ""
    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MUTUA WA KATANGI</title>
<style>body{{margin:0;font-family:Arial;background:#004d26;color:white;text-align:center}}.header{{padding:20px 15px}}.card{{background:white;color:#222;padding:20px;border-radius:20px;margin:15px}}.btn{{display:block;padding:14px;margin:8px 0;border-radius:12px;text-decoration:none;font-weight:bold;color:white;cursor:pointer;border:none;width:100%;box-sizing:border-box}}.wa{{background:#25D366}}.gold{{background:#FFD700;color:#000}}.pochi-box{{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;padding:20px;border-radius:15px;font-weight:bold;border:3px solid #004d26}}.copy-btn{{background:#004d26;color:white;padding:10px 15px;border-radius:8px;border:none;font-weight:bold;cursor:pointer;margin:5px}}img{{width:160px;height:160px;border-radius:50%;border:4px solid gold;object-fit:cover;background:white}}input,textarea,select{{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}}.submit{{background:#004d26;color:white;border:none;font-weight:bold;cursor:pointer}}</style>
<script>function copyPochi(){{navigator.clipboard.writeText('0796069040');alert('Namba 0796069040 ime-COPY!');}}</script>
</head><body>
<div style="background:#111;padding:12px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;position:sticky;top:0;z-index:999"><a href="https://www.facebook.com/share/1A5o1f48R6/" target="_blank" style="background:#1877F2;color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">📘 Facebook</a><a href="https://www.instagram.com/daudidenismutua" target="_blank" style="background:linear-gradient(45deg,#feda75,#fa7e1e,#d62976,#962fbf,#4f5bd5);color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">📸 Instagram</a><a href="https://www.tiktok.com/@mutuawakatangi" target="_blank" style="background:#000;color:white;border:1px solid #444;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">🎵 TikTok</a><a href="https://x.com/denis_mutua_d" target="_blank" style="background:white;color:black;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">🐦 Twitter</a><a href="https://wa.me/254796069040" target="_blank" style="background:#25D366;color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">💬 WhatsApp</a><a href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH" target="_blank" style="background:#128C7E;color:white;padding:8px 14px;border-radius:20px;text-decoration:none;font-weight:bold;font-size:13px">👥 Group</a></div>
<div class="header"><img src="https://raw.githubusercontent.com/denismutua4/Yatta-2027/main/mutua.jpg"><h1>🔥 MUTUA WA KATANGI 🔥</h1><h2 style="color:gold;margin:0">YATTA MP 2027 - INDEPENDENT</h2><p>Yatta Mpya, Maendeleo Kwa Wote</p>{admin_banner}</div>
<div class="card" style="border:3px solid #25D366;background:#f0fff0"><h2 style="color:#004d26;margin:0">✅ SAJILI SAHIHI YA IEBC</h2><p style="font-size:13px">Tunahitaji sahihi 1000 za Yatta</p><p style="font-size:14px;background:#004d26;color:white;padding:10px;border-radius:10px">📊 Sahihi: <b>{count_sigs} / 1000</b> | 👁️ Views Siku 3: <b>{total_views}</b></p><form method="POST"><input type="hidden" name="form_type" value="sig"><input name="name" placeholder="Jina kamili kama ID" required><input name="id_no" placeholder="Namba ya ID" required type="number"><input name="voter_no" placeholder="Namba ya Kura" required><input name="station" placeholder="Kituo cha Kura" required><input class="submit btn wa" type="submit" value="SAJILI SAHIHI YANGU ✅"></form>{sigs_dropdown}{visitors_dropdown}{download_btn}</div>
<div class="card"><div class="pochi-box"><h2 style="margin:0;color:#004d26">💰 CHANGIA KAMPENI YETU</h2><p>POCHI LA BIASHARA</p><h1>0796069040</h1><button class="copy-btn" onclick="copyPochi()">📋 COPY</button><a href="tel:*334%23" class="copy-btn" style="text-decoration:none;display:inline-block;background:#000">📞 LIPA *334#</a><p style="font-size:13px;background:white;padding:8px;border-radius:8px;margin-top:10px">✅ Michango: {count_michango} | 💵 Jumla: KES {total_michango}</p></div><br><a class="btn wa" href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH">JOIN WHATSAPP GROUP</a></div>
<div class="card"><h2 style="color:#004d26">💰 THIBITISHA MCHANGO</h2><form method="POST"><input type="hidden" name="form_type" value="mchango"><input name="name" placeholder="Jina lako" required><select name="amount" required><option value="">Chagua Kiasi</option><option value="100">100</option><option value="200">200</option><option value="500">500</option><option value="1000">1,000</option><option value="2000">2,000</option><option value="5000">5,000</option></select><input class="submit btn gold" type="submit" value="THIBITISHA MCHANGO ✅"></form>{michango_dropdown}</div>
<div class="card"><h2 style="color:#004d26">✍️ ANDIKA UJUMBE</h2><form method="POST"><input type="hidden" name="form_type" value="ujumbe"><input name="name" placeholder="Jina lako" required><input name="place" placeholder="Mahali (Matuu)" required><textarea name="msg" placeholder="Ujumbe wako..." rows="3" required maxlength="200"></textarea><input class="submit btn" type="submit" value="TUMA UJUMBE 🔥"></form></div>
<div class="card"><h3 style="color:#004d26">💬 UJUMBE WA WANA-YATTA ({count_msgs})</h3>{msgs_dropdown}</div>
<div class="card" style="background:#111;color:white"><h3>🔗 UNGANA NASI</h3><div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap"><a href="https://www.facebook.com/share/1A5o1f48R6/" target="_blank" style="background:#1877F2;color:white;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">Facebook</a><a href="https://www.instagram.com/daudidenismutua" target="_blank" style="background:linear-gradient(45deg,#feda75,#fa7e1e,#d62976,#962fbf,#4f5bd5);color:white;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">Instagram</a><a href="https://www.tiktok.com/@mutuawakatangi" target="_blank" style="background:#000;border:1px solid white;color:white;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">TikTok</a><a href="https://x.com/denis_mutua_d" target="_blank" style="background:white;color:black;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">Twitter</a><a href="https://wa.me/254796069040" target="_blank" style="background:#25D366;color:white;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">WhatsApp Direct</a></div><p style="margin-top:15px;font-size:12px;color:#999">© 2027 Mutua wa Katangi - INDEPENDENT | Yatta Mpya</p></div></body></html>
"""
