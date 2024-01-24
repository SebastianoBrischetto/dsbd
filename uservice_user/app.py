from src import UserUService

app = UserUService('mongodb://root:password@mongo_db:27017/weather_report_db?authSource=admin&authMechanism=SCRAM-SHA-256', __name__)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')