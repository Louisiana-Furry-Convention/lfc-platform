from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["scanner"])


SCANNER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>LFC Check-In Scanner</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 700px;
      margin: 40px auto;
      padding: 20px;
    }
    input, button, textarea {
      width: 100%;
      padding: 12px;
      margin-top: 10px;
      box-sizing: border-box;
    }
    .ok { color: green; }
    .err { color: red; }
    .box {
      border: 1px solid #ccc;
      border-radius: 10px;
      padding: 16px;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <h1>LFC Check-In Scanner</h1>
  <p>Paste or scan a QR token below.</p>

  <div class="box">
    <label for="token">QR Token</label>
    <textarea id="token" rows="4" placeholder="Paste QR token here"></textarea>

    <label for="jwt">Staff/Admin Bearer Token</label>
    <textarea id="jwt" rows="3" placeholder="Paste staff JWT here"></textarea>

    <button onclick="submitCheckin()">Submit Check-In</button>
  </div>

  <div class="box">
    <h3>Result</h3>
    <pre id="result">No scan yet.</pre>
  </div>

  <script>
    async function submitCheckin() {
      const token = document.getElementById("token").value.trim();
      const jwt = document.getElementById("jwt").value.trim();
      const result = document.getElementById("result");

      if (!token || !jwt) {
        result.textContent = "QR token and JWT are required.";
        result.className = "err";
        return;
      }

      try {
        const res = await fetch("/checkin", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + jwt
          },
          body: JSON.stringify({ qr_token: token })
        });

        const data = await res.json();
        result.textContent = JSON.stringify(data, null, 2);
        result.className = res.ok ? "ok" : "err";
      } catch (err) {
        result.textContent = "Request failed: " + err;
        result.className = "err";
      }
    }
  </script>
</body>
</html>
"""


@router.get("/scan", response_class=HTMLResponse)
def scan_page():
    return SCANNER_HTML

