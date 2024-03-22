import os
import shutil
import re


def clear_directory_except(directory, exceptions):
    """
    Clears the directory except for the files and directories specified in exceptions.

    :param directory: The directory to clear.
    :param exceptions: A list of filenames or directory names to exclude from deletion.
    """
    for item in os.listdir(directory):
        if item not in exceptions:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    print(f"Cleared directory {directory} except for {exceptions}")


def main():
    # Adjust the base path to point to the QuantumCheckersWebApp directory
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Set the path for the React project
    react_project_path = os.path.join(base_path, 'quantum-checkers-ui')  # Adjusted path

    # Correct the paths for static and template directories
    django_static_path = os.path.join(base_path, 'qgame', 'game', 'static', 'game')
    django_templates_path = os.path.join(base_path, 'qgame', 'game', 'templates', 'game')

    # Ensure the target directories exist
    os.makedirs(django_static_path, exist_ok=True)
    os.makedirs(django_templates_path, exist_ok=True)

    # Clear the django_static_path directory except for .gitignore and .gitkeep
    clear_directory_except(django_static_path, ['.gitignore', '.gitkeep'])

    # Build the React project
    os.chdir(react_project_path)
    os.system('npm run build')

    # Move the built index.html to Django templates and update it
    index_html_path = os.path.join(react_project_path, 'build', 'index.html')
    update_and_move_index_html(index_html_path, django_templates_path)

    # Move the rest of the build directory to Django's static files directory
    move_static_files(react_project_path, django_static_path)


def update_and_move_index_html(source_path, templates_path):

    if os.path.exists(source_path):
        # Read the original HTML content
        with open(source_path, 'r') as file:
            html_content = file.read()

        # Perform replacements
        html_content = update_html_for_django_static(html_content)

        # Write the updated HTML to the new location
        destination_path = os.path.join(templates_path, 'index.html')
        with open(destination_path, 'w') as file:
            file.write(html_content)

        print("index.html has been updated and moved successfully.")


def update_html_for_django_static(html_content):
    # Add {% load static %} right after <!doctype html> on the same line
    updated_html = re.sub(
        r'(<\!doctype html>)',
        r'\1{% load static %}',
        html_content,
        flags=re.IGNORECASE
    )

    # Replace all src and href attributes for JS and CSS to use Django static
    updated_html = re.sub(
        r'(src|href)="/static/(js|css)/([^"]+)"',
        r'\1="{% static \'game/static/\2/\3\' %}"',
        updated_html
    )

    # Handle the root directory static files like manifest.json, favicon.ico, logo192.png
    updated_html = re.sub(
        r'(src|href)="/(manifest.json|favicon.ico|logo192.png|asset-manifest.json|robots.txt|logo512.png)"',
        r'\1="{% static \'game/\2\' %}"',
        updated_html
    )

    # Fix the paths by removing any incorrect static path constructions and extra backslashes
    updated_html = updated_html.replace("static '/static/", "static '").replace('\\', '')

    return updated_html



def move_static_files(react_project_path, static_path):
    build_path = os.path.join(react_project_path, 'build')

    if os.path.exists(build_path):
        for item in os.listdir(build_path):
            source = os.path.join(build_path, item)
            destination = os.path.join(static_path, item)
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                if item != 'index.html':  # Skip index.html since it's already been moved
                    shutil.copy2(source, destination)
        print("Static files have been moved successfully.")


if __name__ == "__main__":
    main()

