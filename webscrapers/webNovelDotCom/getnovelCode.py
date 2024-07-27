base_url = 'https://www.webnovel.com/book/i-stayed-at-home-for-a-century-when-i-emerged-i-was-invincible_22969003505340005'
print(base_url)

reversed_base_url = base_url[::-1]

print(reversed_base_url)

novelCode = ''
for character in base_url:
    if character.isdigit():
        novelCode += character
         


url = f"https://book-pic.webnovel.com/bookcover/{novelCode}"

print(url)