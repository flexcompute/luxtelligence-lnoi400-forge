import luxtelligence_lnoi400_forge as lxt


def test_components():
    technology = lxt.lnoi400()
    for name in dir(lxt.component):
        if name[0] == "_":
            continue
        func = getattr(lxt.component, name)
        _ = func(technology=technology)
