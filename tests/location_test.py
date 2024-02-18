from compiler.objs.location import Location, L # type: ignore

def test_location_L_equal_to_all() -> None:
    loc_a = L
    loc_b = Location(file='a.txt', row=2, column=1)
    loc_c = Location(file='b.txt', row=22, column=92)
    assert(loc_a==loc_b)
    assert(loc_c==loc_a)

def test_different_locations_not_equal() -> None:
    loc_b = Location(file='a.txt', row=2, column=1)
    loc_c = Location(file='b.txt', row=22, column=92)
    assert(loc_b!=loc_c)

def test_different_files_not_equal() -> None:
    loc_b = Location(file='a.txt', row=2, column=1)
    loc_c = Location(file='b.txt', row=2, column=1)
    assert(loc_b!=loc_c)

def test_different_rows_not_equal() -> None:
    loc_b = Location(file='a.txt', row=2, column=1)
    loc_c = Location(file='a.txt', row=4, column=1)
    assert(loc_b!=loc_c)

def test_different_columns_not_equal() -> None:
    loc_b = Location(file='a.txt', row=2, column=1)
    loc_c = Location(file='a.txt', row=2, column=3)
    assert(loc_b!=loc_c)

def test_same_locations_equal() -> None:
    loc_b = Location(file='a.txt', row=2, column=1)
    loc_c = Location(file='a.txt', row=2, column=1)
    assert(loc_b==loc_c)