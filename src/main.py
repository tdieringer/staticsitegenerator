import os
import shutil
import sys
from textnode import TextNode, TextType
from blocktypes import markdown_to_html_node  # Assumes this is defined in blocktypes.py

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
    Extracts the h1 header (a line starting with a single '# ') from the given markdown text.
    Returns the header text with the '#' and any leading/trailing whitespace removed.
    If no h1 header is found, raises an Exception.
    """
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No h1 header found in markdown")

def generate_page(from_path, template_path, dest_path, basepath):
    """
    Generates an HTML page by:
      - Reading a markdown file from from_path.
      - Reading a template HTML file from template_path.
      - Converting the markdown to HTML using markdown_to_html_node().
      - Extracting the page title from the markdown using extract_title().
      - Replacing the {{ Title }} and {{ Content }} placeholders in the template.
      - Then replacing any href="/ and src="/ with the provided basepath.
      - Writing the resulting HTML to dest_path.
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
    
    # Replace placeholders.
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    # Update all absolute paths in href and src attributes with the basepath.
    full_html = full_html.replace('href="/', f'href="{basepath}')
    full_html = full_html.replace('src="/', f'src="{basepath}')
    
    # Ensure the destination directory exists.
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the final HTML.
    with open(dest_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(full_html)
    
    print(f"Page generated successfully at {dest_path}")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    """
    Recursively crawls the content directory (dir_path_content) and, for every markdown file found,
    generates an HTML page (using generate_page) in the dest_dir_path directory, preserving the same directory structure.
    """
    for root, dirs, files in os.walk(dir_path_content):
        for file in files:
            if file.lower().endswith(".md"):
                src_file = os.path.join(root, file)
                # Compute relative path from the content directory.
                rel_path = os.path.relpath(src_file, dir_path_content)
                # Change the .md extension to .html.
                rel_html = os.path.splitext(rel_path)[0] + ".html"
                dest_file = os.path.join(dest_dir_path, rel_html)
                print(f"Generating page for {src_file} -> {dest_file}")
                generate_page(src_file, template_path, dest_file, basepath)

def main():
    # Get the basepath from command-line arguments; default to "/" if none provided.
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    
    project_root = os.getcwd()
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    
    # Step 1: Delete anything in the public directory and copy static files there.
    print("Copying static files...")
    copy_static(static_dir, public_dir)
    
    # Step 2: Generate a page for every markdown file in the content directory.
    print("Generating pages recursively...")
    generate_pages_recursive(content_dir, template_path, public_dir, basepath)
    
    print("Site generation complete!")

if __name__ == "__main__":
    main()
