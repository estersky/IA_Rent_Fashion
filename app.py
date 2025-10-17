from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html') 

@app.route('/koleksi')
def koleksi():
    return render_template('koleksi.html')

@app.route('/index')
def beranda():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
