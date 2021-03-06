from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from audio import printWAV
import time, random, threading
from turbo_flask import Turbo
from flask_bcrypt import Bcrypt
from flask_behind_proxy import FlaskBehindProxy


app = Flask(__name__)                    # this gets the name of the file so Flask knows it's name
proxied = FlaskBehindProxy(app)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

interval=5
FILE_NAME = "misery.wav"
turbo = Turbo(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.password}')"


@app.route("/")                       # this tells you the URL the method below is related to
@app.route("/home")  
def hello_world():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')

@app.route("/about")                          # this tells you the URL the method below is related to
def about():
    return render_template('about.html', subtitle='Home Page', subtitle2='About Page', text='This is the about page!')
  
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=pw_hash)
        db.session.add(user)
        db.session.commit()
    if form.validate_on_submit(): # checks if entries are valid
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('about')) # if so - send to home page
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username = form.username.data
    password = form.password.data
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first() # https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
        
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Invalid login. Please try again.')
            return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page
        else:
            flash(f'Login successful.', 'success')
            print('hey')
            return redirect(url_for('about')) # if so - send to home page
            
  
    return render_template('login.html', title='Log In', form=form)

@app.route("/captions")
def captions():
  TITLE = "Misery"
  return render_template('captions.html', songName=TITLE, file=FILE_NAME)

@app.before_first_request
def before_first_request():
    #resetting time stamp file to 0
    file = open("pos.txt","w") 
    file.write(str(0))
    file.close()

    #starting thread that will time updates
    threading.Thread(target=update_captions).start()
    threading.Thread(target=update_captions, daemon=True).start()
    
    

@app.context_processor
def inject_load():
    # getting previous time stamp
    file = open("pos.txt","r")
    pos = int(file.read())
    file.close()

    # writing next time stamp
    file = open("pos.txt","w")
    file.write(str(pos+interval))
    file.close()

    #returning captions
    return {'caption':printWAV(FILE_NAME, pos=pos, clip=interval)}

def update_captions():
    with app.app_context():
        while True:
            # timing thread waiting for the interval
            time.sleep(interval)

            # forcefully updating captionsPane with caption
            turbo.push(turbo.replace(render_template('captionsPane.html'), 'load'))


if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0")
