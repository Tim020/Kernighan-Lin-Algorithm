import decimal


class Partition(object):
    def __init__(self):
        self.nodes = set()

    def add_node(self, node):
        if type(node) is Node:
            self.nodes.add(node)
            node.partition = self
        else:
            raise TypeError("Type of node was {} but should be Node".
                            format(type(node)))

    def remove_node(self, node):
        if type(node) is Node:
            self.nodes.remove(node)
        else:
            raise TypeError("Type of node was {} but should be Node".
                            format(type(node)))

    def contains_node(self, node):
        if type(node) is Node:
            return node in self.nodes
        else:
            raise TypeError("Type of node was {} but should be Node".
                            format(type(node)))

    def __str__(self):
        return "Contained Nodes: [{}]".format(", ".join(node.name for
                                                        node in self.nodes))


class Node(object):
    def __init__(self, partition, name):
        if type(partition) is Partition:
            self.partition = partition
        else:
            raise TypeError("Type of partition was {} but should be Partition".
                            format(type(partition)))
        self.connections = set()
        self.name = name
        self.partition.add_node(self)

    def add_connection(self, node, cost):
        if type(node) is Node:
            if type(cost) is int:
                self.connections.add((node, cost))
            else:
                raise TypeError("Type of cost was {} but should be int".
                                format(type(cost)))
        else:
            raise TypeError("Type of node was {} but should be Node".
                            format(type(node)))

    def internal_cost(self):
        weight = 0
        for connection in self.connections:
            if self.partition.contains_node(connection[0]):
                weight += connection[1]
        return weight

    def external_cost(self):
        weight = 0
        for connection in self.connections:
            if not self.partition.contains_node(connection[0]):
                weight += connection[1]
        return weight

    def connects_to(self, node):
        if type(node) is Node:
            for connection in self.connections:
                if connection[0] == node:
                    return True
            return False
        else:
            raise TypeError("Type of node was {} but should be Node".
                            format(type(node)))

    def get_connection_weight(self, node):
        if type(node) is Node:
            for connection in self.connections:
                if connection[0] == node:
                    return connection[1]
            raise RuntimeError("Node {} has no connection to Node {}".
                               format(self.name, node.name))
        else:
            raise TypeError("Type of node was {} but should be Node".
                            format(type(node)))

    def __str__(self):
        return "Name: {}\nConnected To: [{}]".format(self.name, ", ".join(
            connection[0].name for connection in self.connections))


class KernighanLin(object):
    def __init__(self, pa, pb):
        if type(pa) is Partition:
            self.pa = pa
        else:
            raise TypeError("Type of pa was {} but should be Partition".
                            format(type(pa)))
        if type(pb) is Partition:
            self.pb = pb
        else:
            raise TypeError("Type of pb was {} but should be Partition".
                            format(type(pb)))

    def get_max_dt(self, nodes_a, nodes_b):
        swap_a = None
        swap_b = None
        max_cost = decimal.Decimal('-Infinity')
        for node_a in nodes_a:
            for node_b in nodes_b:
                cost = self.calculate_dt(node_a, node_b)
                if cost > max_cost:
                    max_cost = cost
                    swap_a = node_a
                    swap_b = node_b
        return swap_a, swap_b, max_cost

    def calculate_dt(self, node_a, node_b):
        if node_a.partition == node_b.partition:
            raise RuntimeError("Cannot calculate DT for nodes in the same "
                               "partition")
        da = node_a.external_cost() - node_a.internal_cost()
        db = node_b.external_cost() - node_b.internal_cost()
        dc = 0
        if node_a.connects_to(node_b):
            dc += node_a.get_connection_weight(node_b)
        if node_b.connects_to(node_a):
            dc += node_b.get_connection_weight(node_a)
        return (da + db) - (2 * dc)

    def swap_nodes(self, node_a, node_b):
        if node_a.partition == node_b.partition:
            raise RuntimeError("Cannot swap nodes in the same partition")
        pa = node_a.partition
        pb = node_b.partition

        pa.remove_node(node_a)
        pb.remove_node(node_b)
        pa.add_node(node_b)
        pb.add_node(node_a)

    def do_work(self):
        max_dt = 0
        # Repeat until max DT is negative
        while max_dt >= 0:
            print("A: {}".format(self.pa))
            print("B: {}".format(self.pb))

            nodes_left_a = set(self.pa.nodes)
            nodes_left_b = set(self.pb.nodes)
            hist = []
            # Repeat until all nodes have been swapped
            while len(nodes_left_a.union(nodes_left_b)) > 0:
                swap_a, swap_b, max_cost = self.get_max_dt(nodes_left_a,
                                                           nodes_left_b)
                nodes_left_a.remove(swap_a)
                nodes_left_b.remove(swap_b)
                self.swap_nodes(swap_a, swap_b)
                hist.append((swap_a, swap_b, max_cost))

            # Get the maximum DT sum
            hist_totals = []
            for count, move in enumerate(hist):
                if count == 0:
                    hist_totals.append(move[2])
                else:
                    hist_totals.append(hist_totals[count - 1] + move[2])
            max_dt = max(hist_totals)
            undo_start_index = hist_totals.index(max_dt) + 1

            print("Hist Totals: {}".format(hist_totals))
            print("Max DT: {}".format(max_dt))

            if max_dt < 0:
                break

            for move in hist[undo_start_index:]:
                self.swap_nodes(move[0], move[1])

        print("Done: {}, {}".format(self.pa, self.pb))


A = Partition()
B = Partition()

a = Node(A, "a")
b = Node(A, "b")
c = Node(B, "c")
d = Node(B, "d")
e = Node(B, "e")
f = Node(B, "f")
g = Node(A, "g")
h = Node(B, "h")
i = Node(B, "i")
j = Node(A, "j")
k = Node(A, "k")
l = Node(A, "l")

a.add_connection(c, 64)
a.add_connection(f, 8)
b.add_connection(c, 64)
c.add_connection(d, 128)
d.add_connection(b, 16)
d.add_connection(e, 48)
d.add_connection(h, 48)
e.add_connection(g, 16)
f.add_connection(a, 16)
f.add_connection(g, 16)
g.add_connection(l, 8)
h.add_connection(i, 48)
i.add_connection(k, 12)
j.add_connection(k, 48)
k.add_connection(l, 24)

test = KernighanLin(A, B)
test.do_work()
