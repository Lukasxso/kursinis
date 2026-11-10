from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from routeros_api import RouterOsApiPool

app = Flask(__name__)
CORS(app)

# Mikrotik config
MIKROTIK_IP = "172.16.0.1"
USERNAME = "admin"
PASSWORD = "asd"  

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create-vlan", methods=["POST"])
def create_vlan():
    data = request.json

    vlan_id = data.get("vlan_id")
    vlan_name = data.get("vlan_name")

    # Auto-generate IP pool
    ip_pool = f"172.16.{vlan_id}.100-172.16.{vlan_id}.200"

    try:
        connection = RouterOsApiPool(
            MIKROTIK_IP,
            username=USERNAME,
            password=PASSWORD,
            plaintext_login=True,
            use_ssl=False
        )
        api = connection.get_api()

        # Create VLAN
        vlan = api.get_resource("/interface/vlan")
        vlan.add(
            name=vlan_name,
            vlan_id=vlan_id,
            interface="ether1"
        )

        # Create IP pool
        pool = api.get_resource("/ip/pool")
        pool.add(
            name=vlan_name + "_pool",
            ranges=ip_pool
        )

        connection.disconnect()

        return jsonify({
            "status": "success",
            "vlan_id": vlan_id,
            "vlan_name": vlan_name,
            "ip_pool": ip_pool
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)