import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
import traceback

class BrowserLogger:
    """Centralized logging system for the AI-powered browser"""
    
    def __init__(self, name: str = "ai_browser", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler with rotation
        log_file = os.path.join(log_dir, f"browser_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Error log handler
        error_file = os.path.join(log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=5*1024*1024, backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Apply formatters
        console_handler.setFormatter(simple_formatter)
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log info message"""
        self.logger.info(message, extra=extra)
    
    def debug(self, message: str, extra: Optional[dict] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exception: Optional[Exception] = None, extra: Optional[dict] = None):
        """Log error message with optional exception details"""
        if exception:
            error_msg = f"{message}: {str(exception)}\n{traceback.format_exc()}"
        else:
            error_msg = message
        self.logger.error(error_msg, extra=extra)
    
    def critical(self, message: str, exception: Optional[Exception] = None, extra: Optional[dict] = None):
        """Log critical message with optional exception details"""
        if exception:
            error_msg = f"{message}: {str(exception)}\n{traceback.format_exc()}"
        else:
            error_msg = message
        self.logger.critical(error_msg, extra=extra)

# Global logger instance
logger = BrowserLogger()

def get_logger(name: str = "ai_browser") -> BrowserLogger:
    """Get logger instance"""
    return BrowserLogger(name)

class ErrorHandler:
    """Error handling utilities"""
    
    @staticmethod
    def handle_exception(func):
        """Decorator for handling exceptions in functions"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}", exception=e)
                raise
        return wrapper
    
    @staticmethod
    def safe_execute(func, default_return=None, log_errors=True):
        """Safely execute a function and return default on error"""
        try:
            return func()
        except Exception as e:
            if log_errors:
                logger.error(f"Safe execution failed for {func.__name__ if hasattr(func, '__name__') else 'anonymous function'}", exception=e)
            return default_return
    
    @staticmethod
    def validate_input(data, data_type, field_name="input"):
        """Validate input data type"""
        if not isinstance(data, data_type):
            error_msg = f"Invalid {field_name}: expected {data_type.__name__}, got {type(data).__name__}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        return True

# Custom exceptions for the browser
class BrowserError(Exception):
    """Base exception for browser-related errors"""
    pass

class NavigationError(BrowserError):
    """Exception for navigation-related errors"""
    pass

class TabError(BrowserError):
    """Exception for tab-related errors"""
    pass

class AIServiceError(BrowserError):
    """Exception for AI service-related errors"""
    pass

class ScrapingError(BrowserError):
    """Exception for web scraping-related errors"""
    pass

class DatabaseError(BrowserError):
    """Exception for database-related errors"""
    pass
