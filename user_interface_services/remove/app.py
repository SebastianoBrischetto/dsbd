import os
from src import Remove

app = Remove( os.environ.get('API_GATEWAY') + "users_db/", __name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
