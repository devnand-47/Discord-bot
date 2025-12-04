# dashboard.py

import sqlite3
from pathlib import Path
from time import localtime, strftime
import json

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature

from config import (
    DB_PATH,
    GUILD_ID,
    DASHBOARD_USERNAME,
    DASHBOARD_PASSWORD,
    DASHBOARD_SECRET_KEY,
)

app = FastAPI(title="UltimateBot Dashboard")

DB_FILE = Path(DB_PATH)
serializer = URLSafeTimedSerializer(DASHBOARD_SECRET_KEY)
SESSION_COOKIE_NAME = "ub_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


# ---------- DB helpers ----------

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Auth helpers ----------

def get_logged_in_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    try:
        username = serializer.loads(token, max_age=SESSION_MAX_AGE)
        return username
    except BadSignature:
        return None


def require_login(request: Request):
    user = get_logged_in_user(request)
    if not user:
        return None
    return user


# ---------- Stats helpers ----------

def get_logs_text(limit: int) -> str:
    if not DB_FILE.exists():
        return "No database yet."

    conn = get_db()
    cur = conn.execute(
        """
        SELECT user_id, actor_id, action, reason, created_at
        FROM moderation_logs
        WHERE guild_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (GUILD_ID, limit),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No moderation logs yet."

    lines = []
    for r in rows:
        ts_str = strftime("%Y-%m-%d %H:%M", localtime(r["created_at"]))
        user_txt = r["user_id"] or "-"
        reason_txt = r["reason"] or "-"
        lines.append(
            f"[{ts_str}] action={r['action']}, target={user_txt}, by={r['actor_id']}, reason={reason_txt}"
        )
    return "\n".join(lines)


def get_stats():
    """Return stats for graphs: labels (dates) + series per action."""
    if not DB_FILE.exists():
        return {"labels": [], "series": []}

    conn = get_db()
    cur = conn.execute(
        """
        SELECT
          date(datetime(created_at, 'unixepoch')) AS d,
          action,
          COUNT(*) as c
        FROM moderation_logs
        WHERE guild_id = ?
        GROUP BY d, action
        ORDER BY d ASC
        """,
        (GUILD_ID,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {"labels": [], "series": []}

    dates = sorted({r["d"] for r in rows})
    actions = sorted({r["action"] for r in rows})

    date_index = {d: i for i, d in enumerate(dates)}
    data_map = {action: [0] * len(dates) for action in actions}

    for r in rows:
        d = r["d"]
        a = r["action"]
        c = r["c"]
        idx = date_index[d]
        data_map[a][idx] = c

    series = []
    for action, counts in data_map.items():
        series.append(
            {
                "name": action,
                "type": "line",
                "smooth": True,
                "data": counts,
            }
        )

    return {"labels": dates, "series": series}


# ---------- Routes: auth ----------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_logged_in_user(request)
    if user:
        return RedirectResponse("/", status_code=303)

    html = """
    <html>
    <head>
        <title>UltimateBot Login</title>
        <style>
            body {
                font-family: system-ui, sans-serif;
                background: #050812;
                color: #f5f5f5;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background: #0b1020;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 0 15px rgba(0, 224, 255, 0.25);
                width: 320px;
            }
            h1 {
                color: #00e0ff;
                text-align: center;
            }
            label {
                display: block;
                margin-top: 12px;
            }
            input {
                width: 100%;
                padding: 8px;
                margin-top: 4px;
                border-radius: 6px;
                border: 1px solid #222a3f;
                background: #050812;
                color: #f5f5f5;
            }
            button {
                margin-top: 16px;
                width: 100%;
                padding: 8px;
                border-radius: 6px;
                border: none;
                background: #00e0ff;
                color: #050812;
                font-weight: 600;
                cursor: pointer;
            }
            button:hover {
                background: #10f0ff;
            }
            .error {
                color: #ff6b6b;
                margin-top: 8px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>UltimateBot</h1>
            <form method="post" action="/login">
                <label>Username
                    <input name="username" autocomplete="username">
                </label>
                <label>Password
                    <input name="password" type="password" autocomplete="current-password">
                </label>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/login")
def do_login(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
):
    if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
        token = serializer.dumps(username)
        resp = RedirectResponse("/", status_code=303)
        resp.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
        return resp

    html = """
    <html>
    <head>
        <title>UltimateBot Login</title>
        <style>
            body {
                font-family: system-ui, sans-serif;
                background: #050812;
                color: #f5f5f5;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background: #0b1020;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 0 15px rgba(0, 224, 255, 0.25);
                width: 320px;
            }
            h1 {
                color: #00e0ff;
                text-align: center;
            }
            label {
                display: block;
                margin-top: 12px;
            }
            input {
                width: 100%;
                padding: 8px;
                margin-top: 4px;
                border-radius: 6px;
                border: 1px solid #222a3f;
                background: #050812;
                color: #f5f5f5;
            }
            button {
                margin-top: 16px;
                width: 100%;
                padding: 8px;
                border-radius: 6px;
                border: none;
                background: #00e0ff;
                color: #050812;
                font-weight: 600;
                cursor: pointer;
            }
            button:hover {
                background: #10f0ff;
            }
            .error {
                color: #ff6b6b;
                margin-top: 8px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>UltimateBot</h1>
            <form method="post" action="/login">
                <label>Username
                    <input name="username" autocomplete="username">
                </label>
                <label>Password
                    <input name="password" type="password" autocomplete="current-password">
                </label>
                <button type="submit">Login</button>
                <div class="error">Invalid credentials</div>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(SESSION_COOKIE_NAME)
    return resp


# ---------- Main dashboard ----------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = require_login(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    conn = get_db()
    cur = conn.execute(
        """
        SELECT welcome_channel_id, welcome_message, autorole_id, default_announce_id
        FROM guild_settings WHERE guild_id = ?
        """,
        (GUILD_ID,),
    )
    row = cur.fetchone()
    conn.close()

    welcome_channel_id = row["welcome_channel_id"] if row else ""
    welcome_message = (
        row["welcome_message"]
        if row and row["welcome_message"]
        else "{mention}, welcome to {server}."
    )
    autorole_id = row["autorole_id"] if row else ""
    default_announce_id = row["default_announce_id"] if row else ""

    logs_text = get_logs_text(20)
    stats = get_stats()
    stats_json = json.dumps(stats)

    html = f"""
    <html>
    <head>
        <title>UltimateBot Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
        <style>
            body {{
                font-family: system-ui, sans-serif;
                background: #050812;
                color: #f5f5f5;
                padding: 20px;
            }}
            h1 {{
                color: #00e0ff;
            }}
            .top-bar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }}
            .card {{
                background: #0b1020;
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(0, 224, 255, 0.2);
            }}
            label {{
                display: block;
                margin-top: 8px;
            }}
            input, textarea {{
                width: 100%;
                padding: 8px;
                margin-top: 4px;
                border-radius: 6px;
                border: 1px solid #222a3f;
                background: #050812;
                color: #f5f5f5;
            }}
            button {{
                margin-top: 12px;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                background: #00e0ff;
                color: #050812;
                font-weight: 600;
                cursor: pointer;
            }}
            button:hover {{
                background: #10f0ff;
            }}
            pre {{
                background: #050812;
                border-radius: 8px;
                padding: 12px;
                overflow-x: auto;
            }}
            a.logout {{
                color: #ff6b6b;
                text-decoration: none;
                font-weight: 600;
            }}
            #modChart {{
                width: 100%;
                height: 380px;
            }}
        </style>
    </head>
    <body>
        <div class="top-bar">
            <h1>UltimateBot Dashboard</h1>
            <div>
                Logged in as <strong>{user}</strong>
                &nbsp;|&nbsp;
                <a href="/logout" class="logout">Logout</a>
            </div>
        </div>

        <div class="card">
            <h2>Welcome Settings</h2>
            <form method="post" action="/settings/welcome">
                <label>Welcome Channel ID
                    <input name="welcome_channel_id" value="{welcome_channel_id}">
                </label>
                <label>Welcome Message (use {{mention}} and {{server}})
                    <textarea name="welcome_message" rows="4">{welcome_message}</textarea>
                </label>
                <label>Autorole ID
                    <input name="autorole_id" value="{autorole_id}">
                </label>
                <button type="submit">Save Welcome Settings</button>
            </form>
        </div>

        <div class="card">
            <h2>Announcement Settings</h2>
            <form method="post" action="/settings/announce">
                <label>Default Announcement Channel ID
                    <input name="default_announce_id" value="{default_announce_id}">
                </label>
                <button type="submit">Save Announcement Settings</button>
            </form>
        </div>

        <div class="card">
            <h2>Moderation Activity (per day)</h2>
            <div id="modChart"></div>
        </div>

        <div class="card">
            <h2>Moderation Logs (Last 20)</h2>
            <pre>{logs_text}</pre>
        </div>

        <script>
            const stats = {stats_json};

            if (stats.labels.length > 0) {{
                const chartDom = document.getElementById('modChart');
                const myChart = echarts.init(chartDom);
                const option = {{
                    backgroundColor: '#0b1020',
                    tooltip: {{
                        trigger: 'axis'
                    }},
                    legend: {{
                        data: stats.series.map(s => s.name),
                        textStyle: {{ color: '#f5f5f5' }}
                    }},
                    grid: {{
                        left: '3%',
                        right: '3%',
                        bottom: '5%',
                        containLabel: true
                    }},
                    xAxis: {{
                        type: 'category',
                        boundaryGap: false,
                        data: stats.labels,
                        axisLine: {{ lineStyle: {{ color: '#888' }} }},
                    }},
                    yAxis: {{
                        type: 'value',
                        minInterval: 1,
                        axisLine: {{ lineStyle: {{ color: '#888' }} }},
                        splitLine: {{ lineStyle: {{ color: '#222a3f' }} }}
                    }},
                    series: stats.series
                }};
                myChart.setOption(option);
                window.addEventListener('resize', () => myChart.resize());
            }} else {{
                document.getElementById('modChart').innerHTML = "<p>No moderation data yet.</p>";
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ---------- Settings update routes (protected) ----------

@app.post("/settings/welcome")
def save_welcome(
    request: Request,
    welcome_channel_id: str = Form(""),
    welcome_message: str = Form(""),
    autorole_id: str = Form(""),
):
    user = require_login(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    conn = get_db()
    conn.execute(
        """
        INSERT INTO guild_settings (guild_id, welcome_channel_id, welcome_message, autorole_id, default_announce_id)
        VALUES (?, ?, ?, ?, COALESCE((SELECT default_announce_id FROM guild_settings WHERE guild_id = ?), NULL))
        ON CONFLICT(guild_id) DO UPDATE SET
            welcome_channel_id = excluded.welcome_channel_id,
            welcome_message    = excluded.welcome_message,
            autorole_id        = excluded.autorole_id
        """,
        (
            GUILD_ID,
            int(welcome_channel_id) if welcome_channel_id else None,
            welcome_message,
            int(autorole_id) if autorole_id else None,
            GUILD_ID,
        ),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)


@app.post("/settings/announce")
def save_announce(
    request: Request,
    default_announce_id: str = Form(""),
):
    user = require_login(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    conn = get_db()
    conn.execute(
        """
        INSERT INTO guild_settings (guild_id, welcome_channel_id, welcome_message, autorole_id, default_announce_id)
        VALUES (
            ?,
            (SELECT welcome_channel_id FROM guild_settings WHERE guild_id = ?),
            (SELECT welcome_message FROM guild_settings WHERE guild_id = ?),
            (SELECT autorole_id FROM guild_settings WHERE guild_id = ?),
            ?
        )
        ON CONFLICT(guild_id) DO UPDATE SET
            default_announce_id = excluded.default_announce_id
        """,
        (
            GUILD_ID,
            GUILD_ID,
            GUILD_ID,
            GUILD_ID,
            int(default_announce_id) if default_announce_id else None,
        ),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)
