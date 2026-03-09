from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import sqlite3, os

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/voices"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect("database.db")
    return conn

@app.route("/")
def home():
    conn = get_db()
    wishes = conn.execute("SELECT id, name, message FROM wishes").fetchall()
    visits = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()[0]
    conn.execute("UPDATE visitors SET count=? WHERE id=1",(visits+1,))
    conn.commit()
    conn.close()
    return render_template("index.html", wishes=wishes, visits=visits+1)

@app.route("/send", methods=["POST"])
def send():
    name = request.form["name"]
    message = request.form["message"]
    voice_file = request.files.get("voice")
    filename = None
    if voice_file:
        filename = voice_file.filename
        voice_file.save(os.path.join(UPLOAD_FOLDER, filename))
    conn = get_db()
    conn.execute("INSERT INTO wishes (name,message,voice) VALUES (?,?,?)",(name,message,filename))
    conn.commit()
    conn.close()
    return redirect("/")

# Admin login
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        admin = conn.execute("SELECT * FROM admin WHERE username=? AND password=?",(username,password)).fetchone()
        conn.close()
        if admin:
            session["admin"]=True
            return redirect("/admin")
        else:
            return "Wrong credentials"
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db()
    wishes = conn.execute("SELECT * FROM wishes").fetchall()
    visits = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()[0]
    conn.close()
    return render_template("admin.html", wishes=wishes, visits=visits)

@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db()
    conn.execute("DELETE FROM wishes WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("admin",None)
    return redirect("/login")

@app.route("/voices/<filename>")
def voices(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

app.run(debug=True)
