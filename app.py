from flask import Flask, request, redirect, render_template, url_for, abort
# from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Users, Post, Tag
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
    for user in users:
        user.posts = Post.query.filter_by(user_id=user.id).all()  # Assuming you have user_id in Post table
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

# Route 9: Go to make a new post for user
@app.route('/users/<int:user_id>/posts/new', methods=["GET", "POST"])
def add_post(user_id):
    user = Users.query.get_or_404(user_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('user_detail', user_id=user.id))

    return render_template('post_form.html', user=user)


# Route 10: Show post details
@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_details.html', post=post)

# Route 11: Delete post
@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = post.user.id
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('user_detail', user_id=user_id))

# Route 12: Edit post
@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = Users.query.get_or_404(post.user_id)  # Get the associated user
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template('post_form.html', post=post, user=user)  # Pass the user to the template

# TAGS ------------------------

# Route 13: Lists all tags
@app.route('/tags', methods=["GET"])
def tags_list():
    tags = Tag.query.all()  # Fetch all tags from the database
    return render_template('tags_list.html', tags=tags)

# Route 14: 
@app.route('/tags/<int:tag_id>', methods=["GET"])
def tags_detail(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags_details.html', tag=tag)


# 
# # **GET */tags/new :*** Shows a form to add a new tag.
# # Route 15: Show form to add a new tag
# @app.route('/tags/new', methods=["GET"])
# def add_tags():
#     return render_template('tags_form.html')  # Render the form to add a new tag


# Route 15: Show form to add a new tag
@app.route('/tags/new', methods=["GET", "POST"])
def add_tag():
    if request.method == "POST":
        tag_name = request.form["name"]
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect(url_for('list_tags'))  # Redirect to the tags list page after creating the tag

    return render_template("tags_form.html")  # GET request renders the form



# Route 17: Show edit form for a tag
@app.route('/tags/<int:tag_id>/edit', methods=["GET", "POST"])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == "POST":
        tag.name = request.form['name']
        db.session.commit()
        return redirect(url_for('tags_detail', tag_id=tag.id))
    return render_template("tags_form.html", tag=tag)




# Route 18: Process edit form and update the tag
@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def update_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)  # Get the tag by its ID
    tag.name = request.form['name']  # Update the tag's name
    db.session.commit()  # Commit the change to the database
    return redirect(url_for('list_tags'))  # Redirect to the list of tags

# Route 19: Delete a tag
@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('list_tags'))  # Redirect to the list of tags after deletion
