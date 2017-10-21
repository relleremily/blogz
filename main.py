from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12345678@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'e337kImch&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(80))
    blog_entry = db.Column(db.String(250))

    def __init__(self, blog_title, blog_entry):
        self.blog_title = blog_title
        self.blog_entry = blog_entry


@app.route('/newpost', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_entry = request.form['blog-entry']

        if blog_title == '' or blog_entry == '':
            flash('Must fill in all form fields!!', 'error')
            return render_template('newpost.html', blog_title=blog_title, blog_entry=blog_entry)
        
        if blog_title != '' and blog_entry!= '':
            new_blog = Blog(blog_title, blog_entry)
            db.session.add(new_blog)        
            db.session.commit()

            return redirect ("/blog?id=" + str(new_blog.id))

    return render_template('newpost.html',title="Add a Blog Entry")


@app.route('/blog', methods=['POST', 'GET'])
def blog_page():

    all_blogs = Blog.query.all()

    if request.args:
        blog_id = request.args.get('id')
        single_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('individual_blog_page.html', blog=single_blog)


    return render_template('blog.html',title="Build a Blog", all_blogs = all_blogs)




if __name__ == '__main__':
    app.run()
