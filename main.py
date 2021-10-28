import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        return redirect(url_for('home_page') + '?first_name={}'.format(request.form['search']))
    if request.args.get('first_name', None):
        customers = get_customers(first_name=request.args['first_name'])
    else:
        customers = get_customers()
    return render_template('index.html', customers=customers)


@app.route('/add/', methods=['POST', 'GET'])
def customer_add_view():
    if request.method == 'POST':
        try:
            create_customer(list(request.form.values()))
            return redirect(url_for("home_page"))
        except Exception as e:
            return render_template('customer_add.html')

    return render_template('customer_add.html')


def get_connection():
    return psycopg2.connect(database='techschool', user='postgres', password='postgres', port=5432, host='localhost')


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers(
            id serial primary key,
            first_name varchar(100) not null,
            last_name varchar(100) not null,
            phone_number varchar(13) not null,
            email varchar(100),
            address text not null,
            birth_date date not null)
    """)
    conn.commit()
    cursor.close()
    conn.close()


def create_customer(values):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers(
            first_name,
            last_name,
            phone_number,
            email,
            birth_date,
            address) VALUES (
          %s, %s, %s, %s, %s, %s
        )
    """, values)
    conn.commit()
    cursor.close()
    conn.close()


def get_customers(first_name=None):
    query = """SELECT * FROM customers"""
    if first_name:
        query = """SELECT * FROM customers WHERE first_name ILIKE '%{}%'""".format(first_name)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    keys = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'address', 'birth_date']
    return [dict(zip(keys, customer)) for customer in customers]

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port='5000', debug=True)
