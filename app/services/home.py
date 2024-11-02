from db import MongoDB
from . import api_bp

mongo_db = MongoDB()

@api_bp.route("/recommendation/to-connect")
def get_remmended_to_connect():
    return "<p>Hello, World!</p>"

@api_bp.route("/recommendation/to-chat")
def get_remmended_to_chat():
    return "<p>Hello, World!</p>"

@api_bp.route("/search")
def search_agents():
    return "<p>Hello, World!</p>"

