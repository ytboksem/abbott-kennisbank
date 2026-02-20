import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "abbott_secret"

DATABASE = "knowledge.db"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------------------------
# Database automatisch maken
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            department TEXT,
            category TEXT,
            version TEXT,
            content TEXT,
            video_link TEXT,
            file_name TEXT,
            date_created TEXT,
            views INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]
        if password == "Windesheim":
            return redirect(url_for("dashboard"))
    return render_template("login.html")


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM articles")
    total = c.fetchone()[0]

    c.execute("SELECT * FROM articles ORDER BY date_created DESC LIMIT 5")
    latest = c.fetchall()

    c.execute("SELECT * FROM articles ORDER BY views DESC LIMIT 5")
    most_viewed = c.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           total=total,
                           latest=latest,
                           most_viewed=most_viewed)


# -------------------------
# ARTIKEL TOEVOEGEN
# -------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        department = request.form["department"]
        category = request.form["category"]
        version = request.form["version"]
        content = request.form["content"]
        video_link = request.form["video_link"]

        file = request.files["file"]
        filename = None

        if file and file.filename != "":
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        date_created = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO articles
            (title, author, department, category, version, content,
            video_link, file_name, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, department, category,
              version, content, video_link,
              filename, date_created))
        conn.commit()
        conn.close()

        return redirect(url_for("articles"))

    return render_template("add.html")


# -------------------------
# ARTIKEL OVERZICHT + ZOEK
# -------------------------
@app.route("/articles")
def articles():
    search = request.args.get("search")
    category = request.args.get("category")
    department = request.args.get("department")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend(['%' + search + '%'] * 2)

    if category:
        query += " AND category = ?"
        params.append(category)

    if department:
        query += " AND department = ?"
        params.append(department)

    c.execute(query, params)
    articles = c.fetchall()
    conn.close()

    return render_template("articles.html", articles=articles)


# -------------------------
# DETAIL
# -------------------------
@app.route("/article/<int:id>")
def detail(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("UPDATE articles SET views = views + 1 WHERE id = ?", (id,))
    conn.commit()

    c.execute("SELECT * FROM articles WHERE id = ?", (id,))
    article = c.fetchone()

    conn.close()
    return render_template("detail.html", article=article)

# -------------------------
# EDIT
# -------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        department = request.form["department"]
        category = request.form["category"]
        version = request.form["version"]
        content = request.form["content"]
        video_link = request.form["video_link"]

        c.execute('''
            UPDATE articles
            SET title=?, author=?, department=?, category=?,
                version=?, content=?, video_link=?
            WHERE id=?
        ''', (title, author, department, category,
              version, content, video_link, id))

        conn.commit()
        conn.close()
        return redirect(url_for("detail", id=id))

    c.execute("SELECT * FROM articles WHERE id=?", (id,))
    article = c.fetchone()
    conn.close()

    return render_template("edit.html", article=article)

# -------------------------
# DELETE
# -------------------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM articles WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("articles"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)


