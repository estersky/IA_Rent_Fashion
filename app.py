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

# @app.route('/koleksi/<kategori>')
# def koleksi_kategori(kategori):
#     return render_template('koleksi.html', kategori=kategori)

@app.route('/index')
def beranda():
    return render_template('index.html')

@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

@app.route('/inspirasi')
def inspirasi():
    return render_template('inspirasi.html')
if __name__ == '__main__':
    app.run(debug=True)
