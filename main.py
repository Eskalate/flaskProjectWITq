import pymysql
from tables import Results
from tables_std import Results1
from db_config import mysql
from flask import flash, render_template, request, redirect, session, url_for
from flask import Flask

app = Flask(__name__)

app.secret_key = 'your secret key'

adminlogin = 0


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tbl_user WHERE user_name = %s AND user_password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            adminlogin = account[4]
            if adminlogin == 1:
                return redirect('/adm_view')
            else:
                return redirect('/std_view')
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='')


@app.route('/new_user')
def add_user_view():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def add_user():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _admin = request.form['inputAdmin']
        if _name and _email and _password and _admin and request.method == 'POST':
            sql = "INSERT INTO tbl_user(user_name, user_email, user_password, if_admin) VALUES(%s, %s, %s, %s)"
            data = (_name, _email, _password, _admin)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            return 'User added successfully'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/adm_view')
def users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_user")
        rows = cursor.fetchall()
        table = Results(rows)
        table.border = True
        return render_template('users.html', table=table)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/std_view')
def std_users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_user")
        rows = cursor.fetchall()
        table1 = Results1(rows)
        table1.border = True
        return render_template('std_users.html', table1=table1)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/edit/<int:id>')
def edit_view(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tbl_user WHERE user_id=%s", id)
        row = cursor.fetchone()
        if row:
            return render_template('edit.html', row=row)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/update', methods=['POST'])
def update_user():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _id = request.form['id']
        if _name and _email and _password and _id and request.method == 'POST':
            sql = "UPDATE tbl_user SET user_name=%s, user_email=%s, user_password=%s WHERE user_id=%s"
            data = (_name, _email, _password, _id,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User updated successfully!')
            if adminlogin == 1:
                return redirect('/adm_view')
            else:
                return redirect('/std_view')
        else:
            return 'Error while updating user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/logout/')
def logout():
    adminlogin = 0
    return redirect('/')


@app.route('/delete/<int:id>')
def delete_user(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tbl_user WHERE user_id=%s", (id,))
        conn.commit()
        flash('User deleted successfully!')
        return redirect('/')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run()
