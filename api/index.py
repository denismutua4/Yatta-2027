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
    "Content-Type": "application/json"
}

def get_supporters():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=*&order=created_at.desc&limit=2000", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except: pass
    return []

def get_visitors():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}?select=*&order=created_at.desc&limit=500", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
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

def delete_supporter(sid):
    try:
        requests.delete(f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{sid}", headers=HEADERS, timeout=10)
    except: pass

@app.route('/download')
def download():
    key = request.args.get('key')
    if key != ADMIN_PASSWORD:
        return "<h1 style='text-align:center;margin-top:50px'>Hautaruhusiwi</h1>"
    supporters = get_supporters()
    sigs = [s for s in supporters if "SIG_ID" in str(s.get('msg',''))]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No", "Jina", "ID Number", "Kura Number", "Kituo"])
    for i, s in enumerate(sigs, 1):
        writer.writerow([i, s.get('name'), s.get('msg'), s.get('place')])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename=YATTA_SAHIHI_{len(sigs)}.csv"})

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    if request.method == 'GET' and 'favicon' not in path:
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
            if name and amount:
                add_supporter(name, f"MCHANGO {amount}", f"MCHANGO KES {amount}")
        elif form_type == 'sig':
            id_no = request.form.get('id_no','').strip()
            voter_no = request.form.get('voter_no','').strip()
            station = request.form.get('station','').strip()
            if name and id_no and voter_no:
                add_supporter(name, station, f"SIG_ID:{id_no} | KURA:{voter_no} | KITUO:{station} | SIG")
        else:
            if len(msg) > 200: msg = msg[:200]
            if name and msg:
                add_supporter(name, place, msg)
        return redirect('/')

    supporters = get_supporters()
    all_visitors = get_visitors()
    total_views = len(all_visitors)
    visitors = all_visitors if is_admin else []
    
    michango_html = ""; msgs_html = ""; sigs_html = ""; visitors_html = ""
    total_michango = 0; count_michango = 0; count_msgs = 0; count_sigs = 0
    
    for v in visitors[:100]:
        visitors_html += f"<div style='background:#e3f2fd;padding:8px;margin:4px 0;border-radius:8px;font-size:11px;text-align:left'> {str(v.get('created_at',''))[:19]} | IP: {v.get('place','')} | {v.get('msg','')[:80]}</div>"
    if not visitors_html and is_admin:
        visitors_html = "<p style='color:#999'>Hakuna visitors bado</p>"

    for s in supporters:
        if "SIG_ID" in str(s.get('msg','')):
            count_sigs += 1
            if is_admin:
                sid = s.get('id')
                sigs_html += f"<div style='background:#e8f5e9;padding:10px;border-radius:10px;margin:6px 0;text-align:left;color:#222;border-left:5px solid #25D366;'><b>{s.get('name')} - {s.get('msg')} - {s.get('place')}</b></div>"
            continue
        safe_msg = f"{s.get('name','')} ({s.get('place','')}) - {s.get('msg','')}"
        is_mchango = "MCHANGO" in str(s.get('place','')).upper() or "MCHANGO" in str(s.get('msg','')).upper()
        if is_mchango:
            count_michango += 1
            try:
                amt_str = ''.join(filter(str.isdigit, s.get('place','')))
                if amt_str: total_michango += int(amt_str)
            except: pass
            michango_html += f"<div style='background:#fff8dc;padding:10px;border-radius:10px;margin:6px 0;text-align:left;color:#222;border-left:5px solid gold;'><b>{safe_msg}</b></div>"
        else:
            count_msgs += 1
            if count_msgs <= 100:
                msgs_html += f"<div style='background:#f0f7f0;padding:12px;border-radius:10px;margin:8px 0;text-align:left;color:#222;border-left:5px solid #004d26;'><b>{safe_msg}</b></div>"
    
    if not msgs_html: msgs_html = "<p style='color:#999'>Hakuna ujumbe bado</p>"
    if not michango_html: michango_html = "<p style='color:#999'>Hakuna mchango bado</p>"
    if not sigs_html: sigs_html = "<p style='color:#999'>Hakuna sahihi bado</p>" if is_admin else ""

    michango_dropdown = f"<div style='margin-top:15px'><button style='background:#FFD700;color:#000;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;'>WALIOTUMA ({count_michango})</button><div style='max-height:350px; overflow-y:auto; border:2px solid gold; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{michango_html}</div></div>"
    msgs_dropdown = f"<div style='margin-top:10px'><button style='background:#004d26;color:white;border:none;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;'>UJUMBE WOTE ({count_msgs})</button><div style='max-height:350px; overflow-y:auto; border:2px solid #004d26; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{msgs_html}</div></div>"
    
    if is_admin:
        sigs_dropdown = f"<div style='margin-top:10px'><div style='background:#25D366;color:white;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;'>SAHIHI ZOTE ({count_sigs}) - ADMIN</div><div style='max-height:500px; overflow-y:auto; border:2px solid #25D366; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{sigs_html}</div></div>"
        download_btn = f"<a href='/download?key={ADMIN_PASSWORD}' style='display:block;margin-top:15px;background:#000;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold'>DOWNLOAD LIST YA IEBC - {count_sigs} sahihi</a>"
        visitors_dropdown = f"<div style='margin-top:15px'><div style='background:#2196F3;color:white;padding:12px 15px;border-radius:10px;font-weight:bold;width:100%;'>WALIOTEMBELEA WEBSITE ({total_views}) - VIEWS</div><div style='max-height:400px; overflow-y:auto; border:2px solid #2196F3; border-radius:12px; margin-top:10px; padding:10px; background:#fff;'>{visitors_html}</div></div>"
    else:
        sigs_dropdown = "<p style='font-size:12px;color:#666;background:#e8f5e9;padding:10px;border-radius:8px'><b>Data yako ni siri</b></p>"
        download_btn = "<a href='#' style='display:block;margin-top:15px;background:#444;color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold'>DOWNLOAD - Admin Tu</a>"
        visitors_dropdown = ""

    admin_banner = f"<p style='background:red;padding:10px;border-radius:10px'>ADMIN MODE</p>" if is_admin else ""

    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MUTUA WA KATANGI - YATTA MP 2027</title>
<style>
body{{margin:0;font-family:Arial;background:#004d26;color:white;text-align:center}}
.header{{padding:20px 15px}}.card{{background:white;color:#222;padding:20px;border-radius:20px;margin:15px}}
.btn{{display:block;padding:14px;margin:8px 0;border-radius:12px;text-decoration:none;font-weight:bold;color:white;cursor:pointer;border:none;width:100%;box-sizing:border-box}}
.wa{{background:#25D366}}.gold{{background:#FFD700;color:#000}}
.pochi-box{{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;padding:20px;border-radius:15px;font-weight:bold;border:3px solid #004d26}}
.copy-btn{{background:#004d26;color:white;padding:10px 15px;border-radius:8px;border:none;font-weight:bold;cursor:pointer;margin:5px}}
img{{width:160px;height:160px;border-radius:50%;border:4px solid gold;object-fit:cover;background:white}}
input,textarea,select{{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}}
.submit{{background:#004d26;color:white;border:none;font-weight:bold;cursor:pointer}}
</style>
</head><body>
<div class="header"><img src="https://raw.githubusercontent.com/denismutua4/Yatta-2027/main/mutua.jpg">
<h1>MUTUA WA KATANGI</h1><h2 style="color:gold;margin:0">YATTA MP 2027 - INDEPENDENT</h2>
{admin_banner}</div>
<div class="card" style="border:3px solid #25D366;background:#f0fff0">
<h2 style="color:#004d26;margin:0">SAJILI SAHIHI YA IEBC</h2>
<p style="font-size:14px;background:#004d26;color:white;padding:10px;border-radius:10px">Sahihi: <b>{count_sigs} / 1000</b> | Views: <b>{total_views}</b></p>
<form method="POST">
<input type="hidden" name="form_type" value="sig">
<input name="name" placeholder="Jina kamili kama ID" required>
<input name="id_no" placeholder="Namba ya ID" required type="number">
<input name="voter_no" placeholder="Namba ya Kura" required>
<input name="station" placeholder="Kituo cha Kura" required>
<input class="submit btn wa" type="submit" value="SAJILI SAHIHI YANGU">
</form>
{sigs_dropdown}
{visitors_dropdown}
{download_btn}
</div>
</body></html>
"""
