import logging
import sys
import os

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aimassist.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import vgamepad
    except ImportError:
        missing_deps.append("vgamepad")
    
    try:
        import pynput
    except ImportError:
        missing_deps.append("pynput")
    
    return missing_deps

def check_pyqt6():
    """Check if PyQt6 is available"""
    try:
        import PyQt6
        return True
    except ImportError:
        return False

def show_dependency_error(missing_deps):
    """Show error dialog for missing dependencies"""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    
    deps_text = "\n".join([f"• {dep}" for dep in missing_deps])
    
    messagebox.showerror(
        "Missing Dependencies",
        f"The following required modules are not installed:\n\n{deps_text}\n\n"
        f"Please install them using:\n\n"
        f"pip install {' '.join(missing_deps)}\n\n"
        f"Or if you are using conda:\n"
        f"conda install -c conda-forge pynput\n"
        f"pip install vgamepad"
    )
    root.destroy()

def launch_pyqt6_version():
    """Launch the application"""
    try:
        from gui import main as gui_main
        logger.info("Starting Aim Assist")
        gui_main()
    except Exception as e:
        logger.error(f"PyQt6 version failed: {e}")
        raise


def main():
    """Main application entry point"""
    try:
        missing_deps = check_dependencies()
        if missing_deps:
            show_dependency_error(missing_deps)
            return

        pyqt6_available = check_pyqt6()
        
        if pyqt6_available:
            try:
                launch_pyqt6_version()
            except Exception as e:
                logger.warning(f"Failed to start: {e}")
        else:
            return

    except ImportError as e:
        logger.error(f"Import error: {e}")
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown module"
        
        messagebox.showerror(
            "Missing Dependency",
            f"Required module not found: {missing_module}\n\n"
            f"Install dependencies with:\n"
            f"pip install vgamepad pynput\n\n"
            f"or if you are using conda:\n"
            f"conda install -c conda-forge pynput\n"
            f"pip install vgamepad"
        )
        root.destroy()
        return
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "Fatal Error",
            f"Unexpected error occurred while starting the application:\n\n{e}\n\n"
            f"Please ensure that:\n"
            f"1. All dependencies are installed\n"
            f"2. You have the necessary permissions\n"
            f"3. No other conflicting programs are running\n\n"
            f"Check the log file 'aimassist.log' for more details."
        )
        root.destroy()
        return

if __name__ == "__main__":
    main()