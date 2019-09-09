#file = "cube.obj"#input("filename: ")

def open_obj_file(filename, index=1):
    """
    Only supports the loading of vertices, edges, and faces (not texture coords, normals, etc.)
    """
    vertices = []
    edges = []
    faces = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                #print(line,end='')
                if line[0:2] == 'v ':
                    coords = [float(n) for n in line[2:-1].split(' ')]
                    coords[1]=-coords[1]
                    coords[2]=-coords[2]
                    vertices.append(coords)
                elif line[0:2] == 'l ':
                    indices = [int(n)+index-1 for n in line[2:-1].split(' ')]
                    edges.append(indices)
                elif line[0:2] == 'f ':
                    indices = [int(n.split('/')[0])+index-1 for n in line[2:-1].split(' ')]
                    faces.append(indices)
    except FileNotFoundError:
        print("File %s was not found." %filename)
        return -1

    return vertices, edges, faces

#a,b,c = open_obj_file(file, index=0)

#print(a)
#print(b)
#print(c)
