from math import ceil


class File:
    def __init__(self, path: str):
        assert path != None
        assert type(path) is str
        assert len(path) > 0

        self.path = path

    def filesize(self):
        with open(self.path, 'rb') as file:
            file.seek(0, 2)
            return file.tell()

    def countSegment(self):
        fileSize = self.filesize()
        return ceil(fileSize / 32768)

    def fileBuffer(self):
        with open(self.path, 'rb') as file:
            return file