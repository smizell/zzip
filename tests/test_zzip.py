import pytest
from zzip import zipper, NavigationException


def test_list_down():
    z = zipper([1, 2, 3])
    zd = z.down()
    assert zd.current == 1
    assert zd.path.index == 0


def test_list_down_index():
    z = zipper([1, 2, 3])
    assert z.down(1).current == 2


def test_list_up():
    z = zipper([1, 2, 3])
    assert z.down().up().current == [1, 2, 3]


def test_list_right():
    z = zipper([1, 2, 3])
    assert z.down().right().current == 2


def test_list_left():
    z = zipper([1, 2, 3])
    assert z.down().right().left().current == 1


def test_list_top():
    z = zipper([1, 2, 3])
    assert z.down().right().top().current == [1, 2, 3]


def test_list_replace():
    z = zipper([1, 2, 3])
    assert z.down().right().replace(100).top().current == [1, 100, 3]


def test_advanced():
    z = zipper([1, [2, [3, 4]]])
    assert z.down().right().down().right().down().replace(300).top().current == [
        1,
        [2, [300, 4]],
    ]


def test_dict_down():
    z = zipper({"a": 1})
    zd = z.down()
    assert zd.current == 1
    assert zd.path.key == "a"


def test_dict_down_down():
    z = zipper({"a": {"b": 2}})
    zd = z.down().down()
    assert zd.current == 2
    assert zd.path.key == "b"


def test_dict_down_key():
    z = zipper({"a": 1, "b": 2, "c": 3})
    zd = z.down("c")
    assert zd.current == 3
    assert zd.path.key == "c"


def test_dict_right():
    z = zipper({"a": 1, "b": 2})
    zv = z.down().right()
    assert zv.current == 2
    assert zv.path.key == "b"


def test_dict_left():
    z = zipper({"a": 1, "b": 2})
    zv = z.down().right().left()
    assert zv.current == 1
    assert zv.path.key == "a"


def test_dict_up():
    z = zipper({"a": 1})
    zv = z.down().up()
    assert zv.current == {"a": 1}


def test_dict_replace():
    z = zipper({"a": 1})
    assert z.down().replace(100).top().current == {"a": 100}


def test_nested():
    z = zipper({"a": {"b": 1, "c": [4, 5, 6]}})
    assert z.down().down().right().down().replace(400).top().current == {
        "a": {"b": 1, "c": [400, 5, 6]}
    }
    assert z.down().down().replace(100).top().current == {
        "a": {"b": 100, "c": [4, 5, 6]}
    }
    # Make sure the original isn't altered
    assert z.current == {"a": {"b": 1, "c": [4, 5, 6]}}


def test_multiple_replace():
    # We have to persist the value by going back to the top then selecting the node again
    z = zipper({"a": {"b": 1, "c": [4, 5, 6]}})
    assert z.down().down().replace(100, persist=True).right().down().replace(
        400
    ).top().current == {"a": {"b": 100, "c": [400, 5, 6]}}


def test_selector():
    z = zipper({"a": {"b": 1, "c": [4, 5, 6]}})
    zv = z.select(["a", "c", 1])
    assert zv.current == 5
    assert zv.path.selector == ("a", "c", 1)


def test_update():
    z = zipper({"a": {"b": 1, "c": [4, 5, 6]}})
    zv = z.select(["a", "c", 1]).update(lambda loc: loc.current * 10)
    assert zv.top().current == {"a": {"b": 1, "c": [4, 50, 6]}}


def test_direction_exceptions():
    z = zipper([1, 2])
    with pytest.raises(NavigationException):
        z.down().down()
    with pytest.raises(NavigationException):
        z.up()
    with pytest.raises(NavigationException):
        z.left()
    with pytest.raises(NavigationException):
        z.right()
