from src import Register
import os

app = Register(os.environ.get('API_GATEWAY') + "users_db/", os.environ.get('API_GATEWAY') + "register_form/", __name__)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')