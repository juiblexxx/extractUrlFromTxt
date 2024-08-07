import re

# p^[π«Εθ`B
P_char={
    "Όp¬Ά":re.compile(r'[a-z]+'),
    "ΌpεΆ":re.compile(r'[A-Z]+'),
    "Όpp"  :re.compile(r'[a-z|A-Z]+'),
    "Όp"  :re.compile(r'[0-9]+')
}

str_data = "ABCDEabcde ’€¦¨01234"

print(P_char["Όp¬Ά"].search(str_data))
print(P_char["ΌpεΆ"].search(str_data))
print(P_char["Όpp"].search(str_data))
print(P_char["Όp"].search(str_data))
