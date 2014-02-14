


import os
for path in os.listdir('.'):
	if "." in path or "-" in path:
		pass
	else:
		os.chdir(path)
		for file in os.listdir('.'):
			if file.endswith('rdf'):
				os.rename(file, 'flow.rdf')
		for file in os.listdir('.'):
			if file.endswith('map'):
				os.rename(file, 'map.rdf')
		os.chdir('..')


