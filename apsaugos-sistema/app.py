from flask import Flask, jsonify, request

app = Flask(__name__)

# Laikina atminties saugykla prototipui (vėliau bus sujungiama su Cloud duomenų baze)
incidents = []

@app.route('/')
def home():
    return "Apsaugos tarnybos debesų sistema veikia sėkmingai!"

@app.route('/api/v1/incidents', methods=['POST'])
def create_incident():
    data = request.json
    incident = {
        "id": len(incidents) + 1,
        "objectID": data.get("objectID"),
        "alertType": data.get("alertType"),
        "status": "Aktyvus"
    }
    incidents.append(incident)
    return jsonify(incident), 201

@app.route('/api/v1/incidents', methods=['GET'])
def get_active_incidents():
    return jsonify(incidents), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)