import os
from datetime import timedelta
from functools import wraps # Diperlukan untuk decorator admin
from flask import (
    Flask, render_template, jsonify, request, session, 
    redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user, 
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# ==============================================================================
# KONFIGURASI APLIKASI
# ==============================================================================
app = Flask(__name__)

# --- Konfigurasi Penting ---
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "kunci_rahasia_yang_sangat_aman_dan_sulit_ditebak")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iarentfashion.db'
app.config['SQLALCHEMY_TRACK_MODIFIKATIONS'] = False

# --- Inisialisasi Ekstensi ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Halaman yang dituju jika user belum login
login_manager.login_message = 'Anda harus login untuk mengakses halaman ini.'
login_manager.login_message_category = 'danger' # Kategori flash message (Bootstrap)


# ==============================================================================
# MODEL DATABASE (PENGGANTI 'PRODUCTS' DICT)
# ==============================================================================

# Model untuk User (terintegrasi dengan Flask-Login)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Model untuk Produk
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer)
    image = db.Column(db.String(200)) # Simpan path ke gambar
    category = db.Column(db.String(100))
    description = db.Column(db.Text)

# Model untuk Pesan Kontak
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

# Model untuk Review
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Nama dari form
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    # Anda bisa tambahkan user_id jika review hanya untuk user yg login
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

# Model untuk Pesanan (Order)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending') # Misal: Pending, Disewa, Selesai
    order_date = db.Column(db.DateTime, default=db.func.now())
    
    # Relasi ke User
    customer = db.relationship('User', backref=db.backref('orders', lazy=True))

# ==============================================================================
# HELPER (FLASK-LOGIN & DECORATOR)
# ==============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Mengambil user dari database untuk session management"""
    return db.session.get(User, int(user_id))

def admin_required(f):
    """Decorator untuk membatasi akses hanya untuk admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        if not current_user.is_admin:
            flash('Halaman ini hanya bisa diakses oleh Admin.', 'danger')
            return redirect(url_for('beranda'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# RUTE SITUS PUBLIK (DARI KODE ANDA, DIMODIFIKASI UNTUK DB)
# ==============================================================================

@app.route('/')
def beranda():
    """Halaman beranda"""
    # (wishlist_count & cart_count sekarang di-handle oleh context processor)
    return render_template('index.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Halaman kontak, sekarang bisa menyimpan pesan"""
    if request.method == 'POST':
        try:
            new_message = ContactMessage(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                subject=request.form.get('subject'),
                message=request.form.get('message')
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Pesan Anda telah berhasil terkirim!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat mengirim pesan: {e}', 'danger')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/koleksi')
def koleksi():
    """Halaman koleksi, mengambil produk dari database"""
    all_products = Product.query.all()
    return render_template('koleksi.html', products=all_products)

@app.route('/detail/<int:product_id>')
def detail(product_id):
    """Halaman detail, mengambil produk dari database"""
    # get_or_404 otomatis menampilkan error 404 jika ID tidak ditemukan
    product = db.session.get(Product, product_id)
    if not product:
        flash("Produk tidak ditemukan.", "danger")
        return redirect(url_for('koleksi'))
        
    return render_template('detail.html', product=product)

@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

@app.route('/inspirasi')
def inspirasi():
    return render_template('inspirasi.html')

@app.route('/review', methods=['GET', 'POST'])
def review():
    """Halaman review, sekarang bisa menyimpan review"""
    if request.method == 'POST':
        try:
            new_review = Review(
                name=request.form.get('name'),
                rating=int(request.form.get('rating')),
                comment=request.form.get('comment')
            )
            db.session.add(new_review)
            db.session.commit()
            flash('Review Anda telah berhasil dikirim!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat mengirim review: {e}', 'danger')
        return redirect(url_for('review'))

    # Ambil semua review dari DB untuk ditampilkan
    all_reviews = Review.query.order_by(Review.timestamp.desc()).all()
    return render_template('review.html', reviews=all_reviews)

@app.route('/sewa')
def sewa():
    """Halaman penyewaan/keranjang"""
    product_id = request.args.get('product_id', type=int)
    cart = session.get('cart', [])
    
    if product_id:
        product = db.session.get(Product, product_id)
        if product and product_id not in cart:
            cart.append(product_id)
            session['cart'] = cart
            flash(f"'{product.name}' ditambahkan ke keranjang!", 'success')
            
    # Ambil detail produk dari DB berdasarkan ID di session
    rental_items = []
    total_price = 0
    if cart:
        # Query semua produk yang ID-nya ada di list 'cart'
        rental_items = Product.query.filter(Product.id.in_(cart)).all()
        total_price = sum(item.price for item in rental_items)

    if not rental_items and not product_id:
        flash('Keranjang Anda kosong.', 'info')
        return redirect(url_for('koleksi')) 

    return render_template('sewa.html', 
                           rental_items=rental_items, 
                           total_price=total_price)

