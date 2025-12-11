
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from sqlalchemy import or_
import os



###ADitya addition
from prometheus_client import generate_latest, Counter
from flask import Response



app = Flask(__name__,
            template_folder="/app/frontend/templates",
            static_folder="/app/frontend/static")




# ==== CONFIG ====
app.config['SECRET_KEY'] = 'abcdefghijklm9876543210'  # change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://movieuser:strongpassword@db/movie_review'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==== MODELS ====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# ==== HELPERS ====
def get_current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Login required", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped



# ==== ROUTES ====

@app.route("/")
def index():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("index.html", reviews=reviews, current_user=get_current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", current_user=get_current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Welcome back!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", current_user=get_current_user())


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out", "info")
    return redirect(url_for("index"))


# ==========================
# CREATE REVIEW
# ==========================
@app.route("/review/new", methods=["GET", "POST"])
@login_required
def new_review():
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        rating = int(request.form["rating"])
        content = request.form["content"]

        review = Review(
            title=title,
            genre=genre,
            rating=rating,
            content=content,
            user_id=session["user_id"]
        )
        db.session.add(review)
        db.session.commit()

        flash("Review posted from docker!", "success")
        return redirect(url_for("index"))

    return render_template("new_review.html", current_user=get_current_user(), is_edit=False)



# ==========================
# VIEW REVIEW
# ==========================
@app.route("/review/<int:review_id>")
def view_review(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template("view_review.html", review=review, current_user=get_current_user())



# ==========================
# EDIT REVIEW (ONLY AUTHOR)
# ==========================
@app.route("/review/<int:review_id>/edit", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != session["user_id"]:
        flash("You are not allowed to edit this review.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        review.title = request.form["title"]
        review.genre = request.form["genre"]
        review.rating = int(request.form["rating"])
        review.content = request.form["content"]

        db.session.commit()
        flash("Review updated!", "success")
        return redirect(url_for("view_review", review_id=review.id))

    return render_template("new_review.html",
                           review=review,
                           is_edit=True,
                           current_user=get_current_user())



# ==========================
# DELETE REVIEW (ONLY AUTHOR)
# ==========================
@app.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != session["user_id"]:
        flash("Not allowed to delete.", "danger")
        return redirect(url_for("index"))

    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "info")
    return redirect(url_for("index"))


# ==========================
# USER PROFILE
# ==========================
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("index"))
    
    reviews = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()
    return render_template("user_profile.html", user=user, reviews=reviews, current_user=get_current_user())


# ==========================
# ALL USERS LIST
# ==========================
@app.route("/users")
def users_list():
    users = User.query.all()
    user_data = []
    for user in users:
        review_count = Review.query.filter_by(user_id=user.id).count()
        user_data.append({
            'user': user,
            'review_count': review_count
        })
    return render_template("users_list.html", user_data=user_data, current_user=get_current_user())


# ==========================
# SEARCH REVIEWS
# ==========================
@app.route("/search")
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        flash("Please enter a search term", "warning")
        return redirect(url_for("index"))
    
    # Search in title, genre, and content
    reviews = Review.query.filter(
        or_(
            Review.title.ilike(f'%{query}%'),
            Review.genre.ilike(f'%{query}%'),
            Review.content.ilike(f'%{query}%')
        )
    ).order_by(Review.created_at.desc()).all()
    
    return render_template("search_results.html", 
                          reviews=reviews, 
                          query=query, 
                          current_user=get_current_user())



REQUEST_COUNT = Counter("request_count", "Total Requests")

@app.before_request
def before_request():
    REQUEST_COUNT.inc()

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)

