import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

# Konfigūruojama duomenų bazės nuoroda (Render PostgreSQL arba vietinė SQLite)
db_url = os.environ.get('DATABASE_URL')
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///security.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Duomenų bazės modelis pagal baigiamojo darbo architektūrą
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)

# Sukuriamos lentelės ir pradiniai duomenys (jei bazė tuščia)
with app.app_context():
    db.create_all()
    if not Incident.query.first():
        vilnius_tz = ZoneInfo("Europe/Vilnius")
        initial_time = datetime.now(vilnius_tz).strftime('%Y-%m-%d %H:%M')
        db.session.add(Incident(object="Vilnius, Gedimino pr. 10", type="Judėjimo daviklis", team="Ekipažas Nr. 2", time=initial_time, status="Reaguojama"))
        db.session.add(Incident(object="Kaunas, Laisvės al. 45", type="Gaisro pavojaus signalas", team="Nepaskirtas", time=initial_time, status="Baigta"))
        db.session.commit()

# Vartotojo sąsajos HTML šablonas
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <title>Apsaugos Tarnybos Incidentų Valdymo Sistema</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f7f6; color: #333; }
        h1, h2 { color: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #0056b3; color: white; }
        form { background: white; padding: 20px; margin-top: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 600px; }
        input, select { width: 100%; padding: 8px; margin: 8px 0 16px 0; display: inline-block; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button, .btn { background-color: #0056b3; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        button:hover, .btn:hover { background-color: #004085; }
        .btn-danger { background-color: #dc3545; }
        .btn-danger:hover { background-color: #c82333; }
        .actions { display: flex; gap: 5px; }
    </style>
</head>
<body>
    <h1>Apsaugos Tarnybos Incidentų Valdymas</h1>
    
    <h2>Registruoti naują incidentą</h2>
    <form action="/add" method="POST">
        <label for="object">Apsaugomas objektas / adresas:</label>
        <input type="text" id="object" name="object" required placeholder="pvz., Vilnius, Gedimino pr. 10">

        <label for="type">Problemos tipas:</label>
        <select id="type" name="type" required>
            <option value="Judėjimo daviklis">Judėjimo daviklis</option>
            <option value="Gaisro pavojaus signalas">Gaisro pavojaus signalas</option>
            <option value="Įsilaužimo signalizacija">Įsilaužimo signalizacija</option>
            <option value="Pagalbos mygtukas">Pagalbos mygtukas</option>
        </select>

        <label for="team">Reagavimo ekipažas:</label>
        <select id="team" name="team" required>
            <option value="Nepaskirtas">Nepaskirtas</option>
            <option value="Ekipažas Nr. 1">Ekipažas Nr. 1</option>
            <option value="Ekipažas Nr. 2">Ekipažas Nr. 2</option>
            <option value="Ekipažas Nr. 3">Ekipažas Nr. 3</option>
        </select>

        <label for="status">Būsena (statusas):</label>
        <select id="status" name="status" required>
            <option value="Naujas">Naujas</option>
            <option value="Reaguojama">Reaguojama</option>
            <option value="Baigta">Baigta</option>
        </select>

        <button type="submit">Pridėti incidentą</button>
    </form>

    <h2>Aktyvūs incidentai</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Objektas / Adresas</th>
            <th>Problemos tipas</th>
            <th>Ekipažas</th>
            <th>Laikas (GMT+2 / LT)</th>
            <th>Būsena</th>
            <th>Veiksmai</th>
        </tr>
        {% for inc in incidents %}
        <tr>
            <td>{{ inc.id }}</td>
            <td>{{ inc.object }}</td>
            <td>{{ inc.type }}</td>
            <td>{{ inc.team }}</td>
            <td>{{ inc.time }}</td>
            <td>{{ inc.status }}</td>
            <td class="actions">
                <a href="/edit/{{ inc.id }}" class="btn">Redaguoti</a>
                <a href="/delete/{{ inc.id }}" class="btn btn-danger" onclick="return confirm('Ar tikrai norite ištrinti?')">Ištrinti</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Redagavimo puslapio HTML šablonas
EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <title>Redaguoti incidentą</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f7f6; color: #333; }
        h2 { color: #0056b3; }
        form { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 600px; }
        input, select { width: 100%; padding: 8px; margin: 8px 0 16px 0; display: inline-block; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button, .btn { background-color: #0056b3; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        button:hover { background-color: #004085; }
        .btn-secondary { background-color: #6c757d; }
    </style>
</head>
<body>
    <h2>Redaguoti incidentą #{{ incident.id }}</h2>
    <form method="POST">
        <label for="object">Apsaugomas objektas / adresas:</label>
        <input type="text" id="object" name="object" value="{{ incident.object }}" required>

        <label for="type">Problemos tipas:</label>
        <select id="type" name="type" required>
            <option value="Judėjimo daviklis" {% if incident.type == 'Judėjimo daviklis' %}selected{% endif %}>Judėjimo daviklis</option>
            <option value="Gaisro pavojaus signalas" {% if incident.type == 'Gaisro pavojaus signalas' %}selected{% endif %}>Gaisro pavojaus signalas</option>
            <option value="Įsilaužimo signalizacija" {% if incident.type == 'Įsilaužimo signalizacija' %}selected{% endif %}>Įsilaužimo signalizacija</option>
            <option value="Pagalbos mygtukas" {% if incident.type == 'Pagalbos mygtukas' %}selected{% endif %}>Pagalbos mygtukas</option>
        </select>

        <label for="team">Reagavimo ekipažas:</label>
        <select id="team" name="team" required>
            <option value="Nepaskirtas" {% if incident.team == 'Nepaskirtas' %}selected{% endif %}>Nepaskirtas</option>
            <option value="Ekipažas Nr. 1" {% if incident.team == 'Ekipažas Nr. 1' %}selected{% endif %}>Ekipažas Nr. 1</option>
            <option value="Ekipažas Nr. 2" {% if incident.team == 'Ekipažas Nr. 2' %}selected{% endif %}>Ekipažas Nr. 2</option>
            <option value="Ekipažas Nr. 3" {% if incident.team == 'Ekipažas Nr. 3' %}selected{% endif %}>Ekipažas Nr. 3</option>
        </select>

        <label for="status">Būsena (statusas):</label>
        <select id="status" name="status" required>
            <option value="Naujas" {% if incident.status == 'Naujas' %}selected{% endif %}>Naujas</option>
            <option value="Reaguojama" {% if incident.status == 'Reaguojama' %}selected{% endif %}>Reaguojama</option>
            <option value="Baigta" {% if incident.status == 'Baigta' %}selected{% endif %}>Baigta</option>
        </select>

        <button type="submit">Išsaugoti pakeitimus</button>
        <a href="/" class="btn btn-secondary">Atšaukti</a>
    </form>
</body>
</html>
"""

# Maršrutai (CRUD valdymas)
@app.route('/')
def index():
    incidents = Incident.query.all()
    return render_template_string(HTML_TEMPLATE, incidents=incidents)

@app.route('/add', methods=['POST'])
def add_incident():
    obj = request.form.get('object')
    inc_type = request.form.get('type')
    team = request.form.get('team')
    status = request.form.get('status')
    
    # Fiksuojamas tikslus vietinis Lietuvos laikas (GMT+2 / GMT+3)
    vilnius_tz = ZoneInfo("Europe/Vilnius")
    time_str = datetime.now(vilnius_tz).strftime('%Y-%m-%d %H:%M')
    
    new_inc = Incident(object=obj, type=inc_type, team=team, time=time_str, status=status)
    db.session.add(new_inc)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_incident(id):
    incident = Incident.query.get_or_404(id)
    if request.method == 'POST':
        incident.object = request.form.get('object')
        incident.type = request.form.get('type')
        incident.team = request.form.get('team')
        incident.status = request.form.get('status')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template_string(EDIT_TEMPLATE, incident=incident)

@app.route('/delete/<int:id>')
def delete_incident(id):
    incident = Incident.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)