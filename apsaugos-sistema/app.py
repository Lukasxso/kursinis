from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Laikina atminties duomenų bazė incidentams demonstruoti
incidents_db = [
    {"id": 101, "object": "Vilnius, Gedimino pr. 10", "type": "Judėjimo daviklis", "time": "2026-11-10 15:10", "status": "Reaguojama"},
    {"id": 102, "object": "Kaunas, Laisvės al. 45", "type": "Gaisro pavojaus signalas", "time": "2026-11-10 14:55", "status": "Baigta"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <title>Apsaugos Tarnybos Debesų Sistema</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }
        .container { max-width: 1050px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #0d6efd; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .status { background: #d1e7dd; color: #0f5132; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #dee2e6; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #0d6efd; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 1em; }
        button:hover { background: #0b5ed7; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #bb2d3b; }
        .btn-warning { background: #ffc107; color: #000; text-decoration: none; padding: 6px 12px; border-radius: 4px; display: inline-block; font-size: 0.9em; font-weight: bold; }
        .btn-warning:hover { background: #ffca2c; }
        .btn-sm { padding: 6px 12px; font-size: 0.9em; }
        .badge-active { background: #ffc107; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold; }
        .badge-done { background: #198754; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }
        .badge-false { background: #dc3545; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }
        .form-box { background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 30px; border: 1px solid #e9ecef; }
        .actions { display: flex; gap: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Apsaugos Tarnybos Debesų Valdymo Pultas</h1>
        <div class="status">🟢 Sistema veikia debesyje (Render.com) – Pilnas incidentų valdymas (Redagavimas ir Šalinimas) aktyvus</div>
        
        <div class="form-box">
            <h3>Registruoti naują incidentą</h3>
            <form method="POST" action="/add">
                <div class="form-group">
                    <label for="object">Saugomas objektas (Adresas / Pavadinimas):</label>
                    <input type="text" id="object" name="object" required placeholder="pvz., Klaipėda, Taikos pr. 20">
                </div>
                <div class="form-group">
                    <label for="type">Problemos tipas:</label>
                    <select id="type" name="type">
                        <option value="Judėjimo daviklis">Judėjimo daviklis</option>
                        <option value="Gaisro pavojaus signalas">Gaisro pavojaus signalas</option>
                        <option value="Įsilaužimas / Lango dūžis">Įsilaužimas / Lango dūžis</option>
                        <option value="Techninis gedimas">Techninis gedimas</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="status">Būsena:</label>
                    <select id="status" name="status">
                        <option value="Reaguojama">Reaguojama</option>
                        <option value="Baigta">Baigta</option>
                        <option value="Klaidingas signalas">Klaidingas signalas</option>
                        <option value="Nepatvirtintas">Nepatvirtintas</option>
                    </select>
                </div>
                <button type="submit">Įregistruoti ir išsaugoti debesyje</button>
            </form>
        </div>

        <h3>Aktyvūs incidentai (Incidentų žurnalas)</h3>
        <table>
            <tr><th>ID</th><th>Saugomas objektas</th><th>Pavojaus tipas</th><th>Laikas</th><th>Būsena</th><th>Veiksmai</th></tr>
            {% for inc in incidents %}
            <tr>
                <td>#{{ inc.id }}</td>
                <td>{{ inc.object }}</td>
                <td>{{ inc.type }}</td>
                <td>{{ inc.time }}</td>
                <td>
                    {% if inc.status == 'Reaguojama' %}
                        <span class="badge-active">{{ inc.status }}</span>
                    {% elif inc.status == 'Baigta' %}
                        <span class="badge-done">{{ inc.status }}</span>
                    {% else %}
                        <span class="badge-false">{{ inc.status }}</span>
                    {% endif %}
                </td>
                <td>
                    <div class="actions">
                        <a href="/edit/{{ inc.id }}" class="btn-warning">Redaguoti</a>
                        <form action="/delete/{{ inc.id }}" method="POST" style="display:inline;" onsubmit="return confirm('Ar tikrai norite ištrinti šį incidentą?');">
                            <button type="submit" class="btn-danger btn-sm">Ištrinti</button>
                        </form>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <title>Redaguoti Incidentą #{{ incident.id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #0d6efd; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #ffc107; color: #000; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 1em; font-weight: bold; }
        button:hover { background: #ffca2c; }
        .btn-secondary { background: #6c757d; color: white; text-decoration: none; padding: 10px 20px; border-radius: 4px; display: inline-block; margin-left: 10px; }
        .btn-secondary:hover { background: #5c636a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Redaguoti Incidentą #{{ incident.id }}</h1>
        <form method="POST">
            <div class="form-group">
                <label for="object">Saugomas objektas (Adresas / Pavadinimas):</label>
                <input type="text" id="object" name="object" value="{{ incident.object }}" required>
            </div>
            <div class="form-group">
                <label for="type">Problemos tipas:</label>
                <select id="type" name="type">
                    <option value="Judėjimo daviklis" {% if incident.type == 'Judėjimo daviklis' %}selected{% endif %}>Judėjimo daviklis</option>
                    <option value="Gaisro pavojaus signalas" {% if incident.type == 'Gaisro pavojaus signalas' %}selected{% endif %}>Gaisro pavojaus signalas</option>
                    <option value="Įsilaužimas / Lango dūžis" {% if incident.type == 'Įsilaužimas / Lango dūžis' %}selected{% endif %}>Įsilaužimas / Lango dūžis</option>
                    <option value="Techninis gedimas" {% if incident.type == 'Techninis gedimas' %}selected{% endif %}>Techninis gedimas</option>
                </select>
            </div>
            <div class="form-group">
                <label for="status">Būsena:</label>
                <select id="status" name="status">
                    <option value="Reaguojama" {% if incident.status == 'Reaguojama' %}selected{% endif %}>Reaguojama</option>
                    <option value="Baigta" {% if incident.status == 'Baigta' %}selected{% endif %}>Baigta</option>
                    <option value="Klaidingas signalas" {% if incident.status == 'Klaidingas signalas' %}selected{% endif %}>Klaidingas signalas</option>
                    <option value="Nepatvirtintas" {% if incident.status == 'Nepatvirtintas' %}selected{% endif %}>Nepatvirtintas</option>
                </select>
            </div>
            <button type="submit">Išsaugoti pakeitimus</button>
            <a href="/" class="btn-secondary">Atšaukti</a>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, incidents=incidents_db)

@app.route('/add', methods=['POST'])
def add_incident():
    new_id = max([inc["id"] for inc in incidents_db]) + 1 if incidents_db else 101
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    object_name = request.form.get('object')
    problem_type = request.form.get('type')
    status = request.form.get('status')
    
    incidents_db.insert(0, {
        "id": new_id,
        "object": object_name,
        "type": problem_type,
        "time": current_time,
        "status": status
    })
    
    return redirect(url_for('home'))

@app.route('/edit/<int:incident_id>', methods=['GET', 'POST'])
def edit_incident(incident_id):
    incident = next((inc for inc in incidents_db if inc["id"] == incident_id), None)
    if not incident:
        return "Incidentas nerastas", 404
        
    if request.method == 'POST':
        incident["object"] = request.form.get('object')
        incident["type"] = request.form.get('type')
        incident["status"] = request.form.get('status')
        return redirect(url_for('home'))
        
    return render_template_string(EDIT_TEMPLATE, incident=incident)

@app.route('/delete/<int:incident_id>', methods=['POST'])
def delete_incident(incident_id):
    global incidents_db
    incidents_db = [inc for inc in incidents_db if inc["id"] != incident_id]
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)