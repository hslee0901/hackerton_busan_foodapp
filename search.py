from flask import Blueprint, request, render_template, jsonify
from DBconnect import DBConnection
from mysql.connector import Error
import requests 
import urllib.parse  # 한글 오류 해결

search_bp = Blueprint('search', __name__)

# 카카오 API 키 설정
KAKAO_API_KEY = "85e8f0bca57b85de47ebd455a73ae806"

# 📌 1. 카카오 지역 검색 API 호출 (맛집 검색)
@search_bp.route("/search", methods=["POST", "GET"])
def search_places():
    s_region = request.form.get("region")
    food_type = request.form.get("food_type")
    query = request.form.get("query", "")  # 사용자가 입력한 추가 검색어 (선택사항)
    page = int(request.form.get("page", 1))  # 페이지 번호, 기본값은 1
    results_per_page = 15  # 페이지당 결과 수 (최대 15로 설정)
    
    
    print("Region:", s_region)
    print("Food Type:", food_type)
    print("Query:", query)
    print("Page:", page)

    if not s_region or not food_type:
        return render_template("search.html", error="지역구와 음식 종류를 선택하세요.")

    region = f"부산 {s_region}"  
    
    full_query = f"{region} {food_type} {query}"  # 검색어에 지역구와 음식 종류를 추가
    encoded_query = urllib.parse.quote(full_query)  # 한글 검색어 인코딩
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={encoded_query}&page={page}&size={results_per_page}"

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    print("카카오 API 응답:", response.text)  # 🔍 API 응답 확인

    if response.status_code == 200:
        search_results = response.json().get("documents", [])
        return render_template("search.html", results=search_results, query=query, page=page, region=s_region, results_per_page=results_per_page)
    else:
        return render_template("search.html", error="검색 결과를 가져올 수 없습니다.")
    
@search_bp.route("/search-btn", methods=["POST", "GET"])
def search_places_btn():
    s_region = request.form.get("region")
    query = request.form.get("query", "")  # 사용자가 입력한 추가 검색어 (선택사항)
    page = int(request.form.get("page", 1))  # 페이지 번호, 기본값은 1
    results_per_page = 15  # 페이지당 결과 수 (최대 15로 설정)

    if not s_region:
        return render_template("search.html", error="지역구를 선택하세요.")

    region = f"부산 {s_region}"  # 지역 설정
    full_query = f"{region} 음식점 {query}"   # 검색어에 지역구와 추가 검색어를 추가
    encoded_query = urllib.parse.quote(full_query)  # 한글 검색어 인코딩
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={encoded_query}&page={page}&size={results_per_page}"

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    print("카카오 API 응답:", response.text)  # 🔍 API 응답 확인

    if response.status_code == 200:
        search_results = response.json().get("documents", [])
        return render_template("search2.html", results=search_results, query=query, page=page, region=s_region, results_per_page=results_per_page)
    else:
        return render_template("search2.html", error="검색 결과를 가져올 수 없습니다.")



# 📌 1. 리뷰 추가 (DB 사용)
@search_bp.route("/add", methods=["POST"])
def add_review():
    data = request.json
    place_id = data.get("place_id")
    user_id = data.get("id")
    rating = data.get("rating")
    comment = data.get("comment")

    db = DBConnection()
    connection = db.get_connection()

    if connection:
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO review (place_id, user_id, rating, comment) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (place_id, user_id, rating, comment))
            connection.commit()
            return jsonify({"message": "리뷰가 성공적으로 저장되었습니다!"}), 201
        except Error as e:
            print("데이터베이스 삽입 오류: ", e)
            return jsonify({"error": "리뷰 저장 실패"}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

# 📌 2. 특정 가게의 리뷰 조회 (DB 사용)
@search_bp.route("/review", methods=["GET"])
def get_reviews():
    place_name = request.args.get("place")

    if not place_name:
        return jsonify({"error": "장소 이름을 입력해야 합니다."}), 400

    db = DBConnection()
    connection = db.get_connection()

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT user_id, review_text, created_at FROM reviews WHERE place_name = %s ORDER BY created_at DESC"
            cursor.execute(query, (place_name,))
            reviews = cursor.fetchall()
            return jsonify({"reviews": reviews}), 200
        except Error as e:
            print("데이터베이스 조회 오류: ", e)
            return jsonify({"error": "리뷰 조회 실패"}), 500
        finally:
            cursor.close()
            connection.close()
