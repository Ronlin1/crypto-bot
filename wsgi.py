from app import app
import waitress

if __name__ == "__main__":
    print("__Amanda__is___up___")
    waitress.serve(app, host='0.0.0.0', port=8080)
    