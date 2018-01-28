from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:fS2mbWR@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '2Xe$vHjVr1&G'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username 
        self.password = password


@app.before_request
def require_login():
    require_login = ['new_post']
    if request.endpoint in require_login and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="blog users!", users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash("User password incorrect or user does not exist","error") 
    return render_template('login.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST': 
        username = request.form['username'] 
       
        if len(username) < 3 or len(username) > 20 or ' ' in username:
            flash("Username must be between 3 and 20 characters with no spaces", "error")
            return redirect('/signup')

        password = request.form['password'] 
        verify = request.form['verify']

        if len(password) < 3 or len(password) > 20 or ' ' in password:
            flash("Password must be between 3 and 20 characters with no spaces", "error")
            return redirect ('/signup')

        if verify != password or len(verify) == 0:
            flash("Passwords do not match", "error")
            return redirect ('/signup')

            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/index')
            else:
                flash('Duplicate user', 'error')    
    return render_template('signup.html')


@app.route('/blog')
def blog():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', title="blog posts!", blogs=blogs)


@app.route('/singleblog')
def single_blog():
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    return render_template('single_blog.html', blog=blog, blog_id=blog_id)
    

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html')

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter(username=session['username']).first()
        owner_id = owner.id

        if blog_title == "":
            flash("Please enter a title for your blog","error")
            return redirect('/newpost')

        if blog_body == "":
            flash("Please enter content for your blog","error")
            return redirect('newpost')

        if blog_body_error or title_error:
            return render_template('new_post.html', blog_title=blog_title, blog_body=blog_body)
        else: 
            newpost = Blog(blog_title, blog_body, owner)
            db.session.add(newpost)
            db.session.commit()
            blog = Blog.query.filter_by(title=title).first()
            user = User.query.filter_by(id = owner_id).first()

            return render_template('single_blog.html', blog=blog, user=user, blog_title=blog_title, blog_body=blog_body)    


@app.route('/singleuser')
def singleuser():
    user_id = request.args.get('user')
    user = User.query.get(user_id)
    owner = user
    blog = Blog.query.filter_by(owner_id=user_id).all
    return render_template('single_user.html', blog=blog, user_id=user_id, user=user)


@app.route('/logout', methods=['GET'])
def logout():
    if "username" in session:
        del session["username"]
    return render_template('blog.html')
        

if __name__ == '__main__':
    app.run()

