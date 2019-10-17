
class MagicalBeast:

    def __init__(self, kind, picture_uri):
        self.kind = kind
        self.picture_uri = picture_uri


def get_random_magical_beast():
    return MagicalBeast("Hippogriff"
                        , "https://vignette.wikia.nocookie.net/harrypotter/images/a/a6/Hippogrif_FBCFWW.png")


def get_magical_beast_by_kind(kind):
    return MagicalBeast("Hippogriff"
                        , "https://vignette.wikia.nocookie.net/harrypotter/images/a/a6/Hippogrif_FBCFWW.png")
