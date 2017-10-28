from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345678@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'e337kImch&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(80))
    blog_entry = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_entry, owner):
        self.blog_title = blog_title
        self.blog_entry = blog_entry
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password   

#----------------------------------------------

def is_enough_characters(word):
    try:
        if (len(word) > 2):
            return True
    except ValueError:
        return False


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_page', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']    
        user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''

        if username == '':
            username_error = 'Not a valid username'
            username = ''
        else:
            if not user:
                username_error = 'Username does not exist'
                username = ''

        if user and user.password != password:
            password_error = 'Incorrect password'
            password = ''

        if user and user.password == password and not username_error and not password_error:
            session['username'] = username
            flash("Logged in")
            return redirect ('/newpost')
        else:
            return render_template('login.html', password_error=password_error, username_error=username_error)

    return render_template('login.html')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''
        verify_error = ''

        if username == '':
            username_error = 'Must fill in all form fields'
            username = ''
        else:
            if not is_enough_characters(username):
                username_error = 'Username is not long enough'
                username = ''
            else:
                if existing_user:
                    username_error = 'This username already exists'
                    username = ''

        if password == '':
            password_error = 'Must fill in all form fields'
            password = ''
        else:
            if not is_enough_characters(password):
                password_error = 'Password is not long enough'
                password = ''
            else:
                if password != verify:
                    password_error = 'Passwords do not match'
                    password = ''

        if verify == '':
            verify_error = 'Must fill in all form fields'
            verify = ''

        if not existing_user and password == verify and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error)

    return render_template('signup.html')



@app.route('/logout')
def logout():
    del session['username']
    flash("Logged out")
    return redirect('/blog')



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_entry = request.form['blog-entry']

        if blog_title == '' or blog_entry == '':
            flash('Must fill in all form fields!!', 'error')
            return render_template('newpost.html', blog_title=blog_title, blog_entry=blog_entry)
        
        if blog_title != '' and blog_entry!= '':
            new_blog = Blog(blog_title, blog_entry, owner)
            db.session.add(new_blog)        
            db.session.commit()

            return redirect ("/blog?id=" + str(new_blog.id))

    return render_template('newpost.html',title="Add a Blog Entry")


@app.route('/blog', methods=['POST', 'GET'])
def blog_page():

    all_blogs = Blog.query.all()
#    for owner in all_blogs:
#        blog_owner = User.query.filter_by(id=owner.owner_id).first()

    if request.args.get('id'):
        blog_id = request.args.get('id')
        single_blog = Blog.query.filter_by(id=blog_id).first()
        user = single_blog.owner
        return render_template('individual_blog_page.html', blog=single_blog, user=user)



    if request.args.get('user'):
        single_user = request.args.get('user')
        blog_author = User.query.filter_by(username=single_user).first()
#        single_user_id_num = single_user_id.id
        blogs = Blog.query.filter_by(owner_id=blog_author.id).all()
        return render_template('bloggers_own_page.html',single_user=single_user, blogs=blogs)

    return render_template('blog.html',title="Build a Blog", all_blogs = all_blogs)


@app.route('/', methods=['POST', 'GET'])
def index():

    all_users = User.query.all()

    if request.args:
        user = request.args.get('username')
        each_user = Blog.query.filter_by(username=user).all()
        return render_template('bloggers_own_page.html', user=each_user)

    return render_template('index.html',title="Blog Users", all_users = all_users)




if __name__ == '__main__':
    app.run()
