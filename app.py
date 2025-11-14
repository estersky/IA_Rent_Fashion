from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from flask import g
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# ===== DATABASE CONFIGURATION =====
DATABASE = 'fashion_rental.db'

def get_db():
    """Membuat koneksi ke database"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Inisialisasi database"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    db.commit()
    db.close()
    print("✅ Database initialized!")

def login_required(f):
    """Decorator untuk melindungi halaman yang memerlukan login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== DATA PRODUK =====
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

# ===== AUTHENTICATION ROUTES =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Route untuk registrasi user baru"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms')
        
        # Validasi
        if not all([name, email, phone, password, confirm_password]):
            flash('❌ Semua field harus diisi', 'error')
            return redirect(url_for('register'))
        
        if len(name) < 3:
            flash('❌ Nama minimal 3 karakter', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('❌ Kata sandi minimal 8 karakter', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('❌ Kata sandi tidak cocok', 'error')
            return redirect(url_for('register'))
        
        if not terms:
            flash('❌ Anda harus menyetujui Syarat & Ketentuan', 'error')
            return redirect(url_for('register'))
        
        try:
            db = get_db()
            cursor = db.cursor()
            hashed_password = generate_password_hash(password)
            
            cursor.execute('''
                INSERT INTO users (name, email, phone, password)
                VALUES (?, ?, ?, ?)
            ''', (name, email, phone, hashed_password))
            
            db.commit()
            db.close()
            
            flash('✅ Registrasi berhasil! Silakan login', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('❌ Email sudah terdaftar!', 'error')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route untuk login user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')
        
        if not email or not password:
            flash('❌ Email dan kata sandi harus diisi', 'error')
            return redirect(url_for('login'))
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                session['show_welcome'] = True
                
                if remember:
                    session.permanent = True
                    app.permanent_session_lifetime = 2592000
                
                cursor.execute('''
                    INSERT INTO login_history (user_id, ip_address)
                    VALUES (?, ?)
                ''', (user['id'], request.remote_addr))
                db.commit()
                
                flash(f'✅ Selamat datang, {user["name"]}!', 'success')
                db.close()
                return redirect(url_for('beranda'))
            else:
                flash('❌ Email atau kata sandi salah', 'error')
                db.close()
                return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Route untuk logout"""
    session.clear()
    flash('✅ Anda telah logout. Silakan login kembali untuk melakukan transaksi.', 'info')
    return redirect(url_for('beranda'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Route untuk forgot password"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('❌ Silakan masukkan email Anda', 'error')
            return redirect(url_for('forgot_password'))
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            db.close()
            
            flash('✅ Jika email terdaftar, kami akan mengirim link reset', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
            return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

@app.route('/profile')
@login_required
def profile():
    """Route untuk profile user yang sudah login"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        db.close()
        
        if user:
            return render_template('profile.html', user=user)
        else:
            return redirect(url_for('logout'))
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'error')
        return redirect(url_for('beranda'))

# ===== MAIN ROUTES =====

@app.before_request
def before_request():
    """Pass session ke semua template"""
    from flask import g
    g.user = None
    if 'user_id' in session:
        g.user = {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }

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

@app.route('/jas')
def jas():
    return render_template('jas.html')

@app.route('/dress')
def dress():
    return render_template('dress.html')

@app.route('/aksesoris')
def aksesoris():
    return render_template('aksesoris.html')

@app.route('/kebaya')
def kebaya():
    return render_template('kebaya.html')

@app.route('/footwear')
def footwear():
    return render_template('footwear.html')

@app.route('/sewa')
def sewa():
    return render_template('sewa.html')


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

@app.route('/checkout')
@login_required
def checkout():
    """Halaman checkout - hanya untuk user yang login"""
    return render_template('checkout.html')

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

# 👇👇👇 TAMBAHKAN KODE BARU DI SINI 👇👇👇

# ===== SHOPPING CART API ROUTES =====

@app.route('/cart')
@login_required
def cart():
    """Halaman keranjang - hanya untuk user yang login"""
    return render_template('cart.html')

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """API untuk menambahkan produk ke keranjang"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Validasi produk exists
        if product_id not in PRODUCTS:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan'}), 404
        
        # Logic untuk menyimpan ke session
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({
            'success': True, 
            'message': 'Produk berhasil ditambahkan ke keranjang',
            'cart_count': sum(cart.values())
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cart')
@login_required
def get_cart():
    """API untuk mendapatkan isi keranjang"""
    try:
        cart = session.get('cart', {})
        cart_items = []
        
        for product_id_str, quantity in cart.items():
            product_id = int(product_id_str)
            if product_id in PRODUCTS:
                product = PRODUCTS[product_id].copy()
                product['quantity'] = quantity
                cart_items.append(product)
        
        return jsonify({
            'success': True,
            'items': cart_items,
            'count': sum(cart.values())
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cart/count')
def get_cart_count():
    """API untuk mendapatkan jumlah item di keranjang"""
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    cart = session.get('cart', {})
    return jsonify({'count': sum(cart.values())})

@app.route('/api/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    """API untuk menghapus produk dari keranjang"""
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        
        if 'cart' in session and product_id in session['cart']:
            del session['cart'][product_id]
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': 'Produk berhasil dihapus dari keranjang'
            })
        
        return jsonify({'success': False, 'message': 'Produk tidak ada di keranjang'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== WISHLIST API ROUTES =====

@app.route('/wishlist')
@login_required
def wishlist():
    """Halaman wishlist - hanya untuk user yang login"""
    return render_template('wishlist.html')

@app.route('/api/wishlist/add', methods=['POST'])
@login_required
def add_to_wishlist():
    """API untuk menambahkan produk ke wishlist"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        # Validasi produk exists
        if product_id not in PRODUCTS:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan'}), 404
        
        # Logic untuk menyimpan ke session
        if 'wishlist' not in session:
            session['wishlist'] = []
        
        wishlist = session['wishlist']
        
        if product_id in wishlist:
            return jsonify({
                'success': False,
                'message': 'Produk sudah ada di wishlist'
            }), 400
        
        wishlist.append(product_id)
        session['wishlist'] = wishlist
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Produk berhasil ditambahkan ke wishlist',
            'wishlist_count': len(wishlist)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wishlist/remove', methods=['POST'])
@login_required
def remove_from_wishlist():
    """API untuk menghapus produk dari wishlist"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if 'wishlist' in session and product_id in session['wishlist']:
            session['wishlist'].remove(product_id)
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': 'Produk berhasil dihapus dari wishlist'
            })
        
        return jsonify({'success': False, 'message': 'Produk tidak ada di wishlist'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== REVIEW API ROUTES =====

@app.route('/api/review/add', methods=['POST'])
@login_required
def add_review():
    """API untuk menambahkan review produk"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment', '').strip()
        
        # Validasi
        if not product_id or not rating:
            return jsonify({'success': False, 'message': 'Data tidak lengkap'}), 400
        
        if product_id not in PRODUCTS:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan'}), 404
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Rating harus antara 1-5'}), 400
        
        # TODO: Simpan review ke database
        
        return jsonify({
            'success': True,
            'message': 'Review berhasil ditambahkan',
            'data': {
                'user_name': session.get('user_name'),
                'rating': rating,
                'comment': comment,
                'created_at': 'Just now'
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 👆👆👆 SAMPAI SINI 👆👆👆

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

@app.before_request
def before_request():
    """Jalankan sebelum setiap request"""
    # Pastikan database sudah terinisialisasi
    if not os.path.exists(DATABASE):
        init_db()

if __name__ == '__main__':
    # Inisialisasi database saat startup
    print("🔄 Menginisialisasi database...")
    if not os.path.exists(DATABASE):
        init_db()
    else:
        # Double check - pastikan tabel ada meskipun file sudah ada
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("⚠️  Tabel users tidak ditemukan, membuat ulang...")
                init_db()
            db.close()
        except Exception as e:
            print(f"❌ Error checking tables: {e}")
    
    print("✅ Database ready!")
    print("🚀 Server running on http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)
    
    
if __name__ == '__main__':
    app.run(debug=True)