import os
from server.demo_server import create_app

# Read the environment or default to 'dev'
env_name = os.getenv('FLASK_ENV', 'dev')
app = create_app(env_name)

if __name__ == '__main__':
    # Run the Jeep
    app.run(host='0.0.0.0', port=5556)