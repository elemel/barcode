from underbar.register import Register

for register in Register:
	print(f'{register.name.lower()} = {register.value}')
