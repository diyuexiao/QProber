import sys
def print_path(result):
	for i in range(1, len(result)):
		subtree= result[i]
		if len(subtree) > 1:
			sys.stdout.write(result[0] + '/')
			print_path(subtree)
		else:
			sys.stdout.write(result[0] + '/' + subtree[0] + '\n')

r1 = ['Root', ['Computers', ['Programming']], ['Health', ['Diseases'], ['Fitness']], ['Sports', ['Basketball'], ['Soccer']]]
#print_path(r1[2])

def get_path_list(result):
	if len(result) == 1:
		return result
	paths = []
	for i in range(1, len(result)):
		child_paths = get_path_list(result[i])
		for path in child_paths:
			paths.append(result[0] + '/' + path)
	return paths

l = get_path_list(r1)
print l