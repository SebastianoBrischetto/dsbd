import requests
from flask import Flask, request


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'hello!'

@app.route('/register' , methods=['GET'])
def prova():
    user_id = request.args.get('user_id')
    requests.get('https://api.telegram.org/bot6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE/sendMessage?chat_id='+user_id+'&text=ti sei registrato')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

