# Flask and CORS imports
from flask import Flask, request, jsonify
from flask_cors import CORS

# import data factory 
import data_factory

app = Flask("Data Server")
CORS(app)

@app.route('/', methods=['GET'])
def connection():
    return jsonify('Connected to Data Server!')

@app.route('/getData', methods=['GET'])
def get_data(type: str = ""):
    # declare return type
    return_data = {}

    if type == "":
        return_data['uuid'] = data_factory.generate_uuid()
        return jsonify(return_data)
    else:
        return_data['error'] = 'hit the default case in the switch statement'
        return jsonify(return_data)

if __name__ == '__main__':
    app.run(debug=True)