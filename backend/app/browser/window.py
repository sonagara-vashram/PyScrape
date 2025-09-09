# Main browser window with PyQt6
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QTabWidget, QToolBar,
    QStatusBar, QMenuBar, QMessageBox, QSplashScreen
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from typing import Optional
import os

# Import our custom modules
from ..utils.logger import logger, ErrorHandler, BrowserError, NavigationError

class BrowserWindow(QMainWindow):
    """Main browser window class with PyQt6"""
    
    # Signals for communication
    url_changed = pyqtSignal(str)
    page_loaded = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        try:
            logger.info("Initializing browser window")
            self._init_ui()
            self._setup_connections()
            logger.info("Browser window initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize browser window", exception=e)
            self._show_error_dialog("Initialization Error", 
                                   "Failed to initialize browser window. Please restart the application.")
    
    def _init_ui(self):
        """Initialize the user interface"""
        try:
            # Set window properties
            self.setWindowTitle("AI-Powered Browser")
            self.setGeometry(100, 100, 1200, 800)
            self.setMinimumSize(800, 600)
            
            # Set window icon (if available)
            self._set_window_icon()
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create components
            self._create_menu_bar()
            self._create_toolbar()
            self._create_address_bar()
            self._create_web_view()
            self._create_status_bar()
            
            # Add components to layout
            main_layout.addWidget(self.toolbar)
            main_layout.addWidget(self.address_widget)
            main_layout.addWidget(self.web_view, 1)  # Stretch factor 1
            
            logger.debug("UI components created successfully")
            
        except Exception as e:
            logger.error("Error creating UI components", exception=e)
            raise BrowserError("Failed to create UI components") from e
    
    def _set_window_icon(self):
        """Set window icon if available"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logger.debug(f"Window icon set from {icon_path}")
        except Exception as e:
            logger.warning("Could not set window icon", exception=e)
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        try:
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu('&File')
            
            new_tab_action = QAction('&New Tab', self)
            new_tab_action.setShortcut('Ctrl+T')
            new_tab_action.triggered.connect(self._new_tab)
            file_menu.addAction(new_tab_action)
            
            close_tab_action = QAction('&Close Tab', self)
            close_tab_action.setShortcut('Ctrl+W')
            close_tab_action.triggered.connect(self._close_current_tab)
            file_menu.addAction(close_tab_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction('&Exit', self)
            exit_action.setShortcut('Ctrl+Q')
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Edit menu
            edit_menu = menubar.addMenu('&Edit')
            
            # View menu
            view_menu = menubar.addMenu('&View')
            
            # Tools menu
            tools_menu = menubar.addMenu('&Tools')
            
            # Help menu
            help_menu = menubar.addMenu('&Help')
            
            about_action = QAction('&About', self)
            about_action.triggered.connect(self._show_about)
            help_menu.addAction(about_action)
            
            logger.debug("Menu bar created successfully")
            
        except Exception as e:
            logger.error("Error creating menu bar", exception=e)
    
    def _create_toolbar(self):
        """Create navigation toolbar"""
        try:
            self.toolbar = QToolBar()
            self.toolbar.setMovable(False)
            self.addToolBar(self.toolbar)
            
            # Back button
            self.back_btn = QPushButton("←")
            self.back_btn.setMaximumWidth(40)
            self.back_btn.setToolTip("Go back")
            self.back_btn.clicked.connect(self._go_back)
            self.toolbar.addWidget(self.back_btn)
            
            # Forward button
            self.forward_btn = QPushButton("→")
            self.forward_btn.setMaximumWidth(40)
            self.forward_btn.setToolTip("Go forward")
            self.forward_btn.clicked.connect(self._go_forward)
            self.toolbar.addWidget(self.forward_btn)
            
            # Refresh button
            self.refresh_btn = QPushButton("⟳")
            self.refresh_btn.setMaximumWidth(40)
            self.refresh_btn.setToolTip("Refresh page")
            self.refresh_btn.clicked.connect(self._refresh_page)
            self.toolbar.addWidget(self.refresh_btn)
            
            # Home button
            self.home_btn = QPushButton("🏠")
            self.home_btn.setMaximumWidth(40)
            self.home_btn.setToolTip("Go home")
            self.home_btn.clicked.connect(self._go_home)
            self.toolbar.addWidget(self.home_btn)
            
            logger.debug("Toolbar created successfully")
            
        except Exception as e:
            logger.error("Error creating toolbar", exception=e)
    
    def _create_address_bar(self):
        """Create address bar widget"""
        try:
            self.address_widget = QWidget()
            address_layout = QHBoxLayout(self.address_widget)
            address_layout.setContentsMargins(5, 5, 5, 5)
            
            # Address bar
            self.address_bar = QLineEdit()
            self.address_bar.setPlaceholderText("Enter URL or search...")
            self.address_bar.returnPressed.connect(self._navigate_to_url)
            address_layout.addWidget(self.address_bar)
            
            # Go button
            self.go_btn = QPushButton("Go")
            self.go_btn.setMaximumWidth(50)
            self.go_btn.clicked.connect(self._navigate_to_url)
            address_layout.addWidget(self.go_btn)
            
            logger.debug("Address bar created successfully")
            
        except Exception as e:
            logger.error("Error creating address bar", exception=e)
    
    def _create_web_view(self):
        """Create web engine view"""
        try:
            self.web_view = QWebEngineView()
            
            # Load default page
            self.web_view.setUrl(QUrl("https://www.google.com"))
            
            logger.debug("Web view created successfully")
            
        except Exception as e:
            logger.error("Error creating web view", exception=e)
            raise BrowserError("Failed to create web engine view") from e
    
    def _create_status_bar(self):
        """Create status bar"""
        try:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Ready", 2000)
            
            logger.debug("Status bar created successfully")
            
        except Exception as e:
            logger.error("Error creating status bar", exception=e)
    
    def _setup_connections(self):
        """Setup signal-slot connections"""
        try:
            # Web view signals
            self.web_view.urlChanged.connect(self._on_url_changed)
            self.web_view.loadFinished.connect(self._on_load_finished)
            self.web_view.loadStarted.connect(self._on_load_started)
            
            logger.debug("Signal connections setup successfully")
            
        except Exception as e:
            logger.error("Error setting up connections", exception=e)
    
    @ErrorHandler.handle_exception
    def _navigate_to_url(self):
        """Navigate to URL from address bar"""
        try:
            url = self.address_bar.text().strip()
            if not url:
                return
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if '.' in url:
                    url = 'https://' + url
                else:
                    # Treat as search query
                    url = f"https://www.google.com/search?q={url}"
            
            logger.info(f"Navigating to: {url}")
            self.web_view.setUrl(QUrl(url))
            self.status_bar.showMessage(f"Loading {url}...", 5000)
            
        except Exception as e:
            logger.error("Error navigating to URL", exception=e)
            self._show_error_dialog("Navigation Error", f"Failed to navigate to URL: {str(e)}")
    
    @ErrorHandler.handle_exception
    def _go_back(self):
        """Go back in history"""
        if self.web_view.history().canGoBack():
            self.web_view.back()
            logger.debug("Navigated back")
    
    @ErrorHandler.handle_exception
    def _go_forward(self):
        """Go forward in history"""
        if self.web_view.history().canGoForward():
            self.web_view.forward()
            logger.debug("Navigated forward")
    
    @ErrorHandler.handle_exception
    def _refresh_page(self):
        """Refresh current page"""
        self.web_view.reload()
        logger.debug("Page refreshed")
    
    @ErrorHandler.handle_exception
    def _go_home(self):
        """Go to home page"""
        home_url = "https://www.google.com"
        self.web_view.setUrl(QUrl(home_url))
        logger.debug("Navigated to home page")
    
    def _new_tab(self):
        """Create new tab (placeholder for future implementation)"""
        logger.info("New tab requested (not implemented yet)")
        self.status_bar.showMessage("New tab feature coming soon!", 3000)
    
    def _close_current_tab(self):
        """Close current tab (placeholder for future implementation)"""
        logger.info("Close tab requested (not implemented yet)")
        self.status_bar.showMessage("Close tab feature coming soon!", 3000)
    
    def _on_url_changed(self, url):
        """Handle URL change"""
        url_str = url.toString()
        self.address_bar.setText(url_str)
        self.url_changed.emit(url_str)
        logger.debug(f"URL changed to: {url_str}")
    
    def _on_load_started(self):
        """Handle page load start"""
        self.status_bar.showMessage("Loading...", 0)
        logger.debug("Page load started")
    
    def _on_load_finished(self, success):
        """Handle page load completion"""
        if success:
            self.status_bar.showMessage("Page loaded", 2000)
            current_url = self.web_view.url().toString()
            self.page_loaded.emit(current_url)
            logger.info(f"Page loaded successfully: {current_url}")
        else:
            self.status_bar.showMessage("Failed to load page", 5000)
            logger.warning("Page failed to load")
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About AI-Powered Browser", 
                         "AI-Powered Browser v1.0\n"
                         "A modern browser with AI capabilities\n"
                         "Built with PyQt6")
    
    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog to user"""
        QMessageBox.critical(self, title, message)
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            logger.info("Browser window closing")
            event.accept()
        except Exception as e:
            logger.error("Error during window close", exception=e)
            event.accept()

def create_application() -> QApplication:
    """Create and configure QApplication"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("AI-Powered Browser")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("PyScrape")
        
        # Set application style
        app.setStyle('Fusion')
        
        logger.info("QApplication created successfully")
        return app
        
    except Exception as e:
        logger.error("Failed to create QApplication", exception=e)
        raise BrowserError("Failed to create application") from e

def main():
    """Main function to run the browser"""
    try:
        # Create application
        app = create_application()
        
        # Create and show main window
        window = BrowserWindow()
        window.show()
        
        logger.info("Browser application started")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical("Fatal error in main function", exception=e)
        sys.exit(1)

if __name__ == "__main__":
    main()
