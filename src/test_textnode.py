import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_noteq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.LINK)
        self.assertNotEqual(node, node2)
        
    def test_not_equal_different_text(self):
        node1 = TextNode("Text A", TextType.BOLD)
        node2 = TextNode("Text B", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_equal_with_none_url(self):
        node1 = TextNode("Anchor", TextType.LINK, None)
        node2 = TextNode("Anchor", TextType.LINK)
        self.assertEqual(node1, node2)

    def test_not_equal_different_url(self):
        node1 = TextNode("Anchor", TextType.LINK, "http://a.com")
        node2 = TextNode("Anchor", TextType.LINK, "http://b.com")
        self.assertNotEqual(node1, node2)

if __name__ == "__main__":
    unittest.main()