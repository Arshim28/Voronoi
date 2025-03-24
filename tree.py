from beachline import Arc, Breakpoint

class Node:
    def __init__(self, data):
        self.data = data
        self._left = None
        self._right = None
        self._height = None
        self.parent = None

    def __repr__(self):
        return f"Node({self.data}, left={self.left}, right={self.right})"

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def grandparent(self):
        if self.parent is None or self.parent.parent is None:
            return None
        return self.parent.parent

    def get_key(self, **kwargs):
        return self.data

    def get_value(self, **kwargs):
        return self.data

    def get_label(self, **kwargs):
        return f"{self.get_key(**kwargs)}({self.height})"

    @left.setter
    def left(self, node):
        if node is not None:
            node.parent = self
        self._left = node

    @right.setter
    def right(self, node):
        if node is not None:
            node.parent = self
        self._right = node

    @property
    def height(self):
        if self._height is None:
            self._height = self.calculate_height()
        return self._height

    @property
    def balance(self):
        left_height = self.left.height if self.left is not None else 0
        right_height = self.right.height if self.right is not None else 0
        return left_height - right_height

    def calculate_height(self):
        left_height = self.left.height if self.left is not None else 0
        right_height = self.right.height if self.right is not None else 0
        height = 1 + max(left_height, right_height)
        return height

    def update_height(self):
        self._height = self.calculate_height()

    def update_heights(self):
        self.update_height()
        if self.parent is not None:
            self.parent.update_heights()

    def is_left_child(self):
        if self.parent is None:
            return False
        return self.parent.left == self

    def is_right_child(self):
        if self.parent is None:
            return False
        return self.parent.right == self

    def is_leaf(self):
        return self.left is None and self.right is None

    def minimum(self):
        current = self
        while current.left is not None:
            current = current.left
        return current

    def maximum(self):
        current = self
        while current.right is not None:
            current = current.right
        return current

    @property
    def successor(self):
        if self.right is not None:
            return self.right.minimum()
        current = self
        while current.is_right_child():
            current = current.parent
        if current.parent is None or current.parent.right is None:
            return None
        return current.parent.right.minimum()

    @property
    def predecessor(self):
        if self.left is not None:
            return self.left.maximum()
        current = self
        while current.is_left_child():
            current = current.parent
        if current.parent is None or current.parent.left is None:
            return None
        return current.parent.left.maximum()

    def replace_leaf(self, replacement, root):
        if replacement is not None:
            replacement.parent = self.parent
        if self.is_left_child():
            self.parent.left = replacement
        elif self.is_right_child():
            self.parent.right = replacement
        else:
            root = replacement
        if replacement is not None:
            replacement.update_heights()
        elif self.parent is not None:
            self.parent.update_heights()
        return root

class LeafNode(Node):
    def __init__(self, data: Arc):
        super().__init__(data)

    def __repr__(self):
        return f"Leaf({self.data}, left={self.left}, right={self.right})"

    def get_key(self, sweep_line=None):
        return self.data.origin.x

    def get_value(self, **kwargs):
        return self.data

    def get_label(self):
        return f"{self.data.origin.name}"

class InternalNode(Node):
    def __init__(self, data: Breakpoint):
        super().__init__(data)

    def __repr__(self):
        return f"Internal({self.data}, left={self.left}, right={self.right})"

    def get_key(self, sweep_line=None):
        return self.data.get_intersection(sweep_line).x

    def get_value(self, **kwargs):
        return self.data

    def get_label(self):
        return f"{self.data.breakpoint[0].name},{self.data.breakpoint[1].name}"

class Tree:
    @staticmethod
    def find_leaf_node(root: Node, key, **kwargs):
        node = root
        while node is not None:
            if node.is_leaf():
                return node
            elif key == node.get_key(**kwargs) and not node.is_leaf():
                if node.left is not None:
                    return node.left.maximum()
                return node.right.minimum()
            elif key < node.get_key(**kwargs):
                node = node.left
            else:
                node = node.right
        return node

    @staticmethod
    def find_value(root: Node, query: Node, compare=lambda x, y: x == y, **kwargs):
        key = query.get_key(**kwargs)
        node = root
        while node is not None:
            if key == node.get_key(**kwargs):
                if compare(node.data, query.data):
                    return node
                left = Tree.find_value(node.left, query, compare, **kwargs)
                if left is None:
                    right = Tree.find_value(node.right, query, compare, **kwargs)
                    return right
                return left
            elif key < node.get_key(**kwargs):
                return Tree.find_value(node.left, query, compare, **kwargs) or \
                       Tree.find_value(node.right, query, compare, **kwargs)
            else:
                return Tree.find_value(node.right, query, compare, **kwargs) or \
                       Tree.find_value(node.left, query, compare, **kwargs)

    @staticmethod
    def balance_and_propagate(node):
        node = Tree.balance(node)
        if node.parent is None:
            return node
        return Tree.balance_and_propagate(node.parent)

    @staticmethod
    def balance(node):
        if node.balance > 1 and node.left.balance >= 0:
            return Tree.rotate_right(node)
        if node.balance < -1 and node.right.balance <= 0:
            return Tree.rotate_left(node)
        if node.balance > 1 and node.left.balance < 0:
            node.left = Tree.rotate_left(node.left)
            return Tree.rotate_right(node)
        if node.balance < -1 and node.right.balance > 0:
            node.right = Tree.rotate_right(node.right)
            return Tree.rotate_left(node)
        return node

    @staticmethod
    def rotate_left(z):
        grandparent = z.parent
        y = z.right
        T2 = y.left
        y.parent = grandparent
        if grandparent is not None:
            if z.is_left_child():
                grandparent.left = y
            else:
                grandparent.right = y
        y.left = z
        z.right = T2
        z.update_height()
        y.update_height()
        return y

    @staticmethod
    def rotate_right(z):
        grandparent = z.parent
        y = z.left
        T3 = y.right
        y.parent = grandparent
        if grandparent is not None:
            if z.is_left_child():
                grandparent.left = y
            else:
                grandparent.right = y
        y.right = z
        z.left = T3
        z.update_height()
        y.update_height()
        return y