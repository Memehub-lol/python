class ImageExceptions:
    class IsDeleted(Exception):
        pass

    class NoImage(Exception):
        pass

    class MalformedImage(Exception):
        pass
