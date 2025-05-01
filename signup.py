from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify
from DBconnect import DBConnection
from mysql.connector import Error

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        id = request.form.get('ID')
        user_name = request.form.get('NickName')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not (id and user_name and password and password_confirm):
            flash("모든 칸을 입력해주세요.")
            return redirect(url_for('main.index'))

        if password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for('main.index'))

        try:
            db = DBConnection()
            conn = db.get_connection()
            cursor = conn.cursor()

            # 중복 확인
            cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
            if cursor.fetchone():
                flash("이미 사용 중인 ID입니다.")
                return redirect(url_for('main.index'))

            # 데이터 삽입
            cursor.execute("INSERT INTO users (id, user_name, password) VALUES (%s, %s, %s)",
                           (id, user_name, password))  # 실제 프로젝트에서는 비밀번호 암호화 필요
            conn.commit()
            flash("회원가입이 완료되었습니다. 로그인 해주세요!")
            return redirect(url_for('main.index'))  # 로그인 페이지로 이동

        except Error as e:
            flash(f"데이터베이스 오류 발생: {str(e)}")
            return redirect(url_for('main.index'))

        finally:
            cursor.close()
            conn.close()

    return render_template('index.html')

@signup_bp.route('/check_id', methods=['POST'])
def check_id():
    data = request.get_json()
    user_id = data.get('ID')

    if not user_id:
        return jsonify({"error": "아이디를 입력해주세요."}), 400

    try:
        db = DBConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
        count = cursor.fetchone()

        return jsonify({"exists": count[0] > 0})

    except Error as e:
        return jsonify({"error": f"데이터베이스 오류: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()
