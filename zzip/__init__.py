from dataclasses import dataclass, replace
from typing import Any, List, Optional, Tuple

__version__ = "0.0.1"


@dataclass
class Path:
    left: Tuple
    right: Tuple
    parent_nodes: Tuple
    parent_path: Tuple
    changed: bool = False


@dataclass
class Location:
    current: Any
    path: Optional[Path] = None

    def down(self, goto=None):
        if isinstance(self.current, list):
            list_goto = goto or 0
            items = self.current
            path = Path(
                left=items[:list_goto],
                right=items[list_goto + 1 :],
                parent_nodes=(*self.path.parent_nodes, self.current)
                if self.path
                else (self.current,),
                parent_path=self.path,
            )
            return replace(self, current=items[list_goto], path=path)

    def up(self):
        if self.path:
            if self.path.parent_nodes:
                parent_node = self.path.parent_nodes[-1]
                if self.path.changed:
                    return replace(
                        self,
                        current=[*self.path.left, self.current, *self.path.right],
                        path=self.path.parent_path
                        and replace(self.path.parent_path, changed=True),
                    )
                return replace(self, current=parent_node, path=self.path.parent_path)
        # todo: elses

    def right(self):
        # todo: fail when no right
        if self.path and self.path.right:
            current, right = self.path.right[0], self.path.right[1:]
            path = replace(self.path, left=(*self.path.left, self.current), right=right)
            return replace(self, current=current, path=path)

    def left(self):
        if self.path and self.path.left:
            current, left = self.path.left[-1], self.path.left[:-1]
            path = replace(self.path, left=left, right=(self.current, *self.path.right))
            return replace(self, current=current, path=path)

    def top(self):
        loc = self
        while loc.path:
            loc = loc.up()
        return loc

    def replace(self, value):
        if self.path:
            return replace(self, current=value, path=replace(self.path, changed=True))
        return replace(self, current=value)


def zipper(value):
    return Location(current=value)
