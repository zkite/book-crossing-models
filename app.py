import time

from flask  import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from entity import users, books


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


userRequests = db.Table('userRequests', db.Model.metadata,
	db.Column('user_id', db.ForeignKey('users.id'), nullable=False),
	db.Column('request_id', db.ForeignKey('requests.id'), nullable=False)
)


class User(db.Model):
	__tablename__ = 'users'

	id = db.Column('id', db.Integer, primary_key=True)
	login = db.Column('login', db.String)
	password = db.Column('password', db.String)
	email = db.Column('email', db.String)
	first_name = db.Column('first_name', db.String)
	last_name = db.Column('last_name', db.String)
	office = db.Column('office', db.String)
	phone_number = db.Column('phone_number', db.String)
	limit = db.Column('limit', db.Integer)
	points = db.Column('points', db.Integer)

	#user-books One to Many
	books = db.relationship('Book', back_populates='owner')

	#users (two) to requests Many to Many
	requests = db.relationship('BookRequest', secondary=userRequests, back_populates='users')

	def __init__(self, login, password, email, first_name, last_name, office, phone_number):
		self.login = login
		self.password = password
		self.email = email
		self.first_name = first_name
		self.last_name = last_name
		self.office = office
		self.phone_number = phone_number


class Book(db.Model):
	__tablename__ = 'books'

	id = db.Column('id', db.Integer, primary_key=True)
	title = db.Column('title', db.String)
	author = db.Column('author', db.String)
	publisher = db.Column('publisher', db.String)
	category = db.Column('category', db.String)

	#books to owner Many to One
	owner_id = db.Column('owner_id', db.Integer, db.ForeignKey('users.id'))
	owner = db.relationship('User', back_populates='books')

	#book to requests One to Many
	requests = db.relationship('BookRequest', back_populates='book')

	def __init__(self, title, author, publisher, category):
		self.title = title
		self.author = author
		self.publisher = publisher
		self.category = category


class BookRequest(db.Model):
	__tablename__ = 'requests'

	id = db.Column('id', db.Integer, primary_key=True)
	request_date = db.Column('request_date', db.DateTime)
	accept_date = db.Column('accept_date', db.DateTime)
	notification = db.Column('notification', db.VARCHAR)

	#requests to users(two) Many to Many
	users = db.relationship('User', secondary=userRequests, back_populates='requests')

	#requests to book Many to One
	book_id = db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
	book = db.relationship('Book', back_populates='requests')

	def __init__(self, request_date=datetime.utcnow(), accept_date=None):
		self.request_date = request_date
		self.accept_date = accept_date


# create tables
db.create_all()


#create users
owner = User(**users['0'])
requester = User(**users['1'])

#create book
hpotter = Book(**books['0'])

#add book to owners shelf
owner.books.append(hpotter)

#requester creates request for owners book
book_request = BookRequest()
requester.requests.append(book_request)
owner.books[0].requests.append(requester.requests[0])

#make some delay
time.sleep(3)

#owner can accept/decline requester request
#requester.requests[0].accept_date=datetime.utcnow()
#owner.requests.append(requester.requests[0])

db.session.add(owner)
db.session.add(requester)
db.session.commit()


print('owner --> ', owner)
print('requester --> ', requester)
print('--------------------------------------------')
print('owners bookshelf --> ', owner.books)
print('owners bookshelf --> ', owner.books[0].title)
print('--------------------------------------------')
print('request date --> ', book_request.request_date)
print('participants in request --> ', book_request.users)
print('participant #0 (requester) --> ', book_request.users[0].login)
print('participant #1 (owner) --> ', None) #book_request.users[1].login)
print('requested book --> ', book_request.book.title)
print('books owner -->', book_request.book.owner.login)
print('--------------------------------------------')
print('owner requests --> ', owner.requests)
print('requester requests --> ', requester.requests)
print('--------------------------------------------')
print('request date --> ', owner.requests) #[0].request_date) #)
print('accept date --> ',  requester.requests[0].accept_date)


if __name__ == '__main__':
	app.run()