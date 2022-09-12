import os

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
from flask import abort

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # za SQL lite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES

# 2. Create a Table called Comment where the tablename is "comments". It should contain an id and a
# text property which will be the primary key and the text entered into the CKEditor.

#Create the Comment Table
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)

    # 3. Establish a One to Many relationship Between the User Table (Parent) and the Comment table (Child).
    # Where One User is linked to Many Comment objects.

    # *******Add child relationship*******#
    # "users.id" The users refers to the tablename of the Users class.
    # "comments" refers to the comments property in the User class.

    # Create Foreign Key, "users.id" the users refers to the tablename of User.  ## 3.
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))  ## 3.
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.  ## 3.
    comment_author = relationship("User", back_populates="comments")  ## 3.

    # ***************Child Relationship*************#
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))  ## 3.
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.  ## 3.
    parent_post = relationship("BlogPost", back_populates="comments")


#Create the User Table
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")

    # *******Add parent relationship*******#
    # "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author") ## 3.


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    # author = db.Column(db.String(250), nullable=False)  bilo ne treba vise
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")


# db.create_all()


# Create all the tables in the database
db.create_all()

# uses Flask-Login is the LoginManager class.
login_manager = LoginManager()
login_manager.init_app(app)


#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def get_all_posts():
    try:
        posts = BlogPost.query.all()
        print(posts)
    except:
        posts = "petar"
        print(posts)
        new_user = User(
            email="1",
            password="1",
            name="1"
        )

        db.session.add(new_user)
        db.session.commit()

        new_post = BlogPost(
            title="1",
            subtitle="1",
            body="1",
            img_url="1",
            author="1",
            author_id="1",
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        posts = BlogPost.query.all()
        return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    # if request.method == "POST":
    if form.validate_on_submit():

        # If user's email already exists
        if User.query.filter_by(email=request.form.get('email')).first():
            # Send flash messsage
            flash("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return redirect(url_for('login', logged_in=current_user.is_authenticated))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)

        new_user = User(
        email=form.email.data,
        password=hash_and_salted_password,
        name=form.name.data
        )

        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)

        return redirect(url_for("get_all_posts", logged_in=current_user.is_authenticated))
        # return "care"
    # new_user = User(
    #     title=form.title.data,
    #     subtitle=form.subtitle.data,
    #
    # )
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():

            email=request.form.get("email")
            password=request.form.get("password")
            print(email, password)
            # Find user by email entered.
            user = User.query.filter_by(email=email).first()
            print(user)
            # Email doesn't exist
            if not user:
                flash("That email does not exist, please register.")
                return redirect(url_for('register'))

            # Password incorrect
            # Check stored password hash against entered password hashed.
            elif not check_password_hash(user.password, password):
                flash('Password incorrect, please try again.')
                return redirect(url_for('login'))

            # Email exists and password correct
            else:  # If the user has successfully logged in or registered, you need to use the login_user() function to authenticate them.
                login_user(user)
                print(current_user.id)
                print(type(print(current_user.id)))
                # if current_user.id == 1:   # ne radi kada se ubaci kao posebna promenljiva
                #     abc = True
                #     print(abc, "ovo")
                return redirect(url_for("get_all_posts", current_user=current_user))


    return render_template("login.html", form=form,  logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()


    return redirect(url_for('get_all_posts', logged_in=current_user.is_authenticated))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])

def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    komentari = Comment.query.filter_by(post_id=post_id).all()
    print(komentari)
    # print(komentari[0].body)

    if form.validate_on_submit():
        try:
            id_korisnika = current_user.id
            new_com = Comment(
                body=form.body.data,
                author_id=current_user.id, #AttributeError: 'AnonymousUserMixin' object has no attribute 'id'
                post_id=post_id
            )

            # ona je stavila objekte, me ni ne radi
            # comment_author=current_user,
            # parent_post=requested_post

            db.session.add(new_com)
            db.session.commit()
            komentari = Comment.query.filter_by(post_id=post_id).all()
            print(komentari)
            # print(komentari[0].body)
            return render_template("post.html", all_komentari=komentari, post=requested_post, current_user=current_user, form=form) #, logged_in=current_user.is_authenticated)
        except AttributeError:
            # print(current_user.id)
            flash("Treba da se uloguješ ili registruješ da bi komentarisao")
            return redirect(url_for('login'))
    return render_template("post.html", all_komentari=komentari, post=requested_post, current_user=current_user, form=form)


@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)

@app.route("/new-post", methods=["GET", "POST"])   #  kada sam dodao relacije izmedju baza, avlja mi gresku Method Not Allowed, to je"POST /edit-post/2 HTTP/1.1" 405 -
#Mark with decorator
@admin_only
def add_new_post():
    form = CreatePostForm()
    print("usao")
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        print("@jeste")
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])   #  kada sam dodao relacije izmedju baza, avlja mi gresku Method Not Allowed, to je"POST /edit-post/2 HTTP/1.1" 405
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        # author=post.author, # deo koda koji je visak, nije kreiran u formi
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        # post.author = edit_form.author.data  # deo koda koji je visak, nije kreiran u formi
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts', logged_in=current_user.is_authenticated))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
