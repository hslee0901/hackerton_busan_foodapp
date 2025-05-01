from flask import Flask
from routes import main_bp
from login import login_bp
from logout import logout_bp
from signup import signup_bp
from search import search_bp
from list import list_bp 

app = Flask(__name__)
app.secret_key = 'ASDASDAR1324SADWQ'  # 세션 암호화를 위한 키
app.register_blueprint(main_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(search_bp)
app.register_blueprint(list_bp)

if __name__ == '__main__':
   app.run(debug=True)
