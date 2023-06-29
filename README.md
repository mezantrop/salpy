# A Python class to help creating self-altering code

<a href="https://www.buymeacoffee.com/mezantrop" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## Usage

```Python
import salpy

# Changeme

new_code = """
print("Hello world!")
exit(0)
"""

slp = salpy.Salpy()
slp.read()

#
# slp.find_line(...)
# slp.find_block(...)
# slp.del_line(...)
# slp.insert_line(...)
# slp.replace_line(...)
# slp.insert_lines(...)
#

entry_point = slp.replace_line(old_string='Changeme', new_string=new_code)
slp.write()
```

Early stage of development, don't expect everything to work properly. If you have an idea, a question, or have found
a problem, do not hesitate to open an issue or mail me: Mikhail Zakharov zmey20000@yahoo.com