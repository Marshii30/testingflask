from flask import Flask, render_template, request
import mysql.connector
import os
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
# MySQL connection
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    auth_plugin='mysql_native_password'
)


cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            flash("✅ Registration successful!", "success")
            return redirect(url_for('login')) 
        except mysql.connector.IntegrityError:
            flash("❌ Username already exists!", "error")
            return redirect(url_for('register'))
    # Show the form
    return render_template('register.html')

from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch the hashed password from the DB
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:  # User found
            stored_password = result[0]
            if password == stored_password:
                flash("✅ Login successful!", "success")
                return redirect(url_for('index'))#viereview
            else:
                flash("❌ Incorrect password!", "error")
                return redirect(url_for('login'))
        else:
            flash("❌ Username not found!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')



# Show the review form
@app.route('/review_form')
def review_form():
    return render_template('add_review.html')
    

@app.route('/add_review', methods=['POST'])
def add_review():
    movie_name = request.form['movie_name']
    reviewer = request.form['reviewer']
    review = request.form['review']
    rating = int(request.form['rating'])

    sql = "INSERT INTO reviews (movie_name, reviewer, review, rating) VALUES (%s, %s, %s, %s)"
    values = (movie_name, reviewer, review, rating)

    try:
        cursor.execute(sql, values)
        db.commit()
        flash("Review added successfully with rating!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect('/')

@app.route('/reviews')
def showreview():
    try:
        cursor.execute("SELECT movie_name, reviewer, review, rating FROM reviews ORDER BY id DESC")
        reviews = cursor.fetchall()
        return render_template('showreview.html', reviews=reviews)
    except Exception as e:
        flash(f"Error fetching reviews: {str(e)}", "danger")
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
