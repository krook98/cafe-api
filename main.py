import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


def to_dict(self):
    dictionary = {}
    for column in self.__table__.columns:
        dictionary[column.name] = getattr(self, column.name)
    return dictionary

@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=to_dict(random_cafe))

@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[to_dict(cafe) for cafe in cafes])


@app.route("/search")
def search_cafe():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(query_location).first()
    if cafe:
        return jsonify(cafe=to_dict(cafe))
    else:
        return jsonify({"Not Found": "Sorry, we don't have a cafe at that location"})

@app.route("/add", methods=['POST'])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify({"Success": "Added a new cafe"})


@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Price updated"})
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"})


@app.route("/delete/<int:cafe_id>", methods=['DELETE'])
def delete(cafe_id):
    api_key = request.args.get('api-key')
    if api_key is "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": "Cafe deleted"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"}), 404
    else:
        return jsonify(error={"Forbidden": "You don't have permission to do that. Make sure you have correct API Key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
