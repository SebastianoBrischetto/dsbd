from src import RegisterForm

app = RegisterForm(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')