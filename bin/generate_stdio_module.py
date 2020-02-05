from underbar.stdio import StandardStream

for handle in StandardStream:
	print(f'{handle.name.lower()} = {handle.value}')
