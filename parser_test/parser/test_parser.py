from pathlib import Path
from sihm.parser import SihmParser

input_file = Path("test.yaml")
p = SihmParser(input_file, "index.js")
p.write_file()
