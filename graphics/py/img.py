from __future__ import annotations

import pathlib

import cv2
import numpy as np

class Img:
    def __init__(self):
        self.img = None

    def read(self, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        """
        Load `path` into self.img and **optionally resize**.

        Parameters
        ----------
        path : str | Path
            Image file to load.
        size : (width, height) | None
            Target size in pixels.  If None, keep original.
        keep_aspect : bool
            • False  → resize exactly to `size`
            • True   → shrink so the *longer* side fits `size` while
                       preserving aspect ratio (no cropping).
        interpolation : OpenCV flag
            E.g.  `cv2.INTER_AREA` for shrink, `cv2.INTER_LINEAR` for enlarge.

        Returns
        -------
        Img
            `self`, so you can chain:  `sprite = Img().read("foo.png", (64,64))`
        """
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self

    def draw_on(self, canvas: Img, x: int, y: int):
        """Draws this image onto another canvas using alpha transparency"""
        h, w = self.img.shape[:2]
        canvas_h, canvas_w = canvas.img.shape[:2]

        # חישוב גבולות כדי למנוע חריגה מהקנבס
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(canvas_w, x + w), min(canvas_h, y + h)
        
        if x1 >= x2 or y1 >= y2:
            return

        # חיתוך חלק התמונה שמופיע בתוך גבולות המסך
        s_x1, s_y1 = x1 - x, y1 - y
        s_x2, s_y2 = s_x1 + (x2 - x1), s_y1 + (y2 - y1)
        
        target = canvas.img[y1:y2, x1:x2]
        source = self.img[s_y1:s_y2, s_x1:s_x2]

        # אם לתמונה יש 4 ערוצים (BGRA), נשתמש בשקיפות
        if source.shape[2] == 4:
            alpha = source[:, :, 3] / 255.0
            alpha_inv = 1.0 - alpha
            
            for c in range(3): # B, G, R
                target[:, :, c] = (alpha * source[:, :, c] + alpha_inv * target[:, :, c])
        else:
            # אם אין אלפא, פשוט נדביק (למקרים של תמונות בלי שקיפות)
            target[:] = source[:, :, :3]

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    def show(self):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
