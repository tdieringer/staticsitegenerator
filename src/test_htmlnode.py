import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_link, split_nodes_image, text_to_textnodes, markdown_to_blocks
from textnode import TextNode, TextType

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_multiple_attributes(self):
        props = {"href": "https://google.com", "target": "_blank"}
        node = HTMLNode(tag="a", props=props)
        result = node.props_to_html()
        expected = ' href="https://google.com" target="_blank"'
        self.assertEqual(result, expected)

    def test_props_to_html_empty(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.props_to_html(), "")

    def test_repr_output(self):
        node = HTMLNode(tag="p", value="Hello, world!", props={"class": "intro"})
        expected = "HTMLNode(tag=p, value=Hello, world!, children=[], props={'class': 'intro'})"
        self.assertEqual(repr(node), expected)

    def test_children_default_empty(self):
        node = HTMLNode(tag="div")
        self.assertEqual(node.children, [])

    def test_props_default_empty_dict(self):
        node = HTMLNode(tag="div")
        self.assertEqual(node.props, {})

    def test_to_html_raises(self):
        node = HTMLNode(tag="p", value="Test")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_basic_tag(self):
        node = LeafNode("em", "Italic text")
        self.assertEqual(node.to_html(), "<em>Italic text</em>")

    def test_leaf_to_html_no_tag_returns_value(self):
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leaf_to_html_with_props(self):
        props = {"class": "highlight", "id": "intro"}
        node = LeafNode("div", "Welcome!", props)
        self.assertEqual(node.to_html(), '<div class="highlight" id="intro">Welcome!</div>')

    def test_leaf_to_html_empty_string_value(self):
        node = LeafNode("span", "")
        self.assertEqual(node.to_html(), "<span></span>")

    def test_leaf_to_html_raises_if_value_is_none(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

    def test_leaf_to_html_ignores_children_argument(self):
        # Even if someone tries to pass children manually, it should not affect behavior
        node = LeafNode("p", "No children", props={"data-test": "true"})
        # Just ensuring it still works
        self.assertEqual(node.to_html(), '<p data-test="true">No children</p>')

    def test_leaf_to_html_special_characters_in_value(self):
        node = LeafNode("p", "Use <code> tags & symbols!")
        self.assertEqual(node.to_html(), "<p>Use <code> tags & symbols!</p>")

    def test_leaf_to_html_self_closing_tag_simulation(self):
        # This isn't required, but good to test if someone uses tags like 'img'
        node = LeafNode("img", "", {"src": "image.png", "alt": "An image"})
        self.assertEqual(node.to_html(), '<img src="image.png" alt="An image"></img>')  # HTML5 allows self-closing, but our code returns full tag

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")    

    def test_bold(self):
        node = TextNode("Bold!", TextType.BOLD)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "b")
        self.assertEqual(html.value, "Bold!")

    def test_image(self):
        node = TextNode("A cat", TextType.IMAGE, "https://cat.png")
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "img")
        self.assertEqual(html.value, "")
        self.assertEqual(html.props, {"src": "https://cat.png", "alt": "A cat"})

    def test_invalid_type(self):
        class FakeTextType:
            pass
        node = TextNode("Oops", FakeTextType())
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_split_code(self):
        node = TextNode("Some `inline code` here", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "Some ")
        self.assertEqual(result[1].text, "inline code")
        self.assertEqual(result[1].text_type, TextType.CODE)
        self.assertEqual(result[2].text, " here")

    def test_extract_markdown_images(self):
        text = "Check this out ![cat](https://i.imgur.com/cat.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("cat", "https://i.imgur.com/cat.png")], matches)

    def test_extract_markdown_links(self):
        text = "Visit [Boot.dev](https://www.boot.dev) and [YouTube](https://youtube.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([
            ("Boot.dev", "https://www.boot.dev"),
            ("YouTube", "https://youtube.com")
        ], matches)

    def test_mixed_images_and_links(self):
        text = "Image ![alt](https://img.png) and link [text](https://site.com)"
        image_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([("alt", "https://img.png")], image_matches)
        self.assertListEqual([("text", "https://site.com")], link_matches)

    def test_no_matches(self):
        text = "This text has no links or images."
        self.assertEqual(extract_markdown_images(text), [])
        self.assertEqual(extract_markdown_links(text), [])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is a [link](https://example.com) and another [thing](https://thing.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("thing", TextType.LINK, "https://thing.com"),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        self.maxDiff = None
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        result = text_to_textnodes(text)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]

        self.assertEqual(result, expected)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ]
        self.assertEqual(blocks, expected)


if __name__ == "__main__":
    unittest.main()