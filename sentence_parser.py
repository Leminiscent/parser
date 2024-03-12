import nltk
from nltk.tokenize import word_tokenize
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
NP -> N | Det N | Det AdjP N | NP PP
VP -> V | V NP | V NP PP | V PP | VP Adv | Adv VP
AdjP -> Adj | Adj AdjP
PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()
    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words, lowercased and filtered for alphabetic content.
    """
    tokens = word_tokenize(sentence.lower())
    words = [word for word in tokens if any(c.isalpha() for c in word)]
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as an NP that does not contain any other NPs within it.
    """
    np_chunks = []

    # Recursively find NP chunks without nested NPs
    def find_np_chunks(t):
        # Assume the current NP is valid unless a nested NP is found
        is_valid_np = t.label() == "NP"
        for child in t:
            # Recursively check children; if a child is an NP, the current NP is not valid
            if isinstance(child, nltk.Tree):
                if child.label() == "NP":
                    is_valid_np = False
                else:
                    find_np_chunks(child)
        if is_valid_np:
            np_chunks.append(t)

    # Start the recursive search from the top of the tree
    for subtree in tree.subtrees(lambda t: t.label() == "NP"):
        find_np_chunks(subtree)

    # Filter out the nested NPs, leaving only the highest-level NPs in nested structures
    final_np_chunks = []
    for np in np_chunks:
        if not any(
            np in list(subtree.subtrees()) for subtree in np_chunks if subtree != np
        ):
            final_np_chunks.append(np)

    return final_np_chunks


if __name__ == "__main__":
    main()
