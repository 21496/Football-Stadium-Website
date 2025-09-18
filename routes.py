import sqlite3


from flask import Flask, render_template, abort, request, redirect, url_for, session


app = Flask(__name__) # A random key that protects a session cookie that stores if user has admin accses or not
app.secret_key = b'\x8f\xa3\x19\xcd\x5f\x91\x72\x4e\xab\x2d\x0c\x6b\xde\x94\x21\x7f\xfa\x11\x3b\x68\xee\xb2\x50\xac'


@app.route('/') # Show a list of all stadiums on the home page
def home():
    conn = sqlite3.connect("stadium.db")
    cur = conn.cursor()
    cur.execute("SELECT Id, name FROM Stadium")
    stadiums = cur.fetchall()
    conn.close()
    return render_template('home.html', title='HOME', stadiums = stadiums)


@app.route("/football/<int:Id>", methods=["GET", "POST"]) # Show a specific stadium page, with detials and reviews
def stadiums(Id):
    conn = sqlite3.connect("stadium.db")
    cur = conn.cursor() # Fetchs the specific stadium details with hometeam and location info
    cur.execute("SELECT stadium.*, hometeam.*, location.* FROM hometeam INNER JOIN stadium ON hometeam.id = stadium.team_id INNER JOIN location ON location.id = stadium.Location WHERE stadium.Id=?", (Id,))
    stadiums = cur.fetchone()
    if stadiums is None:
        conn.close()
        abort(404)
    if request.method == "POST": # Review submission
        if "password" in request.form: 
            password = request.form.get("password", "")
            cur.execute("SELECT password FROM admin WHERE id=1")
            stored_password = cur.fetchone()[0]
            if password == stored_password:
                session["admin"] = True # Admin login

        elif "delete_review_id" in request.form and session.get("admin"): # Delete review
            review_id = int(request.form["delete_review_id"])
            cur.execute("DELETE FROM reviews WHERE id=?", (review_id,))
            conn.commit()

        elif "review" in request.form: # Add new review
            name = request.form.get("name", "Anonymous").strip()
            review = request.form.get("review", "").strip()
            if review:
                cur.execute("INSERT INTO reviews (stadium_id, name, review) VALUES (?, ?, ?)", (Id, name, review))
                conn.commit()

        elif "logout" in request.form: # Logout admin
            session.pop("admin", None)

        return redirect(url_for("stadiums", Id=Id))

    cur.execute("SELECT id, name, review FROM reviews WHERE stadium_id=? ORDER BY id DESC", (Id,))
    reviews = cur.fetchall() # Fetch reviews for the stadium
    conn.close()
    return render_template("stadiums.html", stadiums=stadiums, Id=Id, reviews=reviews, admin=session.get("admin", False))


@app.errorhandler(404)
def http_error_handler(error):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(debug=True)
