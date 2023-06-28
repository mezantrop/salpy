"""A Python class to help creating self-altering code"""

import re
import inspect


# -------------------------------------------------------------------------------------------------------------------- #
class Salpy:
    DEBUG = True

    # -=<v>=- # ------------------------------------------------------------------------------------------------------ #
    ESCAPE_START = '# -=<v>=- #'
    ESCAPE_STOP = '# -=<^>=- #'
    # -=<^>=- # ------------------------------------------------------------------------------------------------------ #

    # -=<v>=- # ------------------------------------------------------------------------------------------------------ #
    def __init__(self, file=__file__, debug=False):
        self.file = file                                                            # Script filename
        self.source_code = {}                                                       # Script code
        self.ignore_code = {}                                                       # String numbers to be ignored

    # ---------------------------------------------------------------------------------------------------------------- #
    def _make_ignore(self):
        """Populate self.ignore_code dictionary with strings to exclude from code"""
        in_ignore = False

        # Method names to ignore
        method_names = [name[0] for name in
                        inspect.getmembers(self, lambda mbs: inspect.isroutine(mbs) and not inspect.isbuiltin(mbs))]

        # Method bodies to ignore
        c = globals()['Salpy']()                                                    # Get our class by name
        for method in method_names:
            m = getattr(c, method)                                                  # Get the method by name
            mb = inspect.getsourcelines(m)                                          # Get sources of the method

            if re.search(pattern='def\s*' + method + '\s*\(', string=mb[0][0]):
                for n in range(mb[1] - 1, mb[1] - 1 + len(mb[0])):
                    self.ignore_code[n] = self.source_code[n]

        # Ignore escaped blocks of strings and method invocations
        for n in self.source_code.keys():
            if n in self.ignore_code:
                continue

            if not in_ignore and self.ESCAPE_START in self.source_code[n]:
                in_ignore = True
                self.ignore_code[n] = self.source_code[n]                           # Add ESCAPE_START tag to ignore
            elif self.ESCAPE_STOP in self.source_code[n]:
                in_ignore = False
                self.ignore_code[n] = self.source_code[n]                           # Add ESCAPE_STOP tag to ignore
            elif in_ignore:  # Add strings in an escaped block
                self.ignore_code[n] = self.source_code[n]
            else:
                for m in method_names:
                    if re.search(pattern=m + '\s*\(', string=self.source_code[n]):  # Add method invocations to ignore
                        self.ignore_code[n] = self.source_code[n]
                        break

    # ---------------------------------------------------------------------------------------------------------------- #
    def renumerate_code(self):
        self.source_code = {n: l for n, l in enumerate(self.source_code.values())}
        self.ignore_code = {n: l for n, l in enumerate(self.ignore_code.values())}

    # ---------------------------------------------------------------------------------------------------------------- #
    def read(self, file=None):
        """Read the file with code"""

        with open(file or self.file, 'r') as f:
            self.source_code = {n: l for n, l in enumerate(f.read().splitlines())}

        self._make_ignore()
        return self.source_code

    # ---------------------------------------------------------------------------------------------------------------- #
    def write(self, file=None, b=False):
        """Write the code into the file"""

        data = '\n'.join([self.source_code[n] for n in list(self.source_code.keys())])

        if not b:
            with open(file or self.file, 'w') as f:
                f.write(data)
        else:
            with open(file or self.file, 'wb') as f:
                f.write(bytes(data, 'utf-8'))

    # ---------------------------------------------------------------------------------------------------------------- #
    def find_line(self, string='', all_entries=False):
        r = []

        if not string:
            return []

        for n in self.source_code.keys():
            if n not in self.ignore_code and re.search(pattern=string, string=self.source_code[n]):
                if all_entries:
                    r.append(n)
                else:
                    return [n]

        return r

    # ---------------------------------------------------------------------------------------------------------------- #
    def find_block(self, begin='', end='', all_entries=False):

        r = []

        n1 = n2 = -1

        for n in self.source_code.keys():
            if n in self.ignore_code:
                continue

            if re.search(begin, self.source_code[n]):
                n1 = n
            elif end and re.search(end, self.source_code[n]):
                n2 = n

            if (n1 > -1 and n2 > -1) or (n1 > -1 and not end):
                if all_entries:
                    r.append([n1, n2] if n1 < n2 else [n2, n1])
                    n1 = n2 = -1
                else:
                    return [n1, n2] if n1 < n2 else [n2, n1]
        return r

    # ---------------------------------------------------------------------------------------------------------------- #
    def del_line(self, n=-1, string='', all_entries=False):

        if n >= 0 and string:
            return -1

        if not string and (n < 0 or n > len(self.source_code)):
            return -1

        if string:
            n = self.find_line(string=string, all_entries=all_entries)

        if isinstance(n, list):
            for nc in n[::-1]:
                del self.source_code[nc]
        else:
            del self.source_code[n]

        self.renumerate_code()
        return n

    # ---------------------------------------------------------------------------------------------------------------- #
    def insert_line(self, string='', n=-1):

        if n in self.source_code:
            for i in list(self.source_code.keys())[::-1]:
                if i >= n:
                    self.source_code[i] = self.source_code[i - 1]

        self.source_code[n] = string
        self.renumerate_code()

    # ---------------------------------------------------------------------------------------------------------------- #
    def insert_lines(self, strings, n=-1):

        slen = len(strings)
        if n in self.source_code:
            for i in list(self.source_code.keys())[::-1]:
                if i >= n:
                    self.source_code[i + slen] = self.source_code[i - 1]

        for s in range(0, slen):
            self.source_code[n+s] = strings[s]

        self.renumerate_code()
    # -=<^>=- # ------------------------------------------------------------------------------------------------------ #


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    pass
