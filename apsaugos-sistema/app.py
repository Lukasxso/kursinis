import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Paimama PostgreSQL nuoroda iš Render aplinkos kintamųjų arba naudojama SQLite lokaliai
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///security.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()
    if not Incident.query.first():
        db.session.add(Incident(object="Vilnius, Gedimino pr. 10", type="Judėjimo daviklis", team="Ekipažas Nr. 2", time="2026-11-10 15:10", status="Reaguojama"))
        db.session.add(Incident(object="Kaunas, Laisvės al. 45", type="Gaisro pavojaus signalas", team="Nepaskirtas", time="2026-11-10 14:55", status="Baigta"))
        db.session.commit()

# HTML šablonai ir maršrutai (HTML_TEMPLATE, EDIT_TEMPLATE, /, /add, /edit, /delete) išlieka tokie patys kaip anksčiau...