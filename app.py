from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Data Produk Lengkap
PRODUCTS = {
    1: {'id': 1, 'name': 'Jas Hitam Klasik', 'price': 120000, 'original_price': 140000, 'image': 'static/images/jas1.jpg', 'category': 'Jas', 'description': 'Jas klasik berwarna hitam dengan potongan sempurna untuk acara formal. Bahan premium berkualitas tinggi dengan jahitan rapi.'},
    2: {'id': 2, 'name': 'Jas Silver Elegan', 'price': 150000, 'original_price': 175000, 'image': 'static/images/jas2.jpg', 'category': 'Jas', 'description': 'Jas warna silver dengan desain elegan untuk acara istimewa. Cocok untuk pernikahan dan acara formal lainnya.'},
    3: {'id': 3, 'name': 'Jas Slim Fit Formal', 'price': 150000, 'original_price': 170000, 'image': 'static/images/jas3.jpg', 'category': 'Jas', 'description': 'Jas slim fit dengan potongan modern dan elegan. Desain kontemporer cocok untuk acara modern.'},
    4: {'id': 4, 'name': 'Blazer Wanita Abu-Abu', 'price': 150000, 'original_price': 165000, 'image': 'static/images/jas4.jpg', 'category': 'Jas', 'description': 'Blazer wanita warna abu-abu dengan desain modern dan elegan. Pas untuk acara bisnis dan formal.'},
    5: {'id': 5, 'name': 'Dress Satin Lavender', 'price': 100000, 'original_price': 125000, 'image': 'static/images/dress1.jpg', 'category': 'Dress', 'description': 'Dress satin berwarna lavender yang elegan dan nyaman. Sempurna untuk acara malam yang istimewa.'},
    6: {'id': 6, 'name': 'Dress Pesta Ungu', 'price': 120000, 'original_price': 145000, 'image': 'static/images/dress1.jpg', 'category': 'Dress', 'description': 'Dress pesta berwarna ungu dengan detail yang mewah. Cocok untuk acara pesta dan perayaan.'},
    7: {'id': 7, 'name': 'Dress Brokat Abu Muda', 'price': 150000, 'original_price': 170000, 'image': 'static/images/dress2.jpg', 'category': 'Dress', 'description': 'Dress brokat abu muda dengan desain mewah. Sempurna untuk acara formal dan pernikahan.'},
    8: {'id': 8, 'name': 'Dress Maroon Elegant', 'price': 130000, 'original_price': 155000, 'image': 'static/images/dress3.jpg', 'category': 'Dress', 'description': 'Dress maroon dengan desain elegan dan mewah. Sangat cocok untuk acara formal dan spesial.'},
    9: {'id': 9, 'name': 'Kacamata Hitam Fashion', 'price': 70000, 'original_price': 90000, 'image': 'static/images/akse1.jpg', 'category': 'Aksesoris', 'description': 'Kacamata hitam fashion dengan desain trendy. Pelengkap sempurna untuk penampilan Anda.'},
    10: {'id': 10, 'name': 'Tas Selempang Merah Muda', 'price': 60000, 'original_price': 80000, 'image': 'static/images/akse2.jpg', 'category': 'Aksesoris', 'description': 'Tas selempang merah muda dengan desain modern. Cocok untuk berbagai acara.'},
    11: {'id': 11, 'name': 'Ikat Pinggang Coklat Bohemian', 'price': 50000, 'original_price': 70000, 'image': 'static/images/akse3.jpg', 'category': 'Aksesoris', 'description': 'Ikat pinggang coklat dengan desain bohemian yang unik dan stylish.'},
    12: {'id': 12, 'name': 'Set Kalung & Anting Silver', 'price': 80000, 'original_price': 100000, 'image': 'static/images/akse4.jpg', 'category': 'Aksesoris', 'description': 'Set kalung dan anting silver yang elegan untuk melengkapi penampilan Anda.'},
    13: {'id': 13, 'name': 'Kebaya Pink Brokat Modern', 'price': 120000, 'original_price': 145000, 'image': 'static/images/kebaya1.jpg', 'category': 'Kebaya', 'description': 'Kebaya pink dengan brokat modern yang elegan. Cocok untuk acara pernikahan dan pesta.'},
    14: {'id': 14, 'name': 'Kebaya Biru Dongker Premium', 'price': 130000, 'original_price': 155000, 'image': 'static/images/kebaya2.jpg', 'category': 'Kebaya', 'description': 'Kebaya biru dongker premium dengan desain elegan dan mewah.'},
    15: {'id': 15, 'name': 'Kebaya Navy Brokat Tile', 'price': 150000, 'original_price': 175000, 'image': 'static/images/kebaya3.jpg', 'category': 'Kebaya', 'description': 'Kebaya navy dengan brokat tile yang indah. Sempurna untuk acara formal tradisional.'},
    16: {'id': 16, 'name': 'Kebaya Pastel Glamour', 'price': 140000, 'original_price': 160000, 'image': 'static/images/kebaya4.jpg', 'category': 'Kebaya', 'description': 'Kebaya pastel dengan desain glamour yang menawan. Cocok untuk berbagai acara spesial.'},
    17: {'id': 17, 'name': 'Sepatu Pantofel Hitam Klasik', 'price': 130000, 'original_price': 155000, 'image': 'static/images/pentopel1.jpg', 'category': 'Footwear', 'description': 'Sepatu pantofel hitam klasik dengan desain formal yang sempurna untuk acara resmi.'},
    18: {'id': 18, 'name': 'Sepatu Formal Pria Premium', 'price': 100000, 'original_price': 125000, 'image': 'static/images/pentopel2.jpg', 'category': 'Footwear', 'description': 'Sepatu formal pria premium dengan kualitas terbaik untuk penampilan yang sempurna.'},
    19: {'id': 19, 'name': 'Sepatu Kulit Hitam Elegan', 'price': 100000, 'original_price': 130000, 'image': 'static/images/pentopel3.jpg', 'category': 'Footwear', 'description': 'Sepatu kulit hitam elegan dengan design klasik yang cocok untuk berbagai acara formal.'},
    20: {'id': 20, 'name': 'Sepatu Oxford Modern', 'price': 90000, 'original_price': 115000, 'image': 'static/images/pentopel4.jpg', 'category': 'Footwear', 'description': 'Sepatu oxford modern dengan desain contemporary yang stylish dan nyaman.'},
}

