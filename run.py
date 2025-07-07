#!/usr/bin/env python3
"""
Simple script to run the Phastats web application.
This is a convenience script for development and testing.
"""

import os
import sys

def main():
    """Run the Flask application."""
    
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Import and run the app
    try:
        from app import app
        print("Starting Phastats Web Application...")
        print("Application directory:", current_dir)
        print("Server will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run in debug mode for development
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"Error importing app: {e}")
        print("Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 