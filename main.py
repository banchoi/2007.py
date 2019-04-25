from flask import Flask, render_template, request
import sqlite3
import random
import string

app = Flask(__name__)

db = sqlite3.connect("data.sqlite", check_same_thread=False);
dbexec = db.cursor();

def generateid(stringLength):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

@app.route("/")
def index():
    return render_template('home.html', message="This is a ripple clone", announcement=True);

@app.route("/api")
def api_docs():
    return render_template('apidocs.html');

# osu /web/ stuff
@app.route("/web/osu-login.php")
def login():
    dbexec.execute("SELECT username,password FROM users WHERE username=? AND password=?", [request.args.get("username"), request.args.get("password")]);

    rownum = dbexec.fetchone()

    if rownum is None:
        return '0'
    else:
        return '1'

@app.route("/web/osu-submit.php", methods=["POST"])
def submitreplay():
    score = request.args.get("score").split(":");

    if score[14] == "True":
        perfect = 1
    else:
        perfect = 0

    if score[11] == "True":
        passed = 1
    else:
        passed = 0

    dbexec.execute("INSERT INTO scores (maphash, username, submithash, threes, tens, fives, geki, katu, misses, score, maxcombo, perfect, mods, passed, grade) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [score[0], score[1], score[2], score[3], score[4], score[5], score[6], score[7], score[8], score[9], score[10], perfect, score[13], passed, score[12]]);

    id = generateid(7);
    file = request.files.get("score");

    file.save("/replays/" + id);

@app.route("/web/osu-getscores.php")
def allscores():
    dbexec.execute("SELECT * FROM scores WHERE maphash=? AND passed=1", [request.args.get("c")]);

    row = dbexec.fetchall();

    return '\n'.join(":".join(tuples) for tuples in row);

@app.route("/web/osu-getreplay.php")
def getreplay():
    app.send_static_file("/replays/" + request.args.get("c"));

app.run(debug=True, host='0.0.0.0', port=8080)
