from src.website import create_app
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
