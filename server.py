from flask import Flask, request, jsonify
from flask.json import JSONEncoder

app = Flask(__name__)

class StringConverterJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


# Use our custom JSONEncoder
app.json_encoder = StringConverterJSONEncoder

from post_storage import PostsStore

posts_store = PostsStore(vector_dir="db")

def default_json(t):
    return f'{t}'


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    query = data.get('query')
    metadata = data.get('metadata', {})
    limit = data.get('limit', 5)

    if query is None:
        return jsonify({"error": "No text_query provided"}, default=default_json), 400

    try:
        posts = posts_store.search_posts(query, metadata, limit=limit)
    except Exception as e:
        return jsonify({"error": str(e)}, default=default_json), 500

    posts = [p.dict() for p in posts]
    return jsonify(posts)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',
            port=5555,
            use_reloader=False)
