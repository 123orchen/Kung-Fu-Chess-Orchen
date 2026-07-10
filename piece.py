class Piece:
    def __init__(self, color, type):
        self._color = color
        self._type = type

    @property
    def color(self):
        return self._color


    @property
    def type(self):
        return self._type

    def is_jumping(self):
        # רק סוס יכול לקפוץ
        return self._type == 'N'

    def get_delta(self, dr, dc):
        # מחזיר כיוון צעד (1, 0, -1) למסלול
        return (0 if dr == 0 else dr // abs(dr),
                0 if dc == 0 else dc // abs(dc))

    def is_valid_move(self, dr, dc, is_capture=False):
        # חוקי חיילים
        if self._type == 'P':
            direction = -1 if self._color == 'w' else 1
            if is_capture:
                # תפיסה: צעד אחד אלכסוני (dc=1 או -1)
                return dr == direction and abs(dc) == 1
            else:
                # תנועה רגילה: צעד אחד קדימה ללא תפיסה
                return dr == direction and dc == 0

        # חוקי שאר הכלים (שלא משתנים בין תפיסה לתנועה)
        rules = {
            'K': lambda dr, dc: abs(dr) <= 1 and abs(dc) <= 1,
            'R': lambda dr, dc: dr == 0 or dc == 0,
            'B': lambda dr, dc: abs(dr) == abs(dc),
            'Q': lambda dr, dc: abs(dr) == abs(dc) or dr == 0 or dc == 0,
            'N': lambda dr, dc: {abs(dr), abs(dc)} == {1, 2},
            'P': lambda dr, dc: dr == -1 and dc == 0  # חייל לבן פשוט
        }
        return rules.get(self._type, lambda dr, dc: False)(dr, dc)


    @staticmethod
    def is_valid_token(token):
        if token == '.': return True
        if len(token) != 2: return False
        return token[0] in 'wb' and token[1] in 'KQRBNP'

    def __str__(self):
        return f"{self._color}{self._type}"