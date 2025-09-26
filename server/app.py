# server/app.py
#!/usr/bin/env python3

from flask import Flask, request, session, make_response
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource

from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'  # session key
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
CORS(app)

api = Api(app)


# -------------------
# Resources
# -------------------

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")

        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)

        return make_response({"error": "Unauthorized"}, 401)


class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return make_response("", 204)


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return make_response(user.to_dict(), 200)
        # ✅ fix: return empty dict with 401 instead of {"error": ...}
        return make_response({}, 401)


# -------------------
# Test helper
# -------------------
@app.route('/clear', methods=['GET'])
def clear():
    """Helper for tests: clears the session."""
    session.clear()
    return make_response({"status": "session cleared"}, 200)


# -------------------
# Register Resources
# -------------------
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

