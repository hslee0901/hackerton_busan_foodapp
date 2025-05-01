from flask import Blueprint, request, redirect, url_for, render_template, session
from DBconnect import DBConnection
from mysql.connector import Error

login_bp = Blueprint('login', __name__)

def validate_user(username, password):
    db = DBConnection()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, id, user_name, password FROM users WHERE id = %s", (username,))
            user = cursor.fetchone()
            if user and user['password'] == password:
                return user
            else:
                return None
        except Error as e:
            print("데이터베이스 검색 오류: ", e)
            return None
        finally:
            cursor.close()
            connection.close()
    return None

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['ID']
        password = request.form['password']
        user = validate_user(username, password)
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['id']
            session['user_name'] = user['user_name']
            session['is_logged_in'] = True
            return redirect(url_for('main.index'))  # 실제 리다이렉트할 경로로 변경하세요
        else:
            error_message = "아이디 혹은 비밀번호가 올바르지 않습니다."
            return render_template('index.html', error_message=error_message)
    return render_template('index.html')
