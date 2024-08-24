import sys
import subprocess
import importlib.metadata

# Load the required packages from the requirements.txt file
with open('requirements.txt') as f:
    REQUIRED_PACKAGES = [line.strip() for line in f if line.strip() and not line.startswith('#')]


def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        sys.exit(1)


def check_and_install_packages():
    """Check for missing packages and install them."""
    installed_packages = {pkg.metadata["Name"].lower() for pkg in importlib.metadata.distributions()}
    missing_packages = [pkg for pkg in REQUIRED_PACKAGES if pkg.lower() not in installed_packages]

    if missing_packages:
        print(f"Missing packages detected: {missing_packages}")
        for package in missing_packages:
            install_package(package)
        print("All required packages are installed.")
        # Return True to indicate that packages were installed and the app should restart
        return True
    else:
        print("All required packages are already installed.")
        return False


def relaunch_app():
    """Relaunch the application after installing missing packages."""
    try:
        print("Relaunching the application...")
        subprocess.check_call([sys.executable, *sys.argv])
    except subprocess.CalledProcessError as e:
        print(f"Failed to relaunch the application: {e}")
        sys.exit(1)

from gui.app import App

def main():
    print("Starting the application...")
    # Import setup_database after ensuring all packages are installed
    from db.setup import setup_database
    setup_database()
    # Add more functionality as needed
    app = App()
    app.mainloop()


if __name__ == '__main__':
    if check_and_install_packages():
        # Relaunch the application if packages were installed
        relaunch_app()
    else:
        # If no packages were installed, proceed with the normal execution
        main()
