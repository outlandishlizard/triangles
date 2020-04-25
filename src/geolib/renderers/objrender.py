import copy

from geolib.renderers.BaseRenderer import BaseRenderer


class Group(object):
    unique_counter = 0

    @classmethod
    def unique_index(cls):
        # Warning! This isn't thread safe!
        cls.unique_counter += 1
        return cls.unique_counter

    def __init__(self, faces, name=None):
        self.vertices = {}
        self.faces = faces
        for face in self.faces:
            self.vertices.update({v.index: v for v in face.vertices})
        self.vertices = [x[1] for x in sorted(self.vertices.items(), key=lambda x: x[0])]

        if name is None:
            self.name = 'shape' + str(self.unique_index())

    def render(self):
        builder = []
        builder.append('g {}'.format(self.name))
        builder.append('\n'.join([v.render() for v in self.vertices]))
        builder.append('\n'.join([f.render() for f in self.faces]))
        return '\n'.join(builder)


class Material(object):
    def __init__(self, Ka, Kd, Ks, Ns, Tr=None):
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns
        self.Tr = Tr
        self.name = '_'.join([str(c) for c in self.Ka])

    @staticmethod
    def from_nodefill(fill):
        c = [float(x) / 255 for x in fill]
        return Material(c, c, c, 200)

    def render(self):
        builder = []
        builder.append('newmtl {}'.format(self.name))
        builder.append('Ka {} {} {}'.format(*self.Ka))
        builder.append('Kd {} {} {}'.format(*self.Kd))
        builder.append('Ks {} {} {}'.format(*self.Ks))
        builder.append('Ns {}'.format(self.Ns))
        if self.Tr is not None:
            builder.append('Tr {}'.format(self.Tr))
        return '\n'.join(builder)


class Face(object):
    def __init__(self, vertices, material):
        self.vertices = vertices
        self.material = material

    def render(self):
        builder = []
        builder.append('usemtl {}'.format(self.material.name))
        builder.append(' '.join(['f'] + [str(v.index) for v in self.vertices]))
        return '\n'.join(builder)


class Vertex(object):
    unique_counter = 0

    @classmethod
    def unique_index(cls):
        # Warning! This isn't thread safe!
        cls.unique_counter += 1
        return cls.unique_counter

    def __init__(self, point, index=None):
        if index is None:
            index = self.unique_index()
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.index = index

    def render(self):
        x, y, z = self.x, self.y, self.z
        return 'v {} {} {}'.format(*[x, y, z])


class ObjCanvas(object):
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.materials = {}
        self.groups = []

    def render(self):
        # Fixup vertex indices to start at 0 rather than whatever the Vertex class counter is at
        lowest_vertex = min(self.vertices, key=lambda x: x.index)
        lowest_index = lowest_vertex.index
        for vertex in self.vertices:
            # this will set the lowest vertex to have index 1
            vertex.index -= (lowest_index - 1)
            # print(vertex.index, lowest_index)
        obj = '\n'.join([g.render() for g in self.groups])
        mtl = '\n'.join([mat.render() for _, mat in self.materials.items()])
        return obj, mtl

    def save(self, filename):
        ObjRenderer.save_image(filename, self)


class ObjRenderer(BaseRenderer):
    def __init__(self):
        super().__init__()

    def extrude_face(self, face, thickness, direction=1):
        new_vertices = []
        for v in face.vertices:
            x, y, z = v.x, v.y, v.z
            z += thickness * direction
            new_vertex = Vertex([x, y, z])
            new_vertices.append(new_vertex)
        new_face = Face(new_vertices, face.material)
        # Now we need to make the sides of the extruded surface
        # Sides are going to be quadrilaterals composed of vertices from both faces.
        # Specifically, we want adjacent pairs of vertices for this to generalize to arbitrary n-gons
        sides = []
        for i in range(len(face.vertices)):
            p1 = face.vertices[i]
            p2 = new_face.vertices[i]
            try:
                p3 = face.vertices[i + 1]
                p4 = new_face.vertices[i + 1]
            except IndexError:
                break
            sides.append(Face([p1, p2, p3, p4], face.material))
        return new_vertices, [new_face] + sides

    def draw_polygon(self, node, canvas, zlevel=None, linecolor=None, fillcolor=None):
        if canvas is None:
            canvas = self.blank_image()

        if zlevel is None:
            try:
                zlevel = node.attrs['zlevel'] * 15
            except KeyError:
                zlevel = 0
        else:
            zlevel = 0

        fill = None
        try:
            fill = node.attrs['fillcolor']
        except KeyError:
            fill = (20, 20, 20)

        material = None
        try:
            material = canvas.materials[fill]
        except KeyError:
            material = Material.from_nodefill(fill)
            canvas.materials[fill] = material

        polygon = node.data
        shape_vertices = []
        for point in polygon:
            v = Vertex([point[0], point[1], zlevel])
            canvas.vertices.append(v)
            shape_vertices.append(v)
        face = Face(shape_vertices, material)

        extruded_vertices, extruded_faces = self.extrude_face(face, 5)

        canvas.vertices.extend(extruded_vertices)
        canvas.faces.append(face)
        canvas.faces.extend(extruded_faces)
        canvas.groups.append(Group([face] + extruded_faces))
        return canvas

    def blank_image(self, l=None, w=None, bg=None):
        return ObjCanvas()

    @staticmethod
    def save_image(filename, canvas):
        obj, mtl = canvas.render()
        with open(filename, 'w') as f:
            f.write('mtllib {}'.format(filename + '.mtl'))
            f.write('\n')
            f.write(obj)
        with open(filename + '.mtl', 'w') as f:
            f.write(mtl)

    def _save_image(self, filename, canvas):
        builder = []
        builder.append('mtllib {}'.format(filename + '.mtl'))
        builder.append('g triangleRender')
        for index, vertex in sorted(canvas.vertices.items()):
            builder.append(vertex)
        for index, face in sorted(canvas.faces.items()):
            builder.append(face)
        print('\n'.join(builder))
        print('vcount:', len(canvas.vertices))
        print('fcount', len(canvas.faces))

        mtlbuilder = [x for x in canvas.materials.values()]

        with open(filename, 'w') as f:
            f.write('\n'.join(builder))
        with open(filename + '.mtl', 'w') as f:
            f.write('\n'.join(mtlbuilder))

        return

    def copy_canvas(self, canvas):
        return copy.deepcopy(canvas)
