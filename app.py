from flask import Flask, flash, request, render_template, redirect, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


# create flask app, set secret key and configure database
app = Flask(__name__)
app.config['SECRET_KEY'] = '29c60916714c8b899ca90061bbcffa200e6ce2d567788a9c'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///journal.db'
db = SQLAlchemy(app)
# instantiate the marshmallow
ma = Marshmallow(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# create database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    products = db.relationship("Product", backref="user")

    def __repr__(self):
        return self.name

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False, default="N/A")
    quantity = db.Column(db.Integer, nullable=False, default="N/A")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return self.name

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email')

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'url', 'price', 'quantity', 'date')

with app.app_context():
    db.create_all()


# define login decorator
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    # check if user is in session
    if 'user_id' in session:
            user_id = session['user_id']
    # user = User.query.filter_by(id=user_id).first()
    #populate database
    #  product = Product(name='social media 30', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut quis faucibus augue. Quisque tempus porttitor nisi laoreet viverra. Etiam semper, ante eu tincidunt bibendum, tellus ex tincidunt est, vitae posuere.', url='static/images/social.jpg', price=200, quantity=10, user_id=50)
    # db.session.add(product)
    # db.session.commit()
    # querry all products from database
    products = Product.query.order_by(Product.name.desc()).all()
    return render_template("index.html", products=products)


@app.route("/json")
# @login_required
def json_api():
    # check if user is in session
    if 'user_id' in session:
            user_id = session['user_id']
    products = Product.query.order_by(Product.name.desc()).all()
    product_schema = ProductSchema(many=True)
    output = product_schema.dump(products)
    return jsonify({'Product': output})

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        # ensure that user inputs and confirms that their password inputs match
        if not password or confirmation != password:
            flash("password does not match")
            return redirect("/register")

        # ensure that user inputs and confirms that their password inputs match
        if not email or not username:
            flash("Username or Email field can not be blank!")
            return redirect("/register")

        # makes sure ther is no duplicate username
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists!!")
            return redirect("/register")

        # makes sure ther is no duplicate username
        emails = User.query.filter_by(email=email).first()
        if emails:
            flash("email already exists!!")
            return redirect("/register")

        # hash password
        hash = generate_password_hash(password)
        # creates and adds the user's information into the database
        user = User(username=username, email=email, password=hash)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("login.html")

        # Query database for username
        user = User.query.filter_by(username=request.form.get("username")).first()
        if not user:
            flash("Incorrect Username or Password!!!")
            return render_template("login.html")

        # Ensure username exists and password is correct
        if not check_password_hash(user.password, request.form.get("password")):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = user.id
        flash("Welcome, Write Your thoughts")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/product/<int:id>/")
def product(id):
    """Prints out Users products"""

    # check if user is in session
    if 'user_id' in session:
        user_id = session['user_id']
    product = Product.query.filter_by(id=id).first()
    product_schema = ProductSchema()
    output = product_schema.dump(product)
    return jsonify({'Product': output})

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
if __name__ == "__main__":
    app.run(debug=True)
