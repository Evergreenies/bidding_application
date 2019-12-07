from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey, inspect, String, BigInteger, DECIMAL
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from bid import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    User model for authentication and authorization.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship('Product', backref='owner', lazy=True)

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception as e:
            print(e)
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.id})"

    @staticmethod
    def object_as_dict(obj):
        """
        Inspect model object and return it as dictionary.
        :param obj: list of dicts
        :return:
        """

        resultant_list = list()

        if isinstance(obj, list):
            for row in obj:
                if row:
                    resultant_list.append(
                        dict(map(lambda c: (c.key, getattr(row, c.key)), inspect(row).mapper.column_attrs))
                    )
        elif obj:
            resultant_list.append(dict(map(lambda c: (c.key, getattr(obj, c.key)), inspect(obj).mapper.column_attrs)))

        return resultant_list


class Product(db.Model):
    """
    Model to add product for current user
    """
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    product_name = Column(String(100), nullable=False)
    product_description = Column(String(550))
    category = Column(String(50), nullable=False)
    minimum_bid = Column(BigInteger, nullable=False)
    post_created = Column(DateTime, default=datetime.now().replace(microsecond=0))
    last_updated = Column(DateTime, default=datetime.now().replace(microsecond=0))
    last_date_to_bid = Column(DateTime, default=datetime.now().replace(microsecond=0))
    bids = db.relationship('Bidder', backref='product', lazy=True, cascade='all,delete,delete-orphan')
    picture = Column(String(1600), nullable=False, default='default.png')

    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.product_name = kwargs.get('product_name')
        self.product_description = kwargs.get('product_description')
        self.category = kwargs.get('category')
        self.minimum_bid = kwargs.get('minimum_bid')
        self.last_updated = kwargs.get('last_updated', datetime.now().replace(microsecond=0))
        self.last_date_to_bid = kwargs.get('last_date_to_bid')
        self.picture = kwargs.get('picture')

    @staticmethod
    def object_as_dict(obj):
        """
        Inspect model object and return it as dictionary.
        :param obj: list of dicts
        :return:
        """

        resultant_list = list()

        if isinstance(obj, list):
            for row in obj:
                if row:
                    resultant_list.append(
                        dict(map(lambda c: (c.key, getattr(row, c.key)), inspect(row).mapper.column_attrs))
                    )
        elif obj:
            resultant_list.append(dict(map(lambda c: (c.key, getattr(obj, c.key)), inspect(obj).mapper.column_attrs)))

        return resultant_list


class Bidder(db.Model):
    """
    Model to apply bidding on product by current user
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    bidders_id = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    bid_value = Column(DECIMAL, nullable=False, default=0)
    note = Column(String(500))

    def __init__(self, **kwargs):
        self.bidders_id = kwargs.get('bidders_id')
        self.product_id = kwargs.get('product_id')
        self.bid_value = kwargs.get('bid_value')
        self.note = kwargs.get('note')
