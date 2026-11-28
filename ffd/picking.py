import numpy as np
import OpenGL.GL as gl
from colour_generator import RGB, colour_generator
from PIL import Image


def colour_to_float(colour: RGB) -> tuple[float, float, float, float]:
    r, g, b = colour
    return r / 255.0, g / 255.0, b / 255.0, 1.0


def colours_in_pixels(pixels: np.ndarray, background: RGB = (0, 0, 0)) -> set[RGB]:
    """Return every unique colour bar the background in an (h, w, 3) or (n, 3) uint8 array."""
    flat = np.asarray(pixels, dtype=np.uint8).reshape(-1, 3)
    unique = np.unique(flat, axis=0)
    return {(int(r), int(g), int(b)) for r, g, b in unique} - {background}


def nearest_colour(pixels: np.ndarray, background: RGB = (0, 0, 0)) -> RGB | None:
    """Return the non background colour closest to the centre of a small (h, w, 3) block.

    Clicking exactly on a 5 pixel cube is fiddly, so we read a small block
    around the mouse and take the hit nearest the cursor.
    """
    block = np.asarray(pixels, dtype=np.uint8)
    hits = np.argwhere(np.any(block != np.array(background, dtype=np.uint8), axis=2))
    if len(hits) == 0:
        return None
    centre = (np.array(block.shape[:2]) - 1) / 2.0
    row, col = hits[np.argmin(np.sum((hits - centre) ** 2, axis=1))]
    r, g, b = block[row, col]
    return int(r), int(g), int(b)


def pick_region(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    width: int,
    height: int,
    ratio: float = 1.0,
) -> tuple[int, int, int, int] | None:
    """Turn two Qt mouse positions into a GL read rectangle.

    Qt gives us logical pixels with the origin top left, GL wants device pixels
    with the origin bottom left. The corners can be in any order and the result
    is clamped to the window.

    Parameters
    ----------
    x0, y0, x1, y1 : float
        The two corners in Qt logical coordinates.
    width, height : int
        The framebuffer size in device pixels.
    ratio : float
        The device pixel ratio of the window.

    Returns
    -------
    tuple[int, int, int, int] | None
        (x, y, w, h) for glReadPixels, or None if the region is off screen.
    """
    left = int(min(x0, x1) * ratio)
    right = int(max(x0, x1) * ratio)
    top = int(min(y0, y1) * ratio)
    bottom = int(max(y0, y1) * ratio)
    left, right = max(left, 0), min(right, width - 1)
    top, bottom = max(top, 0), min(bottom, height - 1)
    if left > right or top > bottom:
        return None
    # flip y as GL starts at the bottom
    return left, height - 1 - bottom, right - left + 1, bottom - top + 1


class PickBuffer:
    def __init__(self) -> None:
        self._fbo = None
        self._colour_rbo = None
        self._depth_rbo = None
        self._width = 0
        self._height = 0

    def resize(self, width: int, height: int) -> None:
        if (width, height) == (self._width, self._height) and self._fbo is not None:
            return
        self.release()
        self._width = width
        self._height = height
        self._fbo = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._fbo)
        # add the colour buffer
        self._colour_rbo = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._colour_rbo)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_RGBA8, width, height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_RENDERBUFFER, self._colour_rbo)
        # add the depth buffer
        self._depth_rbo = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._depth_rbo)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT24, width, height)

        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, self._depth_rbo)

        if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("pick framebuffer is incomplete")
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def release(self):
        if self._fbo is not None:
            gl.glDeleteRenderbuffers(2, [self._colour_rbo, self._depth_rbo])
            gl.glDeleteFramebuffers(1, [self._fbo])
            self._fbo = None

    def bind(self) -> None:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._fbo)
        gl.glViewport(0, 0, self._width, self._height)
        self._previousClearColour = gl.glGetFloatv(gl.GL_COLOR_CLEAR_VALUE)
        clear_colour = colour_generator.background
        gl.glClearColor(*clear_colour, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glClearColor(*self._previousClearColour)

    def read(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._fbo)
        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        data = gl.glReadPixels(x, y, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        return np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)

    def save_png(self, file_name: str) -> None:
        if self._fbo is None:
            raise RuntimeError("need fbo")
        previous_fbo = int(gl.glGetIntegerv(gl.GL_READ_FRAMEBUFFER_BINDING))
        previous_alinment = int(gl.glGetIntegerv(gl.GL_PACK_ALIGNMENT))

        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self._fbo)
        pixels = self.read(0, 0, self._width, self._height)
        Image.fromarray(np.flipud(pixels)).save(file_name, format="PNG")
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, previous_alinment)
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, previous_fbo)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exec_type, exc_val, exc_tb):
        self.unbind()
