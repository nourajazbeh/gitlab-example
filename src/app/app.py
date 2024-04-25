from flask import Flask, jsonify, request

app = Flask(__name__)

# Einfache Begrüßung
@app.route('/')
def hello():
    return "Hallo Welt!"

# Eine Route, die einen Namen als Parameter nimmt und begrüßt
@app.route('/hello/<name>')
def hello_name(name):
    return f"Hallo, {name}!"

# Eine JSON-Route, die Daten zurückgibt
@app.route('/data')
def data():
    return jsonify({'key': 'value', 'int': 1})

# Eine POST-Route, die Daten empfängt und etwas damit macht
@app.route('/post', methods=['POST'])
def post_data():
    data = request.json
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
