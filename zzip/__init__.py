from dataclasses import dataclass, replace
from typing import Any, List, Optional, Tuple

__version__ = "0.0.1"


@dataclass
class Path:
    left: Tuple
    right: Tuple
    parent_nodes: Tuple
    parent_path: Tuple
    selector: Tuple
    changed: bool
    index: int

    def mark_changed(self):
        return replace(self, changed=True)


@dataclass
class ListPath(Path):
    def new_current(self, current):
        return [*self.left, current, *self.right]


@dataclass
class DictPath(Path):
    keys: List[str]

    @property
    def key(self):
        return self.keys[self.index]

    def parent_node(self):
        return self.parent_nodes[-1]

    def go_right(self, current):
        new_current = self.parent_node()[self.right[0]]
        right = self.right[1:]
        left = (*self.left, self.key)
        path = replace(self, index=len(left), left=left, right=right)
        return new_current, path

    def go_left(self, current):
        new_current = self.parent_node()[self.left[-1]]
        left = self.left[:-1]
        right = (self.key, *self.right)
        path = replace(self, index=len(left), left=left, right=right)
        return new_current, path

    def new_current(self, current):
        new_current = dict(**self.parent_node())
        new_current[self.key] = current
        return new_current


@dataclass
class Location:
    current: Any
    path: Optional[Path] = None

    def down(self, goto=None):
        if isinstance(self.current, list):
            list_goto = goto or 0
            items = self.current
            left = items[:list_goto]
            index = len(left)
            selector = (*self.path.selector, index) if self.path else (index,)
            path = ListPath(
                index=index,
                selector=selector,
                left=left,
                right=items[list_goto + 1 :],
                parent_nodes=(*self.path.parent_nodes, self.current)
                if self.path
                else (self.current,),
                parent_path=self.path,
                changed=False,
            )
            return replace(self, current=items[list_goto], path=path)
        if isinstance(self.current, dict):
            keys = list(self.current.keys())
            if not keys:
                # todo: raise instead
                return
            current_key = goto or keys[0]
            index = keys.index(current_key)
            selector = (
                (*self.path.selector, current_key) if self.path else (current_key,)
            )
            path = DictPath(
                keys=keys,
                index=index,
                selector=selector,
                left=keys[:index],
                right=keys[index + 1 :],
                parent_nodes=(*self.path.parent_nodes, self.current)
                if self.path
                else (self.current,),
                parent_path=self.path,
                changed=False,
            )
            return replace(self, current=self.current[current_key], path=path)

    def up(self):
        if self.path:
            if self.path.parent_nodes:
                parent_node = self.path.parent_nodes[-1]
                if self.path.changed:
                    return replace(
                        self,
                        current=self.path.new_current(self.current),
                        path=self.path.parent_path
                        and self.path.parent_path.mark_changed(),
                    )
                return replace(self, current=parent_node, path=self.path.parent_path)
        # todo: elses

    def right(self):
        # todo: fail when no right
        if self.path and self.path.right:
            # todo: make work with ListPath, too
            if isinstance(self.path, DictPath):
                current, path = self.path.go_right(self.current)
                return replace(self, current=current, path=path)
            current, right = self.path.right[0], self.path.right[1:]
            left = (*self.path.left, self.current)
            path = replace(self.path, index=len(left), left=left, right=right)
            return replace(self, current=current, path=path)

    def left(self):
        if self.path and self.path.left:
            # todo: make work with ListPath, too
            if isinstance(self.path, DictPath):
                current, path = self.path.go_left(self.current)
                return replace(self, current=current, path=path)
            current, left = self.path.left[-1], self.path.left[:-1]
            path = replace(self.path, left=left, right=(self.current, *self.path.right))
            return replace(self, current=current, path=path)

    def top(self):
        loc = self
        while loc.path:
            loc = loc.up()
        return loc

    def replace(self, value, persist=False):
        if self.path:
            return replace(self, current=value, path=replace(self.path, changed=True))
        return replace(self, current=value)

    def select(self, selector):
        loc = self
        for s in selector:
            loc = loc.down(s)
        return loc


def zipper(value):
    return Location(current=value)
