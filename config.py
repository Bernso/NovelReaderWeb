import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class for the application."""
    
    # Application Settings
    SECRET_KEY = os.urandom(24)
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', 1111))
    
    # Discord Webhook
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    NOVELS_DIR = os.path.join(BASE_DIR, 'templates', 'novels')
    
    # Logging Configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'formatter': 'standard',
                'level': 'ERROR'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    # SQLAlchemy Settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///comments.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
