import sqlite3


from flask import Flask, render_template, abort, request, redirect, url_for, session


app = Flask(__name__) # A random key that protects a session cookie that stores if user has admin accses or not
app.secret_key = b'\x8f\xa3\x19\xcd\x5f\x91\x72\x4e\xab\x2d\x0c\x6b\xde\x94\x21\x7f\xfa\x11\x3b\x68\xee\xb2\x50\xac'


@app.route('/') # Show a list of all stadiums on the home page
def home():
    conn = sqlite3.connect("stadium.db")
    cur = conn.cursor()
    cur.execute("SELECT stadium_Id, name FROM Stadium")
    stadiums = cur.fetchall()
    conn.close()
    return render_template('home.html', title='HOME', stadiums = stadiums)


@app.route("/football/<int:Id>", methods=["GET", "POST"]) # Show a specific stadium page, with detials and reviews
def stadiums(Id):
    conn = sqlite3.connect("stadium.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor() # Fetchs the specific stadium details with teams and country info by joining the tables together in one query
    cur.execute("SELECT stadium.*, teams.*, country.Stadium_country AS Country_Name FROM stadium INNER JOIN teams ON teams.Team_Id = stadium.Team_Id INNER JOIN country ON country.Country_Id = stadium.Country_Id WHERE stadium.Stadium_Id = ?;", (Id,))
    stadiums = cur.fetchone()
    if stadiums is None:
        conn.close()
        abort(404)
    if request.method == "POST": # Review submission
        if "password" in request.form: 
            password = request.form.get("password", "")
            cur.execute("SELECT password FROM admin WHERE admin_id=1")
            stored_password = cur.fetchone()[0]
            if password == stored_password:
                session["admin"] = True # Admin login

        elif "delete_review_id" in request.form and session.get("admin"): # Delete review
            review_id = int(request.form["delete_review_id"])
            cur.execute("DELETE FROM reviews WHERE reviews_id=?", (review_id,))
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

    cur.execute("SELECT Reviews_id, name, review FROM reviews WHERE stadium_id=? ORDER BY reviews_id DESC;", (Id,))
    reviews = cur.fetchall() # Fetch reviews for the stadium
    

    country_id = stadiums["Country_Id"] # Find stadiums in the same country
    cur.execute("SELECT stadium.Stadium_Id, stadium.name, country.Stadium_country FROM stadium INNER JOIN country ON stadium.Country_Id = country.Country_Id WHERE stadium.Country_Id = ? AND stadium.Stadium_Id != ?;", (country_id, Id))
    other_stadiums = cur.fetchall()
    conn.close()
    return render_template("stadiums.html", stadiums=stadiums, Id=Id, reviews=reviews, other_stadiums=other_stadiums, admin=session.get("admin", False))


@app.errorhandler(404)
def http_error_handler(error):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(debug=True)
