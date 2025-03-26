import re
from enum import Enum
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, text_to_textnodes, markdown_to_blocks
from textnode import TextNode, TextType

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block: str) -> BlockType:
    # Check for code block: must start and end with triple backticks.
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    # Check for heading: starts with 1-6 '#' characters followed by a space.
    if re.match(r'^(#{1,6})\s', block):
        return BlockType.HEADING

    # Split block into lines to handle multi-line blocks.
    lines = block.splitlines()

    # Check for quote block: every line starts with '>'.
    if lines and all(line.startswith('>') for line in lines):
        return BlockType.QUOTE

    # Check for unordered list block: every line starts with '- '.
    if lines and all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST

    # Check for ordered list block: every line must start with a number followed by '. ' and numbers must increment.
    if lines:
        ordered = True
        expected_num = 1
        for line in lines:
            m = re.match(r'^(\d+)\.\s', line)
            if not m:
                ordered = False
                break
            num = int(m.group(1))
            if num != expected_num:
                ordered = False
                break
            expected_num += 1
        if ordered:
            return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def text_to_children(text: str):
    """
    Convert an inline markdown string into a list of HTML child nodes.
    """
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(tn) for tn in text_nodes]

def markdown_to_html_node(markdown: str):
    """
    Convert a full markdown document into a single ParentNode (<div>) containing
    child HTMLNodes representing each block.
    """
    blocks = markdown_to_blocks(markdown)
    block_nodes = []

    for block in blocks:
        bt = block_to_block_type(block)

        if bt == BlockType.CODE:
            # Remove the starting and ending triple backticks.
            lines = block.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            code_content = "\n".join(lines)
            # Ensure code content ends with a newline
            if code_content and not code_content.endswith("\n"):
                code_content += "\n"
            code_leaf = LeafNode("code", code_content)
            code_node = ParentNode("pre", [code_leaf])
            block_nodes.append(code_node)

        elif bt == BlockType.HEADING:
            # Match heading level and content.
            m = re.match(r'^(#{1,6})\s+(.*)', block)
            if m:
                level = len(m.group(1))
                content = m.group(2)
                children = text_to_children(content)
                heading_node = ParentNode(f"h{level}", children)
                block_nodes.append(heading_node)
            else:
                children = text_to_children(block)
                block_nodes.append(ParentNode("p", children))

        elif bt == BlockType.QUOTE:
            # Remove leading '>' from each line.
            lines = [line.lstrip(">").strip() for line in block.splitlines()]
            content = "\n".join(lines)
            children = text_to_children(content)
            quote_node = ParentNode("blockquote", children)
            block_nodes.append(quote_node)

        elif bt == BlockType.UNORDERED_LIST:
            # Process each line starting with '- '.
            items = []
            for line in block.splitlines():
                if line.startswith("- "):
                    item_content = line[2:].strip()
                    li_children = text_to_children(item_content)
                    li_node = ParentNode("li", li_children)
                    items.append(li_node)
            ul_node = ParentNode("ul", items)
            block_nodes.append(ul_node)

        elif bt == BlockType.ORDERED_LIST:
            # Process each line starting with a number, dot, and space.
            items = []
            for line in block.splitlines():
                m = re.match(r'^(\d+)\.\s+(.*)', line)
                if m:
                    item_content = m.group(2).strip()
                    li_children = text_to_children(item_content)
                    li_node = ParentNode("li", li_children)
                    items.append(li_node)
            ol_node = ParentNode("ol", items)
            block_nodes.append(ol_node)

        else:
            # Default is a paragraph.
            # Replace internal newlines with a space.
            normalized_text = " ".join(block.splitlines())
            children = text_to_children(normalized_text)
            p_node = ParentNode("p", children)
            block_nodes.append(p_node)

    return ParentNode("div", block_nodes)
