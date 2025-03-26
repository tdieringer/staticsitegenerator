import os
import sys
import shutil
from textnode import TextNode, TextType
from blocktypes import markdown_to_html_node  # Assumes this function is defined in blocktypes.py

def copy_static(src, dest):
    """
    Recursively copy all files and subdirectories from src to dest.
    Deletes dest if it exists to ensure a clean copy.
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

def generate_page(from_path, template_path, dest_path, basepath):
    """
    Reads a markdown file from from_path and a template file from template_path.
    Converts the markdown to HTML using markdown_to_html_node, extracts the title using extract_title,
    replaces the {{ Title }} and {{ Content }} placeholders, and also replaces
    any instances of href="/ with href="{basepath} and src="/ with src="{basepath}.
    Writes the resulting HTML to dest_path.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    with open(from_path, "r", encoding="utf-8") as md_file:
        markdown_content = md_file.read()
    
    with open(template_path, "r", encoding="utf-8") as tpl_file:
        template_content = tpl_file.read()
    
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    title = extract_title(markdown_content)
    
    # Replace placeholders and update root-relative links
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    full_html = full_html.replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')
    
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    with open(dest_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(full_html)
    
    print(f"Page generated successfully at {dest_path}")

def generate_pages_recursive(content_dir, template_path, dest_dir, basepath):
    """
    Recursively crawls the content directory.
    For each markdown (.md) file found, generates a corresponding HTML file
    in the destination directory (docs) while preserving the directory structure.
    """
    for entry in os.listdir(content_dir):
        entry_path = os.path.join(content_dir, entry)
        if os.path.isdir(entry_path):
            new_dest_dir = os.path.join(dest_dir, entry)
            if not os.path.exists(new_dest_dir):
                os.makedirs(new_dest_dir)
            generate_pages_recursive(entry_path, template_path, new_dest_dir, basepath)
        else:
            if entry.lower().endswith(".md"):
                dest_filename = os.path.splitext(entry)[0] + ".html"
                dest_path = os.path.join(dest_dir, dest_filename)
                print(f"Generating page for {entry_path} -> {dest_path}")
                generate_page(entry_path, template_path, dest_path, basepath)

def main():
    # Get basepath from command-line arguments (default to "/")
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    print(f"Basepath set to: {basepath}")
    
    project_root = os.getcwd()
    static_dir = os.path.join(project_root, "static")
    content_dir = os.path.join(project_root, "content")
    docs_dir = os.path.join(project_root, "docs")  # Using docs instead of public
    template_path = os.path.join(project_root, "template.html")
    
    # Step 1: Copy static files into the docs directory
    print("Copying static files...")
    copy_static(static_dir, docs_dir)
    
    # Step 2: Generate pages recursively from content to docs
    print("Generating pages recursively...")
    generate_pages_recursive(content_dir, template_path, docs_dir, basepath)
    
    print("Site generation complete!")

if __name__ == "__main__":
    main()
