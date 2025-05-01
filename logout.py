from flask import Blueprint, redirect, url_for, session

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout')
def logout():
    session.clear()  # 모든 세션 변수 삭제
    return redirect(url_for('main.index'))
