from flask import Flask, request, redirect, Response
import requests
import csv, io
from datetime import datetime

app = Flask(__name__)

SUPABASE_URL = "https://ccskbtbfbxysocrlzkou.supabase.co"
SUPABASE_KEY = "sb_publishable_ZizSNK8wSNHTBrnae5i-Mw_muX2QpIN"
TABLE = "supporters"
VISITOR_TABLE = "visitors"  # TABLE MPYA YA VISITORS
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
    """Hii ndio inahesabu kila mtu anaingia"""
    try:
        ip = req.headers.get('X-Forwarded-For', req.remote_addr)
        agent = req.headers.get('User-Agent','')[:200]
        payload = {
            "ip": str(ip)[:50],
            "place": agent,  # tunaweka phone type hapa
            "msg": f"VISIT | {req.headers.get('Referer','Direct')}"
        }
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
        return "<h1 style='text-align:center;margin-top:50px'>🔒 Hautaruhusiwi</h1>"
    supporters = get_supporters()
    sigs = [s for s in supporters if "SIG_ID" in str(s.get('msg',''))]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No", "Jina", "ID Number", "Kura Number", "Kituo"])
    for i, s in enumerate(sigs, 1):
        writer.writerow([i, s.get('name'), s.get('msg'), s.get('place')])
    return Response(output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=YATTA_SAHIHI_{len(sigs)}.csv"})

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    # LOG KILA VISITOR
    if request.method == 'GET':
        log_visitor(request)

    is_admin = request.args.get('admin') == ADMIN_PASSWORD or request.args.get('key') == ADMIN_PASSWORD
    # ... (code yako yote ya mwanzo inaendelea hapa)

    # Hii ndio sehemu mpya ya admin - ona visitors
    if is_admin:
        visitors = get_visitors()
        visitors_html = ""
        for v in visitors[:100]:
            visitors_html += f"<div style='background:#e3f2fd;padding:8px;margin:4px 0;border-radius:8px;font-size:12px;text-align:left'>👁️ {v.get('created_at','')} - IP: {v.get('ip','')} - {v.get('place','')[:60]}</div>"
    else:
        visitors = []
        visitors_html = ""

    supporters = get_supporters()
    # ... (endelea na code yako yote)
    # KWENYE RETURN HTML YAKO ONGEZA HII NDANI YA ADMIN MODE:
    # <div class="card"><h3>👁️ WALIOTEMBELEA WEBSITE ({len(visitors)})</h3>{visitors_html}</div>
