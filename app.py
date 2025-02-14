from flask import Flask, request, redirect, render_template, url_for, abort
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Users
import logging

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://lewis.stone:R3dr0ver%23897@localhost/blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey12345'  # Add your secret key here
app.config['DEBUG'] = True
app.config['ENV'] = 'development'

# Enabling logging for Flask
logging.basicConfig(level=logging.DEBUG)

# Nowlogs will show more details when running the app



# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# toolbar = DebugToolbarExtension(app)

connect_db(app)

# Create tables within application context
with app.app_context():
    db.create_all()

@app.route('/')
def root():
    """Homepage redirects to list of users."""
    app.logger.debug("Redirecting to /users route.")
    return redirect("/users")

# Route 2: Show list of users
@app.route('/users')
def list_users():
    users = Users.query.all()
    app.logger.debug(f"Users found: {users}")
    return render_template('user_list.html', users=users)

# Route 3: Show the add user form
@app.route('/users/new')
def show_new_user_form():
    app.logger.debug("Rendering the new user form.")
    # print("Entering the new user form route")
    return render_template('user_form.html')

@app.route('/users/new', methods=["POST"])
def create_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url']

    app.logger.debug(f"Creating user: {first_name} {last_name}, Image URL: {image_url}")


    new_user = Users(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    app.logger.debug(f"User {first_name} {last_name} created successfully.")
    return redirect(url_for('list_users'))


# Route 5: Show information about a user
@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = db.session.get(Users, user_id)  # Updated from Users.query.get()
    if not user:
        abort(404)
    return render_template('user_details.html', user=user)

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