# ==============================================================================
# RUTE OTENTIKASI (LOGIN, REGISTER, LOGOUT)
# ==============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('beranda'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Login berhasil! Selamat datang kembali.', 'success')
            
            # Jika user adalah admin, arahkan ke dashboard admin
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            
            # Jika bukan, arahkan ke halaman 'next' atau beranda
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('beranda'))
        else:
            flash('Login gagal. Periksa kembali email dan password Anda.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('beranda'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Cek jika email sudah terdaftar
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email ini sudah terdaftar. Silakan login.', 'warning')
            return redirect(url_for('login'))
            
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('beranda'))

# ==============================================================================
# RUTE ADMIN (BARU)
# ==============================================================================

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Menampilkan dashboard admin yang dinamis"""
    # Ambil data statistik dari database
    total_pesanan = Order.query.count()
    total_pelanggan = User.query.filter_by(is_admin=False).count()
    total_produk = Product.query.count()
    
    # Ambil 5 pesanan terbaru (contoh)
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    # Siapkan data pesanan terbaru untuk ditampilkan (lebih kompleks di dunia nyata)
    recent_orders_data = []
    for order in recent_orders:
        recent_orders_data.append({
            'customer_name': order.customer.name,
            'product_name': f"Order #{order.id}", # Placeholder, Anda perlu order_items
            'status': order.status,
            'date': order.order_date
        })

    return render_template(
        'admin/dashboard.html',
        total_pesanan=total_pesanan,
        total_pelanggan=total_pelanggan,
        total_produk=total_produk,
        total_pendapatan="Rp 0", # Placeholder, perlu kalkulasi
        recent_orders=recent_orders_data
    )

@app.route('/admin/products')
@admin_required
def admin_products():
    """Halaman untuk melihat semua produk (Contoh)"""
    products = Product.query.all()
    return render_template('admin/products.html', products=products) # Perlu buat template ini

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Halaman untuk melihat semua pesanan (Contoh)"""
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders) # Perlu buat template ini

@app.route('/admin/customers')
@admin_required
def admin_customers():
    """Halaman untuk melihat semua pelanggan (Contoh)"""
    customers = User.query.filter_by(is_admin=False).all()
    return render_template('admin/customers.html', customers=customers) # Perlu buat template ini

@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    """Halaman untuk melihat semua review (Contoh)"""
    reviews = Review.query.all()
    return render_template('admin/reviews.html', reviews=reviews) # Perlu buat template ini

@app.route('/admin/profile')
@admin_required
def admin_profile():
    return render_template('admin/profile.html') # Perlu buat template ini

@app.route('/admin/reports')
@admin_required
def admin_reports():
    return render_template('admin/reports.html') # Perlu buat template ini


# ==============================================================================
# FUNGSI WISHLIST DAN KERANJANG (SESI)
# ==============================================================================

@app.before_request
def make_session_permanent():
    """Memastikan session dibuat permanen sebelum setiap request"""
    session.permanent = True

@app.context_processor
def inject_session_counts():
    """
    Menyuntikkan jumlah item di wishlist dan cart ke semua template.
    Ini membuat 'wishlist_count' dan 'cart_count' tersedia di
    semua file HTML Anda secara otomatis!
    """
    wishlist_count = len(session.get('wishlist', []))
    cart_count = len(session.get('cart', []))
    return dict(wishlist_count=wishlist_count, cart_count=cart_count)

@app.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    data = request.get_json()
    product_id = int(data.get('product_id'))
    
    # Cek ke DB
    if not db.session.get(Product, product_id):
        return jsonify({"success": False, "message": "Produk tidak ditemukan"}), 404

    wishlist = session.get('wishlist', [])
    if product_id not in wishlist:
        wishlist.append(product_id)
        session['wishlist'] = wishlist
        return jsonify({"success": True, "message": "Berhasil ditambahkan ke Wishlist", "count": len(wishlist)})
    
    return jsonify({"success": False, "message": "Sudah ada di Wishlist", "count": len(wishlist)})

# (Anda bisa tambahkan rute lain seperti /remove-from-cart, /remove-from-wishlist, dll.)

# ==============================================================================
# PERINTAH CLI (COMMAND LINE) UNTUK DATABASE
# ==============================================================================

@app.cli.command('init-db')
def init_db_command():
    """Perintah untuk membuat tabel database."""
    with app.app_context():
        db.create_all()
    print('Database telah diinisialisasi.')

@app.cli.command('create-admin')
def create_admin_command():
    """Perintah untuk membuat user admin pertama."""
    try:
        name = input("Masukkan nama admin: ")
        email = input("Masukkan email admin: ")
        password = input("Masukkan password admin: ")
        
        if User.query.filter_by(email=email).first():
            print(f"Error: Email {email} sudah terdaftar.")
            return

        admin_user = User(name=name, email=email, is_admin=True)
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        print(f"User admin '{name}' berhasil dibuat!")
    except Exception as e:
        db.session.rollback()
        print(f"Gagal membuat admin: {e}")

# =Dijalankan saat file dieksekusi langsung=
if __name__ == '__main__':
    app.run(debug=True)