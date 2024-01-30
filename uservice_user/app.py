from src import UserUService
import os

app = UserUService(os.environ.get('MONGO_DB'), __name__)
if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0')