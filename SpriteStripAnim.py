import spritesheet

class SpriteStripAnim(object):

    def __init__(self, filename, rect, count, colorkey=None, loop=False, frames=1):
       
        self.filename = filename
        ss = spritesheet.spritesheet(filename)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames

    def iter(self):
        self.i = 0
        self.f = self.frames
        return self

    def next(self):
        if self.i >= len(self.images):
            if not self.loop:
                raise StopIteration
            else:
                self.i = 0
        image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            self.i += 1
            self.f = self.frames
        return image

    def __add__(self, ss):
        self.images.extend(ss.images)
        return self