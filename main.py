from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:productive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blogz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(120))
    body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, body, date_posted, owner):
        self.title = title
        self.body = body
        self.date_posted = date_posted
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blog = db.relationship('Blogz', backref='owner')
    
   
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password
      
#

@app.route('/')
def index():
    return redirect('/blog')



@app.route('/blog')
def blog():
    posts = Blogz.query.all()
    user_id = request.args.get('User')
    blog_id = request.args.get('id')

    if user_id:
        posts = Blogz.query.filter_by(owner_id=user_id)
        return render_template('singleuser.html', posts=posts, header="User Posts")

    if blog_id == None:
        posts = Blogz.query.all()
        return render_template('blog.html', posts=posts, title='Blogz')
    else:
        post = Blogz.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(user_name=session['user_name']).first()
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        date_posted = datetime.today()
       
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        
        if not blog_body:
            body_error = "Please enter a blog entry"
        if not body_error and not title_error:
            new_entry = Blogz(blog_title, blog_body, date_posted, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        user = User.query.filter_by(user_name=user_name).first()
        if user and user.password == password:
            session['user_name'] = user_name
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


def is_filled(val):
    if val != "":  
        return True 
    else:  
        return False  

def no_whitespace(val):
    whitespace = " "
    if whitespace not in val:
        return True
    else:
        return False

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':    
        user_name = request.form['user_name']  
        password = request.form['password']  
        verify = request.form['verify']  
        user = User.query.filter_by(user_name=user_name).first()

        user_name_error = ""  
        password_error = ""  
        verify_error = ""  
    

    
        if not is_filled(user_name):
            user_name_error = "This field cannot be empty"
            user_name = ""
        else:
            user_name_len = len(user_name)
            if  user_name_len > 20 or user_name_len < 3:
                user_name_error = "Username must be between 3 and 20 characters"
                user_name = ""
            else:
                if not no_whitespace(user_name):
                    user_name_error = "Spaces are not allowed"
                    user_name = ""

            if not is_filled(password):
                password_error = "This field cannot be empty"
                password = ""
            else:
                password_len = len(password)
            if  password_len > 20 or password_len < 3:
                password_error = "Password must be between 3 and 20 characters"
                password = ""
            else:
                if not no_whitespace(password):
                    password_error = "Spaces are not allowed"
                    password = ""

                if not is_filled(verify):
                    verify_error = "This field cannot be empty"
                    verify_input = ""
                else:
                    if verify != password:
                        verify_error = "Passwords must match"
                        verify = ""

    
   
        if not user_name_error and not password_error and not verify_error: 

            session['user_name'] = user_name
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error') 
            return render_template ("signup.html",user_name=user_name, 
        user_name_error=user_name_error, password_error=password_error, verify_error=verify_error,)


  
        
    return render_template('signup.html', title='Login')

@app.route('/logout')
def logout():  
    del session['user_name']
    return redirect('/blog') 

if  __name__ == "__main__":
    app.run()
