from flask import Flask, render_template, request, redirect, url_for
from models import db, Category, Product
from config import Config
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

def save_image(file):
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return path
    return None

@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/category/<int:id>')
def view_category(id):
    category = Category.query.get_or_404(id)
    return render_template('category.html', category=category)

@app.route('/product/<int:id>', methods=['GET', 'POST'])
def view_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        action = request.form['action']
        amount = int(request.form['amount'])
        if action == 'add':
            product.quantity += amount
        elif action == 'remove':
            product.quantity = max(0, product.quantity - amount)
        db.session.commit()
        return redirect(url_for('view_product', id=id))
    return render_template('product.html', product=product)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        image = save_image(request.files['image'])
        category = Category(name=name, image=image)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_category.html')

@app.route('/add_product/<int:category_id>', methods=['GET', 'POST'])
def add_product(category_id):
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        image = save_image(request.files['image'])
        product = Product(name=name, quantity=quantity, image=image, category_id=category_id)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('view_category', id=category_id))
    return render_template('add_product.html', category_id=category_id)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    category_id = product.category_id
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('view_category', id=category_id))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = int(request.form['quantity'])
        product.category_id = int(request.form['category_id'])
        
        # Si quieres permitir cambiar la imagen:
        image = save_image(request.files.get('image'))
        if image:
            product.image = image
        
        db.session.commit()
        return redirect(url_for('view_product', id=product.id))
    return render_template('edit_product.html', product=product)

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        
        image = save_image(request.files.get('image'))
        if image:
            category.image = image
        
        db.session.commit()
        return redirect(url_for('view_category', id=category.id))
    
    return render_template('edit_category.html', category=category)

if __name__ == '__main__':
    app.run(debug=True)
