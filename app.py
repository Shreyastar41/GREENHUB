import os
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "greenpulse.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("GREENPULSE_SECRET_KEY") or os.environ.get("SECRET_KEY", "greenpulse-dev-secret")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024



def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS plantations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tree_name TEXT NOT NULL,
            plantation_date TEXT NOT NULL,
            location_text TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            image_filename TEXT,
            status TEXT DEFAULT 'Growing',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.route("/")
def home():
    db = get_db()
    total_trees = db.execute("SELECT COUNT(*) AS c FROM plantations").fetchone()["c"]
    total_users = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    return render_template("home.html", total_trees=total_trees, total_users=total_users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        db = get_db()
        exists = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone()
        if exists:
            flash("Username or email already exists.", "danger")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE lower(email) = ? OR lower(username) = ?",
            (identifier, identifier),
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid login credentials.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_plantation():
    if request.method == "POST":
        tree_name = request.form.get("tree_name", "").strip()
        plantation_date = request.form.get("plantation_date", "").strip()
        location_text = request.form.get("location_text", "").strip()
        latitude = request.form.get("latitude") or None
        longitude = request.form.get("longitude") or None

        if not tree_name or not plantation_date or not location_text:
            flash("Tree name, date, and location are required.", "danger")
            return render_template("add_plantation.html")

        image_file = request.files.get("image")
        filename = None
        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                flash("Only JPG and PNG images are allowed.", "danger")
                return render_template("add_plantation.html")

            safe_name = secure_filename(image_file.filename)
            name, ext = os.path.splitext(safe_name)
            filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext.lower()}"
            UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            image_file.save(UPLOAD_FOLDER / filename)

        db = get_db()
        db.execute(
            """
            INSERT INTO plantations
                (user_id, tree_name, plantation_date, location_text, latitude, longitude, image_filename, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Growing', ?)
            """,
            (
                session["user_id"],
                tree_name,
                plantation_date,
                location_text,
                float(latitude) if latitude else None,
                float(longitude) if longitude else None,
                filename,
                datetime.utcnow().isoformat(),
            ),
        )
        db.commit()

        flash("Plantation record added successfully!", "success")
        return redirect(url_for("records"))

    return render_template("add_plantation.html")


@app.route("/records")
def records():
    db = get_db()
    filter_user = request.args.get("user", "all")

    query = """
    SELECT p.*, u.username
    FROM plantations p
    JOIN users u ON p.user_id = u.id
    """
    params = []

    if filter_user == "mine" and g.user:
        query += " WHERE p.user_id = ?"
        params.append(g.user["id"])

    query += " ORDER BY p.created_at DESC"

    all_records = db.execute(query, params).fetchall()
    return render_template("records.html", records=all_records, filter_user=filter_user)


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    total_trees = db.execute("SELECT COUNT(*) AS c FROM plantations").fetchone()["c"]
    my_trees = db.execute(
        "SELECT COUNT(*) AS c FROM plantations WHERE user_id = ?", (session["user_id"],)
    ).fetchone()["c"]

    co2_saved = total_trees * 21
    progress_pct = min(100, int((my_trees / 20) * 100)) if my_trees else 0

    return render_template(
        "dashboard.html",
        total_trees=total_trees,
        my_trees=my_trees,
        co2_saved=co2_saved,
        progress_pct=progress_pct,
    )


@app.route("/map")
def map_view():
    return render_template("map.html")


@app.route("/api/plantations")
def plantations_api():
    db = get_db()
    rows = db.execute(
        """
        SELECT p.id, p.tree_name, p.location_text, p.latitude, p.longitude, p.plantation_date, p.status, u.username
        FROM plantations p
        JOIN users u ON p.user_id = u.id
        WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
        """
    ).fetchall()

    data = [dict(row) for row in rows]
    return jsonify(data)


@app.route("/about")
def about():
    return render_template("about.html")

with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
