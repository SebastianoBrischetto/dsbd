from flask import Flask, request
import time

app = Flask(__name__)


@app.route('/update', methods=['POST'])
def update():
    while True:
        data = request.data
        if data is None:
            print("messaggio ricevuto")
            print(data)
            time.sleep(5)
        else:
            print("messaggio non ricevuto")
            time.sleep(5)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
