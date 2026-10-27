from flask import Flask, request, redirect
app = Flask(__name__)
supporters = []

@app.route('/', methods=['GET','POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET','POST'])
def home(path):
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        place = request.form.get('place','').strip()
        msg = request.form.get('msg','').strip()
        if name and msg:
            supporters.insert(0, f"{name} ({place}) - {msg}")
            if len(supporters) > 50: supporters.pop()
        return redirect('/')

    msgs_html = ""
    for s in supporters[:20]:
        msgs_html += f"<div style='background:#f0f7f0;padding:12px;border-radius:10px;margin:8px 0;text-align:left;color:#222;border-left:5px solid #004d26'>💬 <b>{s}</b></div>"
    if not supporters:
        msgs_html = "<p style='color:#999'>Hakuna ujumbe bado - Kuwa wa kwanza! 👇</p>"

    return f"""
<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MUTUA WA KATANGI - YATTA MP 2027</title>
<style>
body{{margin:0;font-family:Arial;background:#004d26;color:white;text-align:center}}
.header{{padding:20px 15px}}.card{{background:white;color:#222;padding:20px;border-radius:20px;margin:15px}}
.btn{{display:block;padding:15px;margin:10px 0;border-radius:12px;text-decoration:none;font-weight:bold;color:white}}
.wa{{background:#25D366}}.gold{{background:#FFD700;color:#000}}.fb{{background:#1877F2}}.tt{{background:#000}}.ig{{background:linear-gradient(45deg,#f09433,#dc2743)}}
.pochi{{background:gold;color:#004d26;padding:12px;border-radius:10px;font-weight:bold}}
img{{width:160px;height:160px;border-radius:50%;border:4px solid gold;object-fit:cover;background:white}}
input,textarea{{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ccc;box-sizing:border-box}}
.submit{{background:#004d26;color:white;border:none;font-weight:bold;cursor:pointer}}
</style>
</head><body>
<div class="header">
<img src="https://raw.githubusercontent.com/denismutua4/Yatta-2027/main/mutua.jpg">
<h1>🔥 MUTUA WA KATANGI 🔥</h1>
<h2 style="color:gold;margin:0">YATTA MP 2027</h2>
<p>Yatta Mpya, Maendeleo Kwa Wote</p>
</div>
<div class="card">
<h2 style="color:#004d26;margin-top:0">SITE IMEWAKA ✅</h2>
<div class="pochi">POCHI: 0796069040<br>Lipa *334# → Pochi → 0796069040</div><br>
<a class="btn wa" href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH">JOIN WHATSAPP GROUP</a>
<a class="btn gold" href="https://wa.me/254796069040?text=Niko%20tayari%20Yatta%202027">WHATSAPP DIRECT</a>
<a class="btn fb" href="https://www.facebook.com/profile.php?id=61594277768769">FACEBOOK PAGE</a>
<a class="btn tt" href="https://www.tiktok.com/@mutuawakatangi">TIKTOK</a>
<a class="btn ig" href="https://www.instagram.com/daudidenismutua">INSTAGRAM</a>
</div>
<div class="card">
<h2 style="color:#004d26">✍️ ANDIKA UJUMBE WA SUPPORT</h2>
<form method="POST">
<input name="name" placeholder="Jina lako" required>
<input name="place" placeholder="Mahali (Matuu)" required>
<textarea name="msg" placeholder="Ujumbe wako..." rows="3" required></textarea>
<input class="submit btn" type="submit" value="TUMA UJUMBE 🔥">
</form>
</div>
<div class="card">
<h3 style="color:#004d26">💬 UJUMBE WA WANA-YATTA ({len(supporters)})</h3>
{msgs_html}
</div>
<p style="padding:15px;font-size:14px">© 2027 Mutua wa Katangi<br>yatta-2027.vercel.app</p>
</body></html>
"""
