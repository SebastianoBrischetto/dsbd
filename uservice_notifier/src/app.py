from notifier import NotificationService


app = NotificationService("6765515091:AAGSMzDzfw4f5zrrZ3FF8Lzboz5g2uUY9ZE")
  
if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')
