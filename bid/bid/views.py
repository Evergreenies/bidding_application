from logging import error
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from bid import app, bcrypt, db, mail
from bid.models import User, Product, Bidder
from bid.utilities.utilities import save_picture
from bid.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, AddProductForm, ApplyBid


@app.route('/', methods=['GET', 'POST'])
def home():
    products = []
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        products = Product.query \
            .filter(Product.last_date_to_bid >= (datetime.now().replace(microsecond=0) + timedelta(days=-1))) \
            .order_by(Product.post_created.desc()) \
            .paginate(page=page, per_page=5)

        for prod in products.items:
            if prod.bids:
                prod.bids.bid_value = max(item.bid_value for item in prod.bids)

    return render_template('home.html', products=products)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    User registration
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log-in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


# @app.route(''/'')?
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User authentication
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please, check email or password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def send_reset_email(user):
    """
    Send mail to reset password
    :param user:
    :return:
    """
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """
    Reset password request
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """
    Reset password. After click on link received in mail user will hit this api url.
    :param token:
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You are now able to log-in.', 'success')
        return redirect(url_for('home'))

    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def add_product():
    """
    Add new product by current user
    :return:
    """
    try:

        form = AddProductForm()
        if request.method == 'POST':

            if form.validate_on_submit():

                product_image = ''
                if form.picture.data:
                    product_image = save_picture(form.picture.data)

                current_user_id = User.query.filter(
                    User.email == current_user.email,
                    User.username == current_user.username
                ).first()

                if not current_user_id.id:
                    logout_user()
                    return redirect(url_for('home'))

                new_product = Product(
                    user_id=current_user_id.id,
                    product_name=form.product_name.data,
                    product_description=form.product_description.data,
                    category=form.category.data,
                    minimum_bid=form.minimum_bid.data,
                    last_date_to_bid=form.last_date_to_bid.data,
                    picture=product_image
                )

                db.session.add(new_product)
                db.session.commit()
                flash('Product has been added!', 'success')
            else:
                flash('Please, insert correct values!', 'warning')
                return render_template('add_products.html', title='Add Product', form=form)

        elif request.method == 'GET':
            return render_template('add_products.html', title='Add Product', form=form, legend='Add Product')

    except Exception as e:
        error(str(e), exc_info=True)

    return redirect(url_for('home'))


@app.route('/product/<int:product_id>')
@login_required
def product(product_id):
    """
    View individual product details
    :param product_id:
    :return:
    """
    my_product = Product.query.get_or_404(product_id)

    if my_product.bids:
        my_product.bids.bid_value = max(item.bid_value for item in my_product.bids)

    return render_template('product.html', title=my_product.product_name, my_product=my_product)


@app.route('/product/<int:product_id>/update', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    """
    Update product details posted by current user
    :param product_id:
    :return:
    """
    my_product = Product.query.get_or_404(product_id)
    form = AddProductForm()

    try:
        if my_product.owner != current_user:
            abort(403)

        if request.method == 'POST':
            if form.validate_on_submit():

                product_image = ''
                if form.picture.data:
                    product_image = save_picture(form.picture.data)

                my_product.product_name = form.product_name.data
                my_product.product_description = form.product_description.data
                my_product.category = form.category.data
                my_product.minimum_bid = form.minimum_bid.data
                my_product.last_date_to_bid = form.last_date_to_bid.data
                my_product.picture = product_image
                my_product.last_updated = datetime.now().replace(microsecond=0)

                db.session.commit()
                flash('Product details has been updated!', 'success')
                return redirect(url_for('product', product_id=my_product.id))

            else:
                flash('Please, insert correct values!', 'warning')

        elif request.method == 'GET':
            form.product_name.data = my_product.product_name
            form.product_description.data = my_product.product_description
            form.category.data = my_product.category
            form.minimum_bid.data = my_product.minimum_bid
            form.last_date_to_bid.data = my_product.last_date_to_bid
            form.picture.data = my_product.picture

    except Exception as e:
        error(str(e), exc_info=True)

    return render_template('add_products.html', title='Update Product', form=form, legend='Update Product')


@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """
    Delete product posted by current user
    :param product_id:
    :return:
    """
    try:
        my_product = Product.query.get_or_404(product_id)

        if my_product.owner != current_user:
            abort(403)

        if my_product:
            Bidder.query.filter(Bidder.product_id == product_id).delete()
            Product.query.filter(Product.id == product_id).delete()
            db.session.commit()
            flash('Your product has been deleted!', 'success')

        else:
            flash('Product does not exist!', 'error')

    except Exception as e:
        error(str(e), exc_info=True)

    return redirect(url_for('home'))


@app.route("/user/<string:username>")
@login_required
def user_product(username):
    """
    View all products of selected user profile
    :param username:
    :return:
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    products = Product.query.filter_by(owner=user) \
        .order_by(Product.post_created.desc()) \
        .paginate(page=page, per_page=5)

    for prod in products.items:
        if prod.bids:
            prod.bids.bid_value = max(item.bid_value for item in prod.bids)

    return render_template('user_products.html', products=products, user=user)


@app.route('/bid/product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def bid_product(product_id):
    """
    Apply bidding aon any selected product
    :param product_id:
    :return:
    """
    form = ApplyBid()
    try:
        my_product = Product.query.get_or_404(product_id)
        update_bidding = Bidder.query \
            .filter(Bidder.bidders_id == current_user.id, Bidder.product_id == product_id) \
            .first()

        if request.method == 'GET':
            if update_bidding:
                flash('Seems previously you bid on this product!', 'info')
                form.bid_value.data = update_bidding.bid_value
                form.note.data = update_bidding.note

        if request.method == 'POST':
            if form.validate_on_submit():

                if int(form.bid_value.data) <= int(my_product.minimum_bid):
                    flash('Bidding value must be greater that minimum bidding value!', 'warning')
                    return render_template('apply_bid.html', form=form, legend='Apply Bidding')

                try:
                    if update_bidding:
                        update_bidding.bidders_id = current_user.id
                        update_bidding.product_id = product_id
                        update_bidding.bid_value = form.bid_value.data
                        update_bidding.note = form.note.data

                    else:
                        query_result = Bidder(
                            bidders_id=current_user.id,
                            product_id=product_id,
                            bid_value=form.bid_value.data,
                            note=form.note.data
                        )

                        db.session.add(query_result)
                    db.session.commit()
                except Exception as e:
                    flash('Incorrect values!', 'warning')
                    error(str(e), exc_info=True)
                    return render_template('apply_bid.html', form=form, legend='Apply Bidding')

                flash('Bidding applied!', 'success')
                return redirect(url_for('home'))

            else:
                flash('Please, fill fields correctly!', 'warning')

    except Exception as e:
        error(str(e), exc_info=True)

    return render_template('apply_bid.html', form=form, legend='Apply Bidding')
