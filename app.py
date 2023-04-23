from flask import Flask, redirect, render_template, request, url_for, session

from radius_admin import *
import radius_admin
import pymysql

app = Flask(__name__)
app.secret_key = 'howhowstanfordmscs'

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Authenticate user
        admin_username, admin_password = radius_admin.get_admin_account()
        if username == admin_username and password == admin_password:
            session['username'] = username
            return redirect(url_for('logged_in'))
        else:
            return render_template('index.html', error='Invalid username or password')
    else:
        return render_template('index.html')

@app.route("/logged_in", methods=['GET', 'POST'])
def logged_in():
    # username = request.form["username"]
    # password = request.form["password"]
    # user_stats = radius_admin.get_user_stats(username, password)
    user_stats = 1
    # radius_admin.kick_user('ta')
    # radius_admin.get_user_stats('howhow')
    if user_stats:
        return render_template("logged_in.html", user_stats=user_stats)
    else:
        return redirect(url_for("index"))


@app.route("/user_stats", methods=["POST", "GET"])
def user_stats():
    # group
    username = request.args.get('username')
    # password = request.form["password"]
    # user_stats = radius_admin.get_user_stats(username, password)
    
    conn = pymysql.connect(host='localhost', user='group8', password='group8', database='radius')
    cursor = conn.cursor()
    query = f"SELECT username, SUM(acctsessiontime), SUM(acctinputoctets), SUM(acctoutputoctets) FROM radacct WHERE acctstarttime >= now() - INTERVAL 1 DAY AND username='{username}' GROUP BY username"

    cursor.execute(query)
    conn.commit()
    user_stats = None
    for username, sessiontime, inputoctets, outputoctets in cursor:
        print(f"query: {username} {inputoctets} {outputoctets}")
        user_stats = {"username": username, "session_time": sessiontime, "input_octets": inputoctets, "output_octets": outputoctets}
  
    print(user_stats)

    if user_stats is None:
        user_stats = {"username": username, "session_time": 0, "input_octets": 0, "output_octets": 0}


    query = f"SELECT username FROM radcheck where username='{username}' and attribute = 'Cleartext-Password'"
    cursor.execute(query)
    conn.commit()
    query_success = cursor.rowcount

    query = f"SELECT attribute, value from radcheck where username='{username}'"
    cursor.execute(query)
    conn.commit()
    d = {}
    for attribute, value in cursor:
        d[attribute] = value
    print(d)
    
    print(query_success)
    if query_success:
        return render_template("user_stats.html", user_stats=user_stats, curr_limit=d)
    else:
        return redirect(url_for("logged_in"))

@app.route('/register_user', methods=["POST"])
def register_user():
    username = request.form["username"]
    password = request.form["password"]

    conn = pymysql.connect(host='localhost', user='group8', password='group8', database='radius')
    
    cursor = conn.cursor()
    query = f"DELETE from radcheck where username = '{username}' and attribute='Cleartext-Password'"
    cursor.execute(query)
    conn.commit()
    
    query = f"INSERT INTO radcheck (username, attribute, op, value) VALUES ('{username}', 'Cleartext-Password', ':=', '{password}')"
    cursor.execute(query)
    conn.commit()

    return redirect(url_for("logged_in"))

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('index'))

@app.route('/kick', methods=['POST'])
def kick():
    # print(request.form.keys())
    kick_user(request.form['id'])
    return redirect(url_for('logged_in'))

@app.route('/add_limit', methods=['POST'])
def add_limit():
    volume = request.form.get("volume")
    limit = request.form.get('timelimit')
    # print(request.form.keys())
    username = request.form['id']

    conn = pymysql.connect(host='localhost', user='group8', password='group8', database='radius')
    cursor = conn.cursor()
    query = f"DELETE FROM radcheck where username='{username}' and (attribute='Max-Daily-Volume' or attribute='Max-Daily-Session')"
    cursor.execute(query)
    conn.commit()
    
    if volume:
        query = f"Insert into radcheck (username, attribute, op, value) values ('{username}', 'Max-Daily-Volume', ':=', '{volume}')"
        cursor.execute(query)
        conn.commit()
    if limit:
        query = f"Insert into radcheck (username, attribute, op, value) values ('{username}', 'Max-Daily-Session', ':=', '{limit}')"
        cursor.execute(query)
        conn.commit()
    

    return redirect(url_for('logged_in'))


if __name__ == "__main__":
    app.run(debug=True)
