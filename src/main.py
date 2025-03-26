import os
import shutil
from textnode import TextNode, TextType
from blocktypes import markdown_to_html_node  # Assumes this function is defined in blocktypes.py

##############################
# Existing functions

def copy_static(src, dest):
    """
    Recursively copies all files and subdirectories from src to dest.
    First, deletes the destination directory if it exists to ensure a clean copy.
    """
    if os.path.exists(dest):
        print(f"Deleting destination directory: {dest}")
        shutil.rmtree(dest)
    os.makedirs(dest)
    print(f"Created destination directory: {dest}")

    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dest_item = os.path.join(dest, item)
        if os.path.isdir(src_item):
            copy_static(src_item, dest_item)
        else:
            shutil.copy(src_item, dest_item)
            print(f"Copied file: {src_item} -> {dest_item}")

def extract_title(markdown):
    """
    Extracts the h1 header (a line starting with a single '# ') from the markdown text.
    Returns the header text with the '#' and any leading/trailing whitespace removed.
    If no h1 header is found, raises an Exception.
    """
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No h1 header found in markdown")

def generate_page(from_path, template_path, dest_path):
    """
    Reads a markdown file from from_path and a template HTML file from template_path.
    Uses markdown_to_html_node() to convert the markdown to HTML, and extract_title() to get the page title.
    Replaces the {{ Title }} and {{ Content }} placeholders in the template with the extracted title and generated HTML.
    Writes the resulting HTML page to dest_path, creating directories as needed.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # Read the markdown file.
    with open(from_path, "r", encoding="utf-8") as md_file:
        markdown_content = md_file.read()

    # Read the template file.
    with open(template_path, "r", encoding="utf-8") as tpl_file:
        template_content = tpl_file.read()

    # Convert markdown to HTML.
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()

    # Extract the title.
    title = extract_title(markdown_content)

    # Replace placeholders in the template.
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)

    # Ensure the destination directory exists.
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Write the final HTML page.
    with open(dest_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(full_html)

    print(f"Page generated successfully at {dest_path}")

##############################
# New: Recursive Page Generator

def generate_pages_recursive(content_dir, template_path, dest_dir):
    """
    Recursively crawls through the content directory.
    For every markdown (.md) file found, generate a new .html file in the corresponding path under dest_dir.
    """
    for entry in os.listdir(content_dir):
        entry_path = os.path.join(content_dir, entry)
        dest_entry_path = os.path.join(dest_dir, entry)
        
        if os.path.isdir(entry_path):
            # Create the corresponding destination directory if it doesn't exist.
            if not os.path.exists(dest_entry_path):
                os.makedirs(dest_entry_path)
            # Recursively process the subdirectory.
            generate_pages_recursive(entry_path, template_path, dest_entry_path)
        elif os.path.isfile(entry_path) and entry.lower().endswith('.md'):
            # Generate HTML file: replace the .md extension with .html in the destination.
            dest_html_path = os.path.splitext(dest_entry_path)[0] + ".html"
            generate_page(entry_path, template_path, dest_html_path)

##############################
# Main Function

def main():
    project_root = os.getcwd()

    # Step 1: Copy static files from static to public.
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    print("Copying static files...")
    copy_static(static_dir, public_dir)
    
    # Step 2: Generate pages recursively from the content directory.
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    # We'll generate pages under the public directory (preserving the structure).
    print("\nGenerating pages from content...")
    generate_pages_recursive(content_dir, template_path, public_dir)
    print("All pages generated successfully!")

if __name__ == "__main__":
    main()
