from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from db import db
from models.users import UserModel
from schemas import UserSchema
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import jwt_required, create_access_token, get_jwt, create_refresh_token, get_jwt_identity
from blocklist import BLOCKLIST

# Initialize Flask-Smorest Blueprint
blp = Blueprint('Users', "users", description='Operations on users')

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Register a new user"""
        if UserModel.query.filter_by(username=user_data['username']).first():
            abort(400, message="Username already exists.")
        user = UserModel(**user_data)
        user.password = sha256.hash(user.password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Username already exists.")
        return user, 201
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def post(self, user_data):
        """Login a user"""
        user = UserModel.query.filter_by(username=user_data['username']).first()
        if user and sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {"access_token": access_token}, 200
        # If user not found or password doesn't match

        if not user or not sha256.verify(user_data['password'], user.password):
            abort(401, message="Invalid credentials.")
        return user, 200

@blp.route("/user/<int:user_id>")
class UserDetail(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get a user by ID"""
        user = UserModel.query.get_or_404(user_id)
        return user
    @jwt_required(fresh=True)  # Ensure that only authenticated users can delete users
    def delete(self, user_id):
        """Delete a user by ID"""
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200
    
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """Logout a user"""
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

@blp.route("/refresh")
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """Refresh a user's access token"""
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_access_token}, 200

