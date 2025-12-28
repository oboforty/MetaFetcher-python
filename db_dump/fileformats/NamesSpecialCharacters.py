import collections
import string
from db_dump.parsinglib import _REPLACE_CHARS



class NamesSpecialCharacters:

    def initialize(self):
        self.words = collections.Counter()

        etc = " !#$%&()*+,-./:;<=>?@[\]^_{|}~"
        also_ok = "¹²⁷⁵⁴³⁸⁶⁹⁰βαΑΒλΓγΔ±δ→éεψôω−üèöΕΩΖïä¬Λ‐Ψ‚ζηÄ氯√≤甲环素φΗ»«₆‡†胍ú¨à®ß∂Ñ¢尿碘马酸Ôøâœ"
        quotes = set("”'") | set(_REPLACE_CHARS.keys())
        self.expected_char = set(string.ascii_lowercase+string.ascii_uppercase+string.digits+etc+also_ok) | quotes
        self.inserted = 0

    async def consume(self, data, dtype):

        if isinstance(data.names, list):
            for name in data.names:
                self.words.update( set(name) - self.expected_char )
        else:
            self.words.update(set(data.names) - self.expected_char)

        self.inserted+=1
        if self.inserted % 1000 == 0:
            self.app.print_progress(self.inserted)

    def dispose(self):
        self.app.print_progress(self.inserted)

        print("[DEBUG] unexpected characters in names:")
        for chr, cnt in self.words.most_common():
            print(f"   chr({ord(chr)})=`{chr}`      --> {cnt}")
