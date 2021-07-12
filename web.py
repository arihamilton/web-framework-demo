from flask import Flask, render_template, url_for
app = Flask(__name__)                    # this gets the name of the file so Flask knows it's name

@app.route("/")                       # this tells you the URL the method below is related to
@app.route("/home")  
def hello_world():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')

@app.route("/about")                          # this tells you the URL the method below is related to
def about():
    return render_template('about.html', subtitle='Home Page', subtitle2='About Page', text='This is the about page!')
  
if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0")
