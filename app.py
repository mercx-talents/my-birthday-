from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    return conn

@app.route("/")
def home():
    conn = get_db()
    wishes = conn.execute("SELECT * FROM wishes").fetchall()
    visits = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()

    if visits:
        new_count = visits[0] + 1
        conn.execute("UPDATE visitors SET count=? WHERE id=1",(new_count,))
    else:
        conn.execute("INSERT INTO visitors VALUES (1,1)")
        new_count = 1

    conn.commit()
    conn.close()

    return render_template("index.html", wishes=wishes, visits=new_count)

@app.route("/send", methods=["POST"])
def send():
    name = request.form["name"]
    message = request.form["message"]

    conn = get_db()
    conn.execute("INSERT INTO wishes (name,message) VALUES (?,?)",(name,message))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/admin")
def admin():
    conn = get_db()
    wishes = conn.execute("SELECT * FROM wishes").fetchall()
    conn.close()
    return render_template("admin.html", wishes=wishes)

app.run(debug=True)
