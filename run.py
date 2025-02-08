import os
from app import create_app
from app.utils.logging import init_logging

app = create_app()
init_logging(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)