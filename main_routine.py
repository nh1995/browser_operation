import helium,yml_tsv_converter

yml_tsv_converter.convert_to_tsv("""
- I: yahoo
- A: click
  O: "検索"
- A: click
""")


