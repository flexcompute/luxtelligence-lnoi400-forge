import photonforge as pf
import luxtelligence_lnoi400_forge as lxt


def test_components():
    technology = lxt.lnoi400()
    for name in dir(lxt.component):
        if name[0] == "_":
            continue
        func = getattr(lxt.component, name)
        _ = func(technology=technology)


def test_defaults(request):
    pf.config.default_technology = lxt.lnoi400()
    for component in [
        getattr(lxt.component, n)() for n in dir(lxt.component) if not n.startswith("_")
    ]:
        name = component.name
        if name == "UBEND_RACETRACK":
            name = "UBEND"
        elif name == "UBEND":
            name = ""

        path = request.path.parent / "gdsii" / f"{name}.gds"
        if not path.is_file():
            continue

        gdsii = pf.find_top_level(*pf.load_layout(path).values())
        assert len(gdsii) == 1
        gdsii = gdsii[0]

        diff = pf.Component(component.name + ".diff")
        total = 0
        error = 0
        for layer in component.layers(include_dependencies=True) + gdsii.layers(
            include_dependencies=True
        ):
            gdsii_structs = gdsii.get_structures(layer)
            diff_structs = pf.offset(
                pf.boolean(component.get_structures(layer), gdsii_structs, "^"),
                -pf.config.tolerance,
            )
            if len(gdsii_structs) > 0:
                total += sum(x.area() for x in gdsii_structs)
            if len(diff_structs) > 0:
                diff.add(layer, *diff_structs)
                error += sum(x.area() for x in diff_structs)

        valid = error / total < {
            "DIR_COUPL": 0.059,
            "MZM": 4e-5,
            "SBEND": 0.011,
            "SBEND_VAR_WIDTH": 0.083,
            "UBEND_RACETRACK": 6e-5,
        }.get(component.name, 1e-5)
        if not valid:
            diff.write_gds()
            assert False, f"{component.name} error: {error / total:g}"
