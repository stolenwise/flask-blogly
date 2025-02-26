from flask import Flask, request, redirect, render_template, url_for, abort, flash
# from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate  
from models import db, Users, Post, Tag
import logging

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://lewis.stone:R3dr0ver%23897@localhost/blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey12345'  # Add your secret key here
app.config['DEBUG'] = True
app.config['ENV'] = 'development'

db.init_app(app)
migrate = Migrate(app, db)

# Enabling logging for Flask
logging.basicConfig(level=logging.DEBUG)

# Nowlogs will show more details when running the app



# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# toolbar = DebugToolbarExtension(app)

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

@app.route('/posts/new', methods=["GET", "POST"])
def add_post():
    user_id = request.args.get('user_id')  # Get user_id from the URL
    user = Users.query.get(user_id)  # Get the user from the database
    
    tags = Tag.query.all()  # Get all tags for the form

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_ids = request.form.getlist('tags')  # Get the selected tag IDs as a list

        # Create the new post object
        new_post = Post(title=title, content=content, user_id=user.id)
        
        db.session.add(new_post)
        db.session.commit()  # Commit to generate the post ID

        # Link the post to the selected tags
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)  # Get each tag by ID
            new_post.tags.append(tag)  # Append the tag to the post's tags relationship
        
        db.session.commit()  # Commit to save the relationship

        return redirect(url_for('post_detail', post_id=new_post.id))  # Redirect to the post detail page

    # In the GET request, just pass the user and tags. No post object is needed here for a new post.
    return render_template('post_form.html', user=user, tags=tags)



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
@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()  # Get all tags for the dropdown
    if request.method == 'POST':
        # Assuming you're handling form submission here
        post.title = request.form['title']
        post.content = request.form['content']
        
        # Update tags
        post.tags = Tag.query.filter(Tag.id.in_(request.form.getlist('tags'))).all()
        
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))  # Redirect to the post detail page
    
    return render_template('post_form.html', post=post, tags=tags, user=post.user)

# TAGS ------------------------

# Route 13: Lists all tags
@app.route('/tags', methods=["GET"])
def tags_list():
    tags = Tag.query.all()  # Fetch all tags from the database
    return render_template('tags_list.html', tags=tags)

# Route 14: Tags page
@app.route('/tags/<int:tag_id>', methods=["GET"])
def tags_detail(tag_id):
    tag = Tag.query.get(tag_id)
    
    if not tag:
        return "Tag not found", 404
    
    # Get all posts related to this tag
    posts = tag.posts.all()  # Ensure you're getting a list of posts
    
    return render_template('tags_details.html', tag=tag, posts=posts)





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

        # Check if tag already exists
        existing_tag = Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            # Redirect to tags list or show a message that the tag already exists
            flash("Tag already exists!")
            return redirect(url_for('tags_list'))  # Or handle as needed

        # If tag doesn't exist, create a new tag
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect(url_for('tags_list'))  # Correct route to redirect after creating the tag

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
    return redirect(url_for('tags_list'))  # Correct

# Route 19: Delete a tag
@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('tags_list'))  # Correct

