import os
import shutil
import sys

def create_clean_structure():
    """Create a clean Django project structure"""
    
    base_dir = os.getcwd()
    print(f"Working in: {base_dir}")
    
    # Define the clean structure
    clean_structure = {
        'manage.py': None,
        'requirements.txt': None,
        '.env': None,
        'alx_travel_app/__init__.py': '',
        'alx_travel_app/settings.py': None,
        'alx_travel_app/celery.py': None,
        'alx_travel_app/urls.py': None,
        'alx_travel_app/wsgi.py': None,
        'listings/__init__.py': '',
        'listings/apps.py': None,
        'listings/models.py': '',
        'listings/views.py': '',
        'listings/urls.py': '',
    }
    
    # Create directories and files
    for file_path, default_content in clean_structure.items():
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
        
        if not os.path.exists(file_path):
            if default_content is not None:
                with open(file_path, 'w') as f:
                    if default_content != '':
                        f.write(default_content)
                print(f"✅ Created: {file_path}")
            else:
                print(f"⚠️  Need to create: {file_path}")
        else:
            print(f"✅ Already exists: {file_path}")

if __name__ == "__main__":
    create_clean_structure()