from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template
from DBconnect import DBConnection
import mysql.connector
from mysql.connector import Error

list_bp = Blueprint('list', __name__)

@list_bp.route("/add_favorite", methods=["POST"])
def add_favorite():
    print("Session data:", session)  # session 내용 출력
    if 'username' not in session or not session['username']:
        return jsonify({"success": False, "message": "로그인이 필요합니다."})

    # 클라이언트로부터 JSON 데이터 받기
    data = request.get_json()
    place_id = data.get("place_id")
    place_name = data.get("place_name")
    address = data.get("address")
    phone = data.get("phone")   
    place_url = data.get("place_url")
    user_id = session['username']  # 현재 로그인한 사용자의 ID (username)

    # 데이터베이스 연결
    db = DBConnection()
    cursor, connection = db.get_cursor()

    if not cursor or not connection:
        return jsonify({"success": False, "message": "데이터베이스 연결 실패"})

    try:
        # 중복 데이터 확인
        query = """
        SELECT * FROM favorites WHERE id = %s AND place_id = %s
        """
        cursor.execute(query, (user_id, place_id))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "이미 즐겨찾기에 추가된 가게입니다."})

        # favorites 테이블에 데이터 삽입
        query = """
        INSERT INTO favorites (id, place_id, place_name, address, phone, place_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, place_id, place_name, address, phone, place_url))
        db.commit(connection)  # 변경 사항 저장

        # 성공 응답
        return jsonify({"success": True, "message": "즐겨찾기에 추가되었습니다."})

    except mysql.connector.Error as err:
        # 오류 발생 시
        db.rollback(connection)
        return jsonify({"success": False, "message": f"데이터베이스 오류: {err}"})

    finally:
        # 데이터베이스 연결 종료
        if cursor:
            cursor.close()
        if connection:
            db.close_connection(connection)

@list_bp.route("/favorites")
def show_favorites():
    if 'username' not in session or not session['username']:
        return redirect(url_for('login.login'))

    id = session['username']

    db = DBConnection()
    cursor, connection = db.get_cursor()

    if not cursor or not connection:
        return render_template("error.html", message="데이터베이스 연결 실패")

    try:
        query = """
        SELECT place_id, place_name, address, phone, place_url
        FROM favorites
        WHERE id = %s
        """
        cursor.execute(query, (id,))
        results = cursor.fetchall()

        # ✅ 데이터 출력 (디버깅용)
        print("Fetched results:", results)

        column_names = [desc[0] for desc in cursor.description]
        results = [dict(zip(column_names, row)) for row in results]

        print("Formatted results:", results)  # 딕셔너리 형태 확인

        return render_template("list.html", results=results)

    except mysql.connector.Error as err:
        return render_template("error.html", message=f"데이터베이스 오류: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            db.close_connection(connection)

@list_bp.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    if 'username' not in session or not session['username']:
        return jsonify({"success": False, "message": "로그인이 필요합니다."})

    data = request.get_json()
    print("Received data:", data)
    place_id = data.get("place_id")
    id = session['username']

    
    db = DBConnection()
    cursor, connection = db.get_cursor()
    print("삭제 요청 ID:", id)
    print("삭제 요청 place_id:", place_id)
    if not cursor or not connection:
        return jsonify({"success": False, "message": "데이터베이스 연결 실패"})
    try:
        query = """
        DELETE FROM favorites WHERE id = %s AND place_id = %s
        """
        cursor.execute(query, (id, place_id))
        deleted_rows = cursor.rowcount  # 🛠 삭제된 행 개수 확인

        if deleted_rows == 0:
            return jsonify({"success": False, "message": "삭제할 데이터가 없습니다. (id 또는 place_id 확인 필요)"})

        db.commit(connection)

        return jsonify({"success": True, "message": "즐겨찾기에서 삭제되었습니다."})

    except mysql.connector.Error as err:
        db.rollback(connection)
        return jsonify({"success": False, "message": f"데이터베이스 오류: {err}"})

    finally:
        if cursor:
            cursor.close()
        if connection:
            db.close_connection(connection)

@list_bp.route('/add_review', methods=['POST'])
def add_review():
    try:
        data = request.json  # JSON 데이터 받기
        store_id = data.get('store_id')  # 가게 ID
        user_id = data.get('id')  # 작성자 ID
        content = data.get('content')  # 리뷰 내용

        if not store_id or not user_id or not content:
            return jsonify({"error": "모든 필드를 입력해주세요."}), 400

        db = DBConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        # 리뷰 저장 SQL 실행
        sql = "INSERT INTO reviews (store_id, id, content) VALUES (%s, %s, %s)"
        cursor.execute(sql, (store_id, user_id, content))
        conn.commit()

        return jsonify({"message": "리뷰가 성공적으로 등록되었습니다!"}), 201

    except Error as e:
        return jsonify({"error": f"데이터베이스 오류 발생: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()