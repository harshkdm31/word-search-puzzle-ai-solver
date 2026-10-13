
class TrieNode:
    """A single node in the Trie."""

    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    """Prefix tree for storing and searching words."""

    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    @staticmethod
    def _normalize(word):
        """Normalize a word and reject invalid input."""
        if not isinstance(word, str):
            raise ValueError("Word must be a string.")

        word = "".join(word.split()).upper()

        if not word or not word.isascii() or not word.isalpha():
            raise ValueError("Word must contain English letters only.")

        return word

    def insert(self, word):
        """Insert a word into the Trie."""
        word = self._normalize(word)
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        if not node.is_word:
            node.is_word = True
            self.word_count += 1

    def search(self, word):
        """Return True if the complete word exists."""
        word = self._normalize(word)
        node = self.root

        for char in word:
            if char not in node.children:
                return False

            node = node.children[char]

        return node.is_word

    def starts_with(self, prefix):
        """Return True if any stored word has this prefix."""
        prefix = self._normalize(prefix)
        node = self.root

        for char in prefix:
            if char not in node.children:
                return False

            node = node.children[char]

        return True

    def __len__(self):
        """Return the number of distinct stored words."""
        return self.word_count
