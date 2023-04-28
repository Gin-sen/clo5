from fastapi import FastAPI
import psycopg2
# FIXME replace jsonify -> jsonable_encoder
# FIXME replace request -> BaseModel
from flask import jsonify, request

app = FastAPI()

mydb = psycopg2.connect(
    host="localhost",
    user="Bobby",
    password="BR",
    database="bookingDb"
)

my_cursor = mydb.cursor()


# -------------- Class -------------- #

# User class
class User:
    def __init__(self, firstname, lastname, id, age, phone, password, email, created_date, update_date):
        self.firstname = firstname
        self.lastname = lastname
        self.id = id
        self.age = age
        self.phone = phone
        self.password = password
        self.email = email
        self.created_date = created_date
        self.update_date = update_date


# Booking class
class Booking:
    def __init__(self, id, username, nights, reservation_number, numbers_peoples, users_id, payements_id, created_date,
                 update_date):
        self.id = id
        self.username = username
        self.nights = nights
        self.reservation_number = reservation_number
        self.numbers_peoples = numbers_peoples
        self.users_id = users_id
        self.payements_id = payements_id
        self.created_date = created_date
        self.update_date = update_date


# Payment class
class AdditionalService:
    def __init__(self, id, name, price, bookings_id, bookings_users_id):
        self.id = id
        self.name = name
        self.price = price
        self.bookings_id = bookings_id
        self.bookings_users_id = bookings_users_id


# User class
class Payment:
    def __init__(self, id, price, promo, total, created_date, update_date):
        self.id = id
        self.price = price
        self.promo = promo
        self.total = total
        self.created_date = created_date
        self.update_date = update_date


# -------------- API roots -------------- #

# --- User roots --- #

@app.get('/users')
def get_all_users():
    my_cursor.execute("SELECT * FROM users")
    rows = my_cursor.fetchall()
    users = []
    for row in rows:
        user = User(row[1], row[2], row[0], row[3], row[4], row[5], row[6], row[7], row[8])
        users.append(user.__dict__)
    return jsonify(users)


@app.post('/users')
def add_user():
    data = request.get_json()
    user = User(data['firstname'], data['lastname'], data['id'], data['age'], data['phone'], data['password'],
                data['email'], data['created_date'], data['update_date'])
    postsql = "INSERT INTO users (firstname, lastname, id, age, phone, password, email, created_date, update_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (user.firstname, user.lastname, user.id, user.age, user.phone, user.password, user.email, user.created_date,
           user.update_date)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify(user.__dict__)


@app.get("/users/{id}")
def get_user(id: int):
    postsql = "SELECT * FROM users WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    row = my_cursor.fetchone()
    if row is None:
        return jsonify({'error': 'User not found'}), 404
    user = User(row[1], row[2], row[0], row[3], row[4], row[5], row[6], row[7], row[8])
    return jsonify(user.__dict__)


@app.put('/users/{id}')
def update_user(id: int):
    data = request.get_json()
    postsql = "UPDATE users SET firstname = %s, lastname = %s, age = %s, phone = %s, email = %s, update_date = CURRENT_DATE  WHERE id = %s"
    val = (data['firstname'], data['lastname'], data['age'], data['phone'], data['email'], data['update_date'], id)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify({'message': 'User updated'})


@app.delete('/users/{id}')
def delete_user(id: int):
    postsql = "DELETE FROM users WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify({'message': 'User deleted'})


# --- Booking roots --- #

@app.get('/bookings')
def get_all_bookings():
    my_cursor.execute("SELECT * FROM bookings")
    rows = my_cursor.fetchall()
    bookings = []
    for row in rows:
        booking = Booking(row[1], row[2], row[0], row[3], row[4], row[5], row[6], row[7], row[8])
        bookings.append(booking.__dict__)
    return jsonify(bookings)


