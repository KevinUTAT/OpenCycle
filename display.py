

class Display(object):

    def __init__(self):
        self.csc_screen = False
        self.msg_screen = False

    def test_msg(self):
        if not hasattr(self, "show_msg"):
            return
        self.show_msg(\
            "A title here", "abcdefg", "qwerty", "!@#$%^&*()_+")
        
    def test_csc(self):
        if not hasattr(self, "show_csc"):
            return
        speed = 100 / 3
        distance = 50 / 3
        rpm = 20 / 3
        raw = [1, 12571, 54302]
        self.show_csc(\
            speed, distance, rpm, raw)
