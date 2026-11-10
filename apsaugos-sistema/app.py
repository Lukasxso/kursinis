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
        .container { max-width: 950px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
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
        .badge-active { background: #ffc107; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold; }
        .badge-done { background: #198754; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }
        .form-box { background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 30px; border: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Apsaugos Tarnybos Debesų Valdymo Pultas</h1>
        <div class="status">🟢 Sistema veikia debesyje (Render.com) – Automatinis laiko ir ID generavimas aktyvus</div>
        
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
                        <option value="Nepatvirtintas">Nepatvirtintas</option>
                    </select>
                </div>
                <button type="submit">Įregistruoti ir išsaugoti debesyje</button>
            </form>
        </div>

        <h3>Aktyvūs incidentai (Incidentų žurnalas)</h3>
        <table>
            <tr><th>ID</th><th>Saugomas objektas</th><th>Pavojaus tipas</th><th>Laikas (Automatinis)</th><th>Būsena</th></tr>
            {% for inc in incidents %}
            <tr>
                <td>#{{ inc.id }}</td>
                <td>{{ inc.object }}</td>
                <td>{{ inc.type }}</td>
                <td>{{ inc.time }}</td>
                <td>
                    {% if inc.status == 'Reaguojama' %}
                        <span class="badge-active">{{ inc.status }}</span>
                    {% else %}
                        <span class="badge-done">{{ inc.status }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, incidents=incidents_db)

@app.route('/add', methods=['POST'])
def add_incident():
    # Kodas pats pasirūpina ID generavimu, dabartinio laiko nustatymu ir teksto tvarkymu
    new_id = incidents_db[-1]["id"] + 1 if incidents_db else 101
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    object_name = request.form.get('object')
    problem_type = request.form.get('type')
    status = request.form.get('status')
    
    # Pridðjimas į sąrašą
    incidents_db.insert(0, {
        "id": new_id,
        "object": object_name,
        "type": problem_type,
        "time": current_time,
        "status": status
    })
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)