@app.post('/bookings')
def add_booking():
    data = request.get_json()
    booking = Booking(data['id'], data['username'], data['nights'], data['reservation_number'], data['numbers_peoples'],
                      data['users_id'],
                      data['payements_id'], data['created_date'], data['update_date'])
    postsql = "INSERT INTO bookings (id, username, nights, reservation_number, numbers_peoples, users_id, payements_id, created_date, update_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (
        booking.id, booking.username, booking.nights, booking.reservation_number, booking.numbers_peoples,
        booking.users_id,
        booking.payements_id, booking.created_date,
        booking.update_date)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify(booking.__dict__)


@app.get('/bookings/{id}')
def get_booking(id: int):
    postsql = "SELECT * FROM bookings WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    row = my_cursor.fetchone()
    if row is None:
        return jsonify({'error': 'Booking not found'}), 404
    booking = Booking(row[1], row[2], row[0], row[3], row[4], row[5], row[6], row[7], row[8])
    return jsonify(booking.__dict__)


@app.delete('/bookings/{id}')
def delete_booking(id: int):
    postsql = "DELETE FROM bookings WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify({'message': 'Booking deleted'})


# --- Payment roots --- #

@app.get('/payments')
def get_all_payments():
    my_cursor.execute("SELECT * FROM payments")
    rows = my_cursor.fetchall()
    payments = []
    for row in rows:
        payment = Payment(row[0], row[1], row[2], row[3], row[4], row[5])
        payments.append(payment.__dict__)
    return jsonify(payments)


@app.post('/payments')
def add_payment():
    data = request.get_json()
    payment = Payment(data['id'], data['price'], data['promo'], data['total'], data['created_date'],
                      data['update_date'])
    postsql = "INSERT INTO payments (id, price, promo, total, created_date, update_date) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (payment.id, payment.price, payment.promo, payment.total, payment.created_date, payment.update_date)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify(payment.__dict__)


@app.get('/payments/{id}')
def get_payment(id: int):
    postsql = "SELECT * FROM payments WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    row = my_cursor.fetchone()
    if row is None:
        return jsonify({'error': 'Payment not found'}), 404
    payment = Payment(row[0], row[1], row[2], row[3], row[4], row[5])
    return jsonify(payment.__dict__)


@app.delete('/payments/{id}')
def delete_payment(id: int):
    postsql = "DELETE FROM payments WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify({'message': 'Payment deleted'})


# --- AdditionalServices roots --- #

@app.get('/additional_services')
def get_all_additional_services():
    my_cursor.execute("SELECT * FROM additional_services")
    rows = my_cursor.fetchall()
    additional_services = []
    for row in rows:
        additional_service = AdditionalService(row[0], row[1], row[2], row[3], row[4])
        additional_services.append(additional_service.__dict__)
    return jsonify(additional_services)


@app.post('/additional_services')
def add_additional_service():
    data = request.get_json()
    additional_service = AdditionalService(data['id'], data['name'], data['price'], data['bookings_id'],
                                           data['bookings_users_id'])
    postsql = "INSERT INTO additional_services (id, name, price, bookings_id, bookings_users_id) VALUES (%s, %s, %s, %s, %s)"
    val = (additional_service.id, additional_service.name, additional_service.price, additional_service.bookings_id,
           additional_service.bookings_users_id)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify(additional_service.__dict__)


@app.get('/additional_services/{id}')
def get_additional_service(id: int):
    postsql = "SELECT * FROM additional_services WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    row = my_cursor.fetchone()
    if row is None:
        return jsonify({'error': 'Additional Service not found'}), 404
    additional_service = AdditionalService(row[0], row[1], row[2], row[3], row[4])
    return jsonify(additional_service.__dict__)


@app.put('/additional_services/{id}')
def update_additional_service(id: int):
    data = request.get_json()
    postsql = "UPDATE additional_services SET name = %s, price = %s WHERE id = %s"
    val = (data['name'], data['price'], id)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify({'message': 'Additional Service updated'})


@app.delete('/additional_services/{id}')
def delete_additional_service(id: int):
    postsql = "DELETE FROM additional_services WHERE id = %s"
    val = (id,)
    my_cursor.execute(postsql, val)
    mydb.commit()
    return jsonify({'message': 'Additional Service deleted'})


if __name__ == '__main__':
    app.run(debug=True)
