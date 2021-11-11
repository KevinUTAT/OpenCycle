

class Display(object):

    def __init__(self):
        self.csc_screen = False

    def test_msg(self):
        if not hasattr(self, "show_msg"):
            return
        self.show_msg(\
            "A title here", "abcdefg", "qwerty", "!@#$%^&*()_+")
