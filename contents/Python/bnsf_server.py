import flask
import flask_cors
import json

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route('/', methods=['GET'])
def echo():
    data = {
        "message": "Hello, World!"
    }
    return flask.jsonify(data), 200

@app.route('/user', methods=['POST'])
def user():
    data = flask.request.get_json()

    name = None
    age = None

    if 'name' not in data or 'age' not in data:
        return flask.jsonify({"Error": "Missing 'name' or 'age' field"}), 400
    else:
        name = data.get('name')
        age = data.get('age')
    
    if len(name) > 32:
        return flask.jsonify({"Error": "Name too long"}), 400
    
    try:
        age = int(age)
    except Exception:
        return flask.jsonify({"Error": "Age must be an integer"}), 400
    
    if age < 16:
        return flask.jsonify({"Error": "Age must be at least 16"}), 400

    # call save

    # return success
    return flask.jsonify({"message": "User data saved successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)