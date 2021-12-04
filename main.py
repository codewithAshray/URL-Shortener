from flask import Flask
from flask import render_template
from flask import request
import pyshorteners as sh
import requests
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "urllogs"

mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        data = request.form.get("data")
        try:
            if data == "https://":
                flag = False
                return render_template("home.html", flag=flag)
            else:
                try:
                    flag = requests.get(data)
                    s = sh.Shortener()
                    link = s.tinyurl.short(data)
                    cur = mysql.connection.cursor()
                    try:
                        cur.execute("INSERT INTO logs(Original_url, Short_url) VALUES(%s, %s)", (data, link))
                        mysql.connection.commit()
                        cur.close()
                    except mysql.connection.IntegrityError:
                        return render_template("home.html", link=link, flag=flag.status_code)
                    return render_template("home.html", link=link, flag=flag.status_code)
                except requests.ConnectionError:
                    flag = False
                    return render_template("home.html", flag=flag)
        except requests.exceptions.MissingSchema:
            flag = False
            return render_template("home.html", flag=flag)

    return render_template("home.html")


@app.route("/history")
def history():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM logs")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template("history.html", userDetails=userDetails)
    else:
        return render_template("history.html")


if __name__ == "__main__":
    app.run(debug=True)
