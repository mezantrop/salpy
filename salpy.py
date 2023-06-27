"""Self-altering Python code class"""

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
        self.file = file  # Script filename
        self.source_code = {}  # Script code
        self.ignore_code = {}  # String numbers to be ignored

    # ---------------------------------------------------------------------------------------------------------------- #
    def _make_ignore(self, code=None):
        """Populate self.ignore_code dictionary with strings to exclude from code"""
        in_ignore = False

        # Method names to ignore
        method_names = [name[0] for name in
                        inspect.getmembers(self, lambda mbs: inspect.isroutine(mbs) and not inspect.isbuiltin(mbs))]

        # Method bodies to ignore
        c = globals()['Salpy']()  # Get our class by name
        for method in method_names:
            m = getattr(c, method)  # Get the method by name
            mb = inspect.getsourcelines(m)  # Get sources of the method

            if re.search(pattern='def\s*' + method + '\s*\(', string=mb[0][0]):
                for n in range(mb[1] - 1, mb[1] - 1 + len(mb[0])):
                    self.ignore_code[n] = self.source_code[n]

        # Ignore escaped blocks of strings and method invocations
        code = code or self.source_code
        for n in code.keys():
            if n in self.ignore_code:
                continue

            if not in_ignore and self.ESCAPE_START in code[n]:
                in_ignore = True
                self.ignore_code[n] = code[n]  # Add ESCAPE_START tag to ignore
            elif self.ESCAPE_STOP in code[n]:
                in_ignore = False
                self.ignore_code[n] = code[n]  # Add ESCAPE_STOP tag to ignore
            elif in_ignore:  # Add strings in an escaped block
                self.ignore_code[n] = code[n]
            else:
                for m in method_names:
                    if re.search(pattern=m + '\s*\(', string=code[n]):  # Add method invocations to ignore
                        self.ignore_code[n] = code[n]
                        break

    # ---------------------------------------------------------------------------------------------------------------- #
    def _squeeze_code(self, d, n=-1):
        for i in range(n, len(d)):
            d[i] = d[i + 1]
            del d[i + 1]

    # ---------------------------------------------------------------------------------------------------------------- #
    def read(self, file=None):
        """Read the file with code"""

        with open(file or self.file, 'r') as f:
            self.source_code = {n: l for n, l in enumerate(f.read().splitlines())}

        slp._make_ignore()

        return self.source_code

    # ---------------------------------------------------------------------------------------------------------------- #
    def write(self, file=None, code=None):
        """Write the code into the file"""

        code = code or self.source_code
        lns = list(code.keys())
        lns.sort()
        with open(file or self.file, 'w') as f:
            f.write('\n'.join([code[n] for n in lns]))

    # ---------------------------------------------------------------------------------------------------------------- #
    def find(self, string='', all_entries=False, code=None):
        r = []

        if not string:
            return []

        code = code or self.source_code
        for n in code.keys():
            if n not in self.ignore_code and re.search(pattern=string, string=code[n]):
                if all_entries:
                    r.append(n)
                else:
                    return [n]

        return r

    # ---------------------------------------------------------------------------------------------------------------- #
    def find_block(self, begin='', end='', all_entries=False, code=None):

        r = []

        n1 = n2 = -1

        code = code or self.source_code
        for n in code.keys():
            if n in self.ignore_code:
                continue

            if re.search(begin, code[n]):
                n1 = n
            elif end and re.search(end, code[n]):
                n2 = n

            if (n1 > -1 and n2 > -1) or (n1 > -1 and not end):
                if all_entries:
                    r.append([n1, n2] if n1 < n2 else [n2, n1])
                    n1 = n2 = -1
                else:
                    return [n1, n2] if n1 < n2 else [n2, n1]
        return r

    # ---------------------------------------------------------------------------------------------------------------- #
    def del_line(self, n=-1, string='', all_entries=False, code=None):

        code = code if code else self.source_code

        if n >= 0 and string:
            return -1

        if not string and (n < 0 or n > len(code)):
            return -1

        if string:
            n = self.find(string=string, all_entries=all_entries, code=code)

        if isinstance(n, list):
            for nc in n[::-1]:
                del code[nc]
                # self._squeeze_code(code, nc)
                self._squeeze_code(code, nc)
        else:
            del code[n]
            self._squeeze_code(code, n)

        return n

    # ---------------------------------------------------------------------------------------------------------------- #
    def insert_line(self, n=-1, string='', code=None):

        code = code or self.source_code
        if n in code:
            for i in list(code.keys())[::-1]:
                if i >= n:
                    code[i] = code[i + 1]

        code[n] = string

    # -=<^>=- # ------------------------------------------------------------------------------------------------------ #


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':

    slp = Salpy()

    # findme
    # findme
    # findme

    slp.DEBUG = True
    slp.read()

    #    n = slp.find(string='# findme', all_entries=True)
    #    print(f'N: {n}')
    #    if n:
    #    slp.del_line(string='# findme', all_entries=True)
    print(slp.source_code)
    slp.del_line(string='# findme', all_entries=True)
    print(slp.source_code)

    #    n = slp.find_block(begin='begin', end='end', all_entries=True)
    #    print(f'N: {n}')

    # begin block
    #    print('Lets try finding')
    #    print('these two lines')
    # end block

    slp.write()
    