from src import Notifier

app = Notifier("6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE", __name__)
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')