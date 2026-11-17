"""Page web de l'orchestrateur (http://localhost:8080).

À gauche : messages et questions pour l'humain, avec les boutons Valider / Refuser.
À droite : les dernières lignes du journal d'actions de tous les agents."""
from __future__ import annotations

from flask import Flask, redirect, render_template_string, request

from common.events import Event, EventType

PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="10">
<title>Orchestrateur MLOps</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 24px; background: #f6f7f9; color: #1f2328; }
  h1 { font-size: 22px; margin: 0 0 16px; }
  h2 { font-size: 16px; margin: 0 0 8px; }
  .cols { display: grid; grid-template-columns: 3fr 2fr; gap: 24px; }
  .card { background: #fff; border: 1px solid #d0d7de; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }
  .question { border-left: 4px solid #bf8700; }
  .approved { border-left: 4px solid #1a7f37; }
  .refused { border-left: 4px solid #cf222e; }
  .time { color: #656d76; font-size: 12px; }
  button { padding: 6px 14px; border-radius: 6px; border: 1px solid #d0d7de; cursor: pointer; margin-right: 6px; }
  .yes { background: #1a7f37; color: #fff; }
  .no { background: #cf222e; color: #fff; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; background: #fff; }
  td, th { border-bottom: 1px solid #d0d7de; padding: 4px 6px; text-align: left; vertical-align: top; }
  @media (max-width: 800px) { .cols { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<h1>Orchestrateur MLOps</h1>
<p>Ton prénom (pour signer les validations) : <input id="who" placeholder="ismail"></p>
<div class="cols">
  <div>
    <h2>Messages</h2>
    {% for n in notifications %}
      <div class="card {{ 'question' if n.status == 'pending' else (n.status or '') }}">
        <div class="time">{{ n.timestamp.strftime('%d/%m %H:%M:%S') }}</div>
        <div>{{ n.text }}</div>
        {% if n.status == 'pending' %}
          <form method="post" action="/answer" onsubmit="this.who.value = document.getElementById('who').value">
            <input type="hidden" name="request_id" value="{{ n.request_id }}">
            <input type="hidden" name="who">
            <button class="yes" name="choice" value="yes">Valider</button>
            <button class="no" name="choice" value="no">Refuser</button>
          </form>
        {% elif n.status %}
          <div class="time">{{ 'Validé' if n.status == 'approved' else 'Refusé' }} par {{ n.answered_by }}</div>
        {% endif %}
      </div>
    {% else %}
      <p>Aucun message pour l'instant.</p>
    {% endfor %}
  </div>
  <div>
    <h2>Journal d'actions</h2>
    <table>
      <tr><th>Heure</th><th>Agent</th><th>Action</th></tr>
      {% for a in actions %}
        <tr><td>{{ a.timestamp.strftime('%H:%M:%S') }}</td><td>{{ a.agent }}</td><td>{{ a.action }}</td></tr>
      {% endfor %}
    </table>
  </div>
</div>
<script>
  const who = document.getElementById("who");
  try { who.value = localStorage.getItem("who") || ""; } catch (e) {}
  who.addEventListener("input", () => { try { localStorage.setItem("who", who.value); } catch (e) {} });
</script>
</body>
</html>"""


def create_app(notifier, bus, log) -> Flask:
    app = Flask("orchestrator-web")

    @app.get("/")
    def index():
        return render_template_string(PAGE, notifications=notifier.latest(), actions=log.latest(20))

    @app.post("/answer")
    def answer():
        request_id = request.form["request_id"]
        approved = request.form.get("choice") == "yes"
        who = request.form.get("who") or "équipe"
        if notifier.answer(request_id, approved, who):  # False si quelqu'un a déjà répondu
            bus.publish(Event(type=EventType.APPROVAL_GIVEN, source="page_web", payload={
                "request_id": request_id, "approved": approved, "approved_by": who}))
        return redirect("/")

    return app