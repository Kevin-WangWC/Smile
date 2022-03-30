from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

DB_NAME = "smile.db"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "2143567uyhgfds5uftyjhg"


def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        # initialise_table(connection)
        return connection
    except Error as e:
        print(e)

    return None


@app.route('/')
def render_homepage():
    return render_template("home.html", logged_in=is_logged_in())


@app.route('/menu')
def render_menu_page():
    # connect to the database
    con = create_connection(DB_NAME)

    # SELECT the things you want from your table(s)
    query = "SELECT id, name, description, volume, price, image FROM product"

    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line will actually execute the query
    product_list = cur.fetchall()  # puts the results into a list usable in python
    con.close()

    return render_template("menu.html", products=product_list, logged_in=is_logged_in())


@app.route('/contact')
def render_contact():
    return render_template("contact.html", logged_in=is_logged_in())


@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if is_logged_in():
        return redirect('/')

    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM customer WHERE email = ?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        # if given the email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty result
        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        print(session)
        return redirect('/')
    return render_template('login.html', logged_in=is_logged_in())


@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DB_NAME)

        query = "INSERT INTO customer(id, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # you need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))  # this line actually executes the query
        except sqlite3.IntegrityError:
            return redirect('signup?error=Email+has+already+been+used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', login=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


@app.route('/addtocart/<productid>')
def addtocart(productid):
    try:
        productid = int(productid)
    except ValueError:
        print("{} is not an integer".format(productid))
        return redirect("/menu?error=Invalid+product+id")
    print(session)
    userid = session['userid']
    timestamp = datetime.now()
    print("User {} would like to add {} to cart at {}".format(userid, productid, timestamp))

    query = "INSERT INTO cart(id, userid, productid, timestamp) VALUES (NULL,?,?,?)"
    con = create_connection(DB_NAME)
    cur = con.cursor()  # You need this line next

    #try to INSERT - this will fail if there is a foregin key issue
    try:
        cur.execute(query, (userid, productid, timestamp))
    except sqlite3.IntegrityError as e:
        print(e)
        print('### PROBLEM INSERTING INTO DATABSE - FOREIGN KEY ###')
        con.close()
        return redirect('/menu?error=Something+went+wrong')

    #everything works, commit the insertion or the system will immediately roll it back
    con.commit()
    con.close()
    return redirect('/menu')

@app.route('/cart')
def render_cart():
    userid = session['userid']
    query = "SELECT productid FROM cart WHERE userid=?;"
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (userid,))
    product_ids = cur.fetchall()
    print(product_ids)

    #the results from the query are a list of sets, loop though and pull out the ids
    for i in range(len(product_ids)):
        product_ids[i] = product_ids[i][0]
    print(product_ids)

    unique_product_ids = list(set(product_ids))
    print(unique_product_ids)

    for i in range(len(unique_product_ids)):
        product_count = product_ids.count(unique_product_ids[i])
        unique_product_ids[i] = [unique_product_ids[i], product_count]
    print(unique_product_ids)

    query = """SELECT name, price FROM product WHERE id =?;"""
    for item in unique_product_ids:
        cur.execute(query, (item[0],))
        item_details = cur.fetchall()
        print(item_details)
        item.append(item_details[0][0])
        item.append(item_details[0][1])

    con.close()
    print(unique_product_ids)
=
    return "hello"


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


app.run(host="0.0.0.0", debug=True)
