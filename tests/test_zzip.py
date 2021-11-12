from zzip import zipper


def test_list_down():
    z = zipper([1, 2, 3])
    assert z.down().current == 1


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
    z = zipper([1, [2, 3], 4])
    assert z.down().right().down().replace(200).top().current == [1, [200, 3], 4]
