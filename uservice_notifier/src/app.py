from notifier import NotificationService


app = NotificationService()
  


if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host='0.0.0.0')
