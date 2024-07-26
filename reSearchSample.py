import re

# �p�^�[���������Œ�`�B
P_char={
    "���p������":re.compile(r'[a-z]+'),
    "���p�啶��":re.compile(r'[A-Z]+'),
    "���p�p��"  :re.compile(r'[a-z|A-Z]+'),
    "���p����"  :re.compile(r'[0-9]+')
}

str_data = "ABCDEabcde����������01234"

print(P_char["���p������"].search(str_data))
print(P_char["���p�啶��"].search(str_data))
print(P_char["���p�p��"].search(str_data))
print(P_char["���p����"].search(str_data))
