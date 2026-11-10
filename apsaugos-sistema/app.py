from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    html_content = """
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
            .badge-active { background: #ffc107; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold; }
            .badge-done { background: #198754; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Apsaugos Tarnybos Debesų Valdymo Pultas</h1>
            <div class="status">🟢 Sistema veikia debesyje (Render.com) – Duomenų sinchronizacija ir šifravimas aktyvūs</div>
            
            <h3>Aktyvūs incidentai (Incidentų žurnalas - S2)</h3>
            <table>
                <tr><th>ID</th><th>Saugomas objektas</th><th>Pavojaus tipas</th><th>Laikas</th><th>Būsena</th></tr>
                <tr><td>#101</td><td>Vilnius, Gedimino pr. 10</td><td>Judėjimo daviklis</td><td>2026-11-10 15:10</td><td><span class="badge-active">Reaguojama</span></td></tr>
                <tr><td>#102</td><td>Kaunas, Laisvės al. 45</td><td>Gaisro pavojaus signalas</td><td>2026-11-10 14:55</td><td><span class="badge-done">Baigta</span></td></tr>
            </table>

            <h3 style="margin-top: 30px;">Reagavimo ekipažų būsenos (S3)</h3>
            <table>
                <tr><th>Ekipažas</th><th>Zonavimas</th><th>Būsena</th></tr>
                <tr><td>Ekipažas Nr. 1</td><td>Naujamiestis</td><td>Laisvas / Patruliuoja</td></tr>
                <tr><td>Ekipažas Nr. 2</td><td>Senamiestis</td><td>Siunčiamas į incidentą #101</td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run(debug=True)