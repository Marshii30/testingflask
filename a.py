from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Maharshi@2004",
    database="session1"
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
        # Optionally hash password here

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            flash("✅ Registration successful!", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("❌ Username already exists!", "error")
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            if password == stored_password:  # Replace with check_password_hash if hashing is used
                session['username'] = username
                flash("✅ Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("❌ Incorrect password!", "error")
        else:
            flash("❌ Username not found!", "error")

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("🔒 You have been logged out.", "info")
    return redirect(url_for('index'))


@app.route('/review_form')
def review_form():
    if 'username' not in session:
        flash("⚠️ Please log in to add a review.", "warning")
        return redirect(url_for('login'))

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
        flash("✅ Review added successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"❌ Error: {str(e)}", "danger")

    return redirect(url_for('index'))


@app.route('/reviews')
def showreview():
    if 'username' not in session:
        flash("⚠️ Please log in to view reviews.", "warning")
        return redirect(url_for('login'))

    try:
        cursor.execute("SELECT movie_name, reviewer, review, rating FROM reviews ORDER BY id DESC")
        reviews = cursor.fetchall()
        return render_template('showreview.html', reviews=reviews)
    except Exception as e:
        flash(f"❌ Error fetching reviews: {str(e)}", "danger")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
