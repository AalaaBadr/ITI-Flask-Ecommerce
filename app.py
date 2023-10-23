import os
from flask import Flask
from flask import request, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = '1'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)  # this will create instance folder --> contains db


# define db models
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String, nullable=True)
    instock = db.Column(db.Boolean)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), onupdate=func.now())


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/not_found.html', error=error)


@app.route("/", endpoint='home')
def home():
    return render_template('layouts/index.html')


@app.route('/products', endpoint='products')
def products():
    products = Product.query.all()
    return render_template('product/products.html', products=products)


@app.route('/product/<int:id>', endpoint='product')
def product(id):
    product = Product.query.get_or_404(id)
    return render_template('product/product.html', product=product)


@app.route('/product/add', methods=['GET', 'POST'], endpoint='add')
def create():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product = Product(name=request.form['name'], image=filename, price=request.form['price'],
                              desc=request.form['desc'], instock=bool(request.form['instock']))
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('products'))

    return render_template('product/add.html')


@app.route('/product/update/<int:id>', methods=['GET', 'POST'], endpoint='update')
def update(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product.name = request.form['name']
            product.price = request.form['price']
            product.image = filename
            product.desc = request.form['desc']
            product.instock = bool(request.form['instock'])

            db.session.commit()
            return redirect(url_for('product',id=product.id))

    return render_template('product/update.html', product=product)


@app.route('/product/delete/<int:id>', endpoint='delete')
def delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))
