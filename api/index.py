from flask import Flask
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return """
<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MUTUA WA KATANGI - YATTA MP 2027</title>
<style>
body{margin:0;font-family:Arial;background:#004d26;color:white;text-align:center}
.header{padding:25px 15px}
.card{background:white;color:#222;padding:22px;border-radius:20px;margin:15px}
.btn{display:block;padding:16px;margin:11px 0;border-radius:13px;text-decoration:none;font-weight:bold;color:white;font-size:17px}
.wa{background:#25D366}.gold{background:#FFD700;color:black}.fb{background:#1877F2}.tt{background:#000}.ig{background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366)}
.pochi{background:gold;color:#004d26;padding:12px;border-radius:10px;font-weight:bold;font-size:18px}
img{width:160px;height:160px;border-radius:50%;border:4px solid gold;object-fit:cover}
</style>
</head><body>
<div class="header">
<img src="/mutua.jpg" onerror="this.style.display='none'">
<h1>🔥 MUTUA WA KATANGI 🔥</h1>
<h2 style="color:gold;margin:0">YATTA MP 2027</h2>
<p>Yatta Mpya, Maendeleo Kwa Wote</p>
</div>
<div class="card">
<h2 style="color:#004d26">SITE IMEWAKA ✅</h2>
<div class="pochi">POCHI LA BIASHARA: 0796069040<br>Lipa *334# → Pochi → 0796069040</div>
<br>
<a class="btn wa" href="https://chat.whatsapp.com/JiuIABnB9gA7iSwlNslTBH">JOIN WHATSAPP GROUP</a>
<a class="btn gold" href="https://wa.me/254796069040?text=Niko%20tayari%20Yatta%202027">WHATSAPP DIRECT - 0796069040</a>
<a class="btn fb" href="https://www.facebook.com/profile.php?id=61594277768769">FACEBOOK PAGE</a>
<a class="btn tt" href="https://www.tiktok.com/@mutuawakatangi">TIKTOK @mutuawakatangi</a>
<a class="btn ig" href="https://www.instagram.com/daudidenismutua">INSTAGRAM @daudidenismutua</a>
</div>
<p style="padding:15px">© 2027 Mutua wa Katangi Campaign<br>Yatta Constituency</p>
</body></html>
"""
