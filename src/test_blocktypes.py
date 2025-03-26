import unittest
from blocktypes import BlockType, block_to_block_type, markdown_to_html_node # adjust import as needed

class TestBlockTypes(unittest.TestCase):
    def test_heading(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        
        block = "###### Another heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_code_block(self):
        block = "```python\nprint('Hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_block(self):
        block = "> This is a quote\n> spanning multiple lines"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- First item\n- Second item\n- Third item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_invalid(self):
        # Numbers not incrementing properly; should be a paragraph
        block = "1. First item\n3. Second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph(self):
        block = "This is just a paragraph of text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """\
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = ("<div>"
                        "<p>This is <b>bolded</b> paragraph text in a p tag here</p>"
                        "<p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p>"
                    "</div>")
        self.assertEqual(html, expected)

    def test_codeblock(self):
        md = (
            "```\n"
            "This is text that _should_ remain\n"
            "the **same** even with inline stuff\n"
            "```"
        )
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = (
            "<div>"
            "<pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre>"
            "</div>"
        )
        self.assertEqual(html, expected)

if __name__ == "__main__":
    unittest.main()
