import collections

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        """
        Creates a doubly linked list with an end node and a mapping of keys to
        lists of key-previous-next nodes. It also accepts an optional iterable
        argument for addition to the list.

        Args:
            iterable (Python sequence.): iterable data structure that is being
                converted into a doubly linked list, and it is assigned to the
                object's internal map and end nodes.
                
                		- `end = []`: A list of sentinel nodes representing the endpoints
                of the linked list. The first node is set to `None`, while the
                last two nodes (`self` and `end`) are set to each other to form a
                cycle, ensuring that the linked list is doubly linked.
                		- `map = {}`: A dictionary where keys represent elements in the
                iterable and values represent the prev, next nodes of those elements
                in the linked list. This allows for efficient navigation through
                the linked list by following the pointers from one element to its
                previous and next neighbors.

        """
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        """
        Updates a dictionary's value for a given key by replacing it with a new value.

        Args:
            key (str): 3-element tuple that contains the value to be inserted into
                the list at the position indicated by the `end` parameter.

        """
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        """
        Pops a key-value pair from a dictionary `self.map`. It updates the next
        and previous elements in the list by swapping their values.

        Args:
            key (`object`.): 0-based index of the key to be popped from the map.
                
                		- `key`: The key that is removed from the map.
                		- `prev`: The previous value associated with the key, which is
                updated to refer to the next element in the linked list.
                		- `next`: The next element in the linked list, which is updated
                to refer to the previous element's new value.

        """
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        """
        Generates a generator that repeatedly yields the first element of each
        list until it reaches the specified `end` value, starting from the last
        item of the first list.

        """
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        """
        Iterates over a sequence in reverse order, yielding each element in reverse.

        """
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        """
        Removes an item from a set and returns it. If the set is empty, it raises
        a `KeyError`.

        Args:
            last (int): 2nd to last element in the sequence passed to `self.end`,
                indicating which position to find the next key to discard from the
                set.

        Returns:
            instance of `KeyError: a single key item from the set, discarded and
            removed from the set.
            
            		- If `last` is `True`, the output will be a `KeyError`.
            		- If `last` is `False`, the output will be a key that is discarded
            from the set.

        """
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        """
        Generates a string representation of an object by returning a string
        containing the class name and the object's attributes in a list.

        Returns:
            str: the name of the class followed by the arguments passed to it.

        """
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        """
        Compares two objects, either a Python `set` or an ordered list (i.e., an
        iterable), and returns `True` if they have the same elements in the same
        order, or `False` otherwise.

        Args:
            other (`OrderedSet`.): 2nd sequence or set that will be compared to
                the current sequence or set by the function.
                
                		- If `other` is an instance of `OrderedSet`, then it means that
                it is an unordered set of objects that preserve their ordering.
                In this case, the comparison checks if the length of both sets
                (i.e., the number of elements) is the same, and if the elements
                are equal in terms of identity.
                		- Otherwise, `other` could be any other type of collection (e.g.,
                a list, set, or frozenset). In this case, the comparison checks
                if the elements are equal in terms of identity regardless of their
                order.

        Returns:
            float: a boolean value indicating whether two objects are equal.

        """
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

            
if __name__ == '__main__':
    s = OrderedSet('abracadaba')
    t = OrderedSet('simsalabim')
    print(s | t)
    print(s & t)
    print(s - t)