# ===== ROUTES =====

@app.route('/')
@app.route('/index')
def beranda():
    """Halaman beranda"""
    return render_template('index.html')

@app.route('/contact')
def contact():
    """Halaman kontak"""
    return render_template('contact.html')

@app.route('/koleksi')
def koleksi():
    """Halaman koleksi produk"""
    return render_template('koleksi.html')

@app.route('/detail/<int:product_id>')
def detail(product_id):
    """Halaman detail produk"""
    product = PRODUCTS.get(product_id)
    
    if not product:
        return "Produk tidak ditemukan", 404
    
    return render_template('detail.html', product=product)

@app.route('/tentang')
def tentang():
    """Halaman tentang"""
    return render_template('tentang.html')

@app.route('/inspirasi')
def inspirasi():
    """Halaman inspirasi"""
    return render_template('inspirasi.html')

@app.route('/review')
def review():
    """Halaman review"""
    return render_template('review.html')

# ===== API ROUTES =====

@app.route('/api/products')
def api_products():
    """API untuk mendapatkan semua produk"""
    return jsonify(PRODUCTS)

@app.route('/api/products/<int:product_id>')
def api_product(product_id):
    """API untuk mendapatkan produk spesifik"""
    product = PRODUCTS.get(product_id)
    
    if not product:
        return jsonify({'error': 'Produk tidak ditemukan'}), 404
    
    return jsonify(product)

if __name__ == '__main__':
    app.run(debug=True)