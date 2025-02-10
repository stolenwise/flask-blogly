"""Blogly application."""

from flask import Flask, redirect, render_template, request, url_for
from models import db, connect_db, Users

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

# Route 1: Redirect to /users
@app.route('/')
def home():
    return redirect('/users')

# Route 2: Show list of users
@app.route('/users')
def list_users():
    users = Users.query.all()
    return render_template('user_list.html', users=users)

# Route 3: Show the add user form
@app.route('/users/new')
def show_new_user_form():
    return render_template('user_form.html')

# Route 4: Process the add form
@app.route('/users/new', methods=["POST"])
def create_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url']

    new_user = Users(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('list_users'))

# Route 5: Show information about a user
@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = db.session.get(Users, user_id)  # Updated from Users.query.get()
    if not user:
        abort(404)
    return render_template('user_detail.html', user=user)

# Route 6: Show edit form for a user
@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = Users.query.get_or_404(user_id)
    return render_template('user_form.html', user=user, editing=True)

# Route 7: Handle form submission for edits
@app.route('/users/<int:user_id>/edit', methods=["POST"])
def update_user(user_id):
    user = Users.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.commit()
    return redirect(url_for('list_users'))

# Route 8: Delete a user
@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))
