import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'diet'
db_path = os.path.join(os.path.dirname(__file__), 'diet.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)

db = SQLAlchemy(app)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    calorie = db.Column(db.Integer, nullable=False)
    date_of_reception = db.Column(db.DateTime, nullable=False, default=datetime.now())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.now())

class FoodResource(Resource):
    def get(self, food_id=None):
        if food_id:
            food = Food.query.get(food_id)
            if food:
                return {
                    "id": food.id,
                    "name": food.name,
                    "category": food.category,
                    "calorie": food.calorie,
                }
            else:
                return {"message": "საკვების ინფორმაცია ვერ ვიპოვეთ"}, 404
        else:
            foods = Food.query.all()
            result = [
                {
                    "id": food.id,
                    "name": food.name,
                    "category": food.category,
                    "calorie": food.calorie,
                }
                for food in foods
            ]
            return result

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument(
            "category", type=str, required=True, help="Category is required"
        )
        parser.add_argument(
            "calorie", type=int, required=True, help="Calorie is required"
        )
        args = parser.parse_args()

        name = args["name"]
        category = args["category"]
        calorie = args["calorie"]

        food = Food(name=name, category=category, calorie=calorie)
        db.session.add(food)
        db.session.commit()

        return {"message": "საკვების ინფორმაცია წარმატებით დაემატა"}, 201

    def put(self, food_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument(
            "category", type=str, required=True, help="Category is required"
        )
        parser.add_argument(
            "calorie", type=int, required=True, help="Calorie is required"
        )
        args = parser.parse_args()

        name = args["name"]
        category = args["category"]
        calorie = args["calorie"]

        food = Food.query.get(food_id)
        if food:
            food.name = name
            food.category = category
            food.calorie = calorie
            db.session.commit()
            return {"message": "საკვების ინფორმაცია წარმატებით შეიცვალა"}, 200
        else:
            return {"message": "საკვები არ არის ნაპოვნი"}, 404

    def delete(self, food_id):
        food = Food.query.get(food_id)
        if food:
            db.session.delete(food)
            db.session.commit()
            return {"message": "წარმატებით წაიშალა"}, 200
        else:
            return {"message": "საკვები არ არის ნაპოვნი"}, 404


api.add_resource(FoodResource, "/api/food", "/api/food/<int:food_id>")

@app.route('/')
def home():
    foods = Food.query.all()
    return render_template('home.html', foods=foods)

@app.route('/filter_by_date', methods=['POST'])
def filter_by_date():
    filter_date = request.form['filter_date']
    filter_hour = request.form['filter_hour']
    filter_datetime = datetime.fromisoformat(filter_date + ' ' + filter_hour)
    foods = Food.query.filter(db.func.extract('hour', Food.date_of_reception) == filter_datetime.hour).all()
    return render_template('home.html', foods=foods)

@app.route('/register', methods=['GET', 'POST'])
def register():
    logged = session.get('user_id')
    if(not logged):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('რეგისტრაცია წარმატებით გაიარეთ.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    logged = session.get('user_id')
    if(not logged):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['username'] = username
                flash('წარმატებით შეხვედით!', 'success')
                return redirect(url_for('home'))
            else:
                flash('არასწორი მომხარებლის სახელი ან პაროლი.', 'error')
        return render_template('login.html')
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('თქვენ გამოხვედით.', 'success')
    return redirect(url_for('home'))

@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        calorie = int(request.form['calorie'])
        food = Food(name=name, category=category, calorie=calorie)
        db.session.add(food)
        db.session.commit()
        flash('საკვების ინფორმაცია წარმატებით დაემატა!', 'success')
        return redirect(url_for('home'))
    return render_template('add_food.html')


@app.route('/edit_food/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    if request.method == 'POST':
        food.name = request.form['name']
        food.category = request.form['category']
        food.calorie = int(request.form['calorie'])
        db.session.commit()
        flash('საკვების ინფორმაცია განახლდა!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_food.html', food=food)


@app.route('/delete_food/<int:food_id>', methods=['GET'])
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()
    flash('საკვების ინფორმაცია ამოიშალა!', 'success')
    return redirect(url_for('home'))


@app.route('/food/<int:food_id>', methods = ["GET"])
def view_food(food_id):
    food = Food.query.get_or_404(food_id)
    return render_template('food.html', food=food)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)

