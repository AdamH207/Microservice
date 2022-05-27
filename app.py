from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import requests



app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)


db.create_all()


post_args_parser = reqparse.RequestParser(bundle_errors=True)
post_args_parser.add_argument("userId", type=int, required=True, help="UserId cannot be blank or cannot be converted!")
post_args_parser.add_argument("title", type=str, required=True, help="UserId cannot be blank!")
post_args_parser.add_argument("body", type=str, required=True, help="UserId cannot be blank!")


put_args_parser = reqparse.RequestParser()
put_args_parser.add_argument("title", type=str)
put_args_parser.add_argument("body", type=str)


resource_fields = {
    'id': fields.Integer,
    'userId': fields.Integer,
    'title': fields.String,
    'body': fields.String
}


class User(Resource):
    @marshal_with(resource_fields)
    def get(self, post_userid):
        '''
        Get api method that return posts with correspond userId.
        '''
        result = PostModel.query.filter_by(userId=post_userid).all()
        if not result:
            abort(404, message="Post not found!")
        return result, 200


class Post(Resource):
    @marshal_with(resource_fields)
    def get(self, post_id = None):
        '''
        Get api method that return post with correspond id.
        '''
        if not post_id:
            posts = PostModel.query.all()
            return posts
        result = PostModel.query.get(post_id)
        if not result:
            response = requests.get("https://jsonplaceholder.typicode.com/posts/" + str(post_id))
            post = PostModel(id=response.json()['id'], userId=response.json()['userId'], title=response.json()['title'], body=response.json()['body'])
            db.session.add(post)
            db.session.commit()
            return post, 200
        return result, 200
    
    @marshal_with(resource_fields)
    def post(self):
        '''
        Post api method that create new post.
        '''
        args = post_args_parser.parse_args()
        response = requests.get("https://jsonplaceholder.typicode.com/users/" + str(args['userId']))
        if response.json() == {}:
            abort(400, message="User not found!")
        post = PostModel(userId=args['userId'], title=args['title'], body=args['body'])
        db.session.add(post)
        db.session.commit()
        return post, 201

    @marshal_with(resource_fields)
    def delete(self, post_id):
        '''
        Detete api method that delete post with correspond id.
        '''
        result = PostModel.query.filter_by(id=post_id).first()
        if not result:
            abort(404, message="Post not found!")
        db.session.delete(result)
        db.session.commit()
        return result, 200

    @marshal_with(resource_fields)
    def put(self, post_id):
        '''
        Put api method that update post with correspond id.
        '''
        args = put_args_parser.parse_args()
        result = PostModel.query.get(post_id)
        if not result:
            abort(404, message="Post not found!")
        if args['title']:
            result.title = args['title']
        if args['body']:
            result.body = args['body']
        db.session.commit()
        return result, 200


api.add_resource(User, "/users/<int:post_userid>/posts")
api.add_resource(Post, "/posts/<int:post_id>", "/posts")



if __name__ == "__main__":
    app.run()
