import re

# ƒpƒ^[ƒ“‚ğ«‘‚Å’è‹`B
P_char={
    "”¼Šp¬•¶š":re.compile(r'[a-z]+'),
    "”¼Šp‘å•¶š":re.compile(r'[A-Z]+'),
    "”¼Šp‰pš"  :re.compile(r'[a-z|A-Z]+'),
    "”¼Šp”š"  :re.compile(r'[0-9]+')
}

str_data = "ABCDEabcde‚ ‚¢‚¤‚¦‚¨01234"

print(P_char["”¼Šp¬•¶š"].search(str_data))
print(P_char["”¼Šp‘å•¶š"].search(str_data))
print(P_char["”¼Šp‰pš"].search(str_data))
print(P_char["”¼Šp”š"].search(str_data))
