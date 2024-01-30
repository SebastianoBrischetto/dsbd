from src import Notifier
import os

app = Notifier(os.environ.get('BOT_TOKEN'), __name__)
if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')