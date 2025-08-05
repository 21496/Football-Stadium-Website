import sqlite3


from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def home():
    conn = sqlite3.connect("stadium.db")
    cur = conn.cursor()
    cur.execute("SELECT Id, name, image_path FROM Stadium")
    stadiums = cur.fetchall()
    conn.close()
    return render_template('home.html', title='HOME', stadiums = stadiums)


@app.route("/football/<int:Id>")
def stadiums(Id):
    conn = sqlite3.connect("stadium.db")
    cur = conn.cursor()
    cur.execute("SELECT Id, name, image_path FROM Stadium")
    stadiums = cur.fetchall()
    conn.close()
    return render_template("stadiums.html", stadiums = stadiums, Id = Id)


if __name__ == '__main__':
    app.run(debug=True)
