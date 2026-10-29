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
        if r.status_code == 200: return r.json()
    except: pass
    return []

def get_visitors():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{VISITOR_TABLE}?select=*&order=created_at.desc&limit=500", headers=HEADERS, timeout=10)
        if r.status_code == 200: return r.json()
    except: pass
    return []

# ... (functions zote kama zako)

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    # ... code yako yote ...
    supporters = get_supporters()
    all_visitors = get_visitors() # <--- HAPA NDIPO FIX
    visitors = all_visitors if is_admin else [] # list kwa admin
    total_views = len(all_visitors) # count kwa kila mtu!

    # kisha mahali unaonyesha Views: badilisha len(visitors) na total_views
