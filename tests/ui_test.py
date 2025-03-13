import inspect
import json
import luxtelligence_lnoi400_forge as lxt
from luxtelligence_lnoi400_forge import _ui_


def test_ui_technologies():
    assert len(_ui_.json["technologies"]) > 0
    for tech in _ui_.json["technologies"]:
        assert hasattr(lxt, tech["function"])
        assert "LNOI400" in tech["label"]
        pars = inspect.signature(getattr(lxt, tech["function"])).parameters
        assert len(pars) == len(tech["arguments"])
        for arg in tech["arguments"]:
            assert arg["name"] in pars
            if arg["type"] != "medium" and arg["type"] != "subForm":
                assert arg["defaults"] == pars[arg["name"]].default


def test_ui_components():
    assert len(_ui_.json["components"]) == len(lxt.component_names)
    for func in _ui_.json["components"]:
        print(func["function"])
        assert hasattr(lxt.component, func["function"])
        pars = inspect.signature(getattr(lxt.component, func["function"])).parameters
        pars = {k: v for k, v in pars.items() if not k.endswith("_kwargs")}
        assert len(pars) == len(func["arguments"])
        for arg in func["arguments"]:
            assert arg["name"] in pars
            if "defaults" in arg:
                assert arg["defaults"] == pars[arg["name"]].default
            elif "children" in arg:
                assert all(
                    child["defaults"] == val
                    for child, val in zip(arg["children"], pars[arg["name"]].default)
                )
            else:
                assert pars[arg["name"]].default in ("", None)
                assert not arg["required"]


def test_json_conversion():
    _ = json.dumps(_ui_.json)
