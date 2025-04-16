import inspect
import pathlib
import subprocess

import tidy3d as td
from tidy3d.material_library.material_library import MaterialItem

import photonforge as pf
import luxtelligence_lnoi400_forge as lxt


replacements = {
    "Sio2": "SiO₂",
    "Sin": "Si₃N₄",
    "Mmi1X2": "MMI 1×2",
    "Mmi2X2": "MMI 2×2",
    "Cpw": "CPW",
    "Eo": "EO",
    "Mz": "MZ",
}


def make_label(name):
    words = name.replace("_", " ").title().split()
    return " ".join(replacements.get(w, w) for w in words)


mat_lib = {}
for name, mi in td.material_library.items():
    if not isinstance(mi, MaterialItem):
        continue
    for spec, var in mi.variants.items():
        if not isinstance(var.medium, td.components.medium.MediumType):
            continue
        mat_lib[var.medium] = {
            "type": "material_library",
            "value": {"path": [name, spec]},
        }


pf.config.svg_labels = False
pf.config.svg_port_names = False
pf.config.default_technology = lxt.lnoi400()


def make_component_arg(name, value, tooltip):
    arg = {
        "defaults": value,
        "label": make_label(name),
        "name": name,
        "tooltip": tooltip,
    }
    if "port_spec" in name:
        arg["category"] = "portSpec"
        arg["type"] = "select"
    elif name == "technology":
        arg = {
            "name": "technology",
            "placeholder": "Use the global default technology.",
            "required": False,
            "tooltip": "Component technology.",
            "type": "technology",
        }
    elif name == "name":
        arg = {"name": "name", "required": False, "tooltip": "Component name.", "type": "input"}
    elif name == "splitter" and value is None:
        arg["type"] = "component"
        arg["required"] = False
        arg["placeholder"] = "Use default 1×2 MMI."
    elif name in ("x_size", "y_size") and value in (10100, 5050):
        arg["options"] = [5000, 5050, 10000, 10100, 20000, 20200]
        arg["suffix"] = "μm"
        arg["type"] = "select"
    elif isinstance(value, bool):
        arg["type"] = "checkbox"
    elif isinstance(value, (float, int)):
        arg["type"] = "number"
        if "angle" in name:
            arg["suffix"] = "°"
            arg["validates"] = ["min", "max"]
            arg["validatesArgs"] = {"min": [-90], "max": [90]}
        elif any(w in name for w in ("ratio", "fraction")):
            assert 0 <= value <= 1
            arg["validatesArgs"] = {"min": [0], "max": [1]}
        else:
            assert 0 <= value
            arg["suffix"] = "μm"
            arg["validates"] = ["min"]
            arg["validatesArgs"] = {"min": [0]}
    elif (
        isinstance(value, tuple)
        and len(value) == 2
        and all(isinstance(x, (float, int)) for x in value)
    ):
        arg = {
            "children": [
                {
                    "defaults": value[0],
                    "hideLabel": True,
                    "name": "x",
                    "prefix": "x",
                    "suffix": "μm",
                    "type": "number",
                },
                {
                    "defaults": value[1],
                    "hideLabel": True,
                    "name": "y",
                    "prefix": "y",
                    "suffix": "μm",
                    "type": "number",
                },
            ],
            "itemSpan": 12,
            "label": make_label(name),
            "name": name,
            "tooltip": tooltip,
            "category": "tuple",
            "type": "subForm",
        }
        if "size" in name:
            arg["children"][0]["validates"] = ["min"]
            arg["children"][0]["validatesArgs"] = {"min": [0]}
            arg["children"][1]["validates"] = ["min"]
            arg["children"][1]["validatesArgs"] = {"min": [0]}
    else:
        raise RuntimeError(f"Unkown type: {name} = {value}")
    return arg


component_names = sorted(n for n in dir(lxt.component) if n[0] != "_")

components = []
for comp_name in component_names:
    component_func = getattr(lxt.component, comp_name)
    parameters = inspect.signature(component_func).parameters
    c = component_func()
    svg = c._repr_svg_()

    args = []
    go_args = False
    name = None
    tooltip = None

    for line in component_func.__doc__.splitlines():
        if go_args:
            if len(line.strip()) == 0:
                if not name.endswith("_kwargs"):
                    args.append(make_component_arg(name, parameters[name].default, tooltip))
                break
            if line.startswith("      "):
                tooltip += " " + line.strip()
            else:
                if name and not name.endswith("_kwargs"):
                    args.append(make_component_arg(name, parameters[name].default, tooltip))
                name = line[4 : 4 + line[4:].find(":")]
                tooltip = line[line.find(":") + 2 :]
        else:
            go_args = line.strip() == "Args:"
    components.append(
        {
            "arguments": args,
            "function": "component." + component_func.__name__,
            "label": make_label(comp_name),
            "svg": svg,
        }
    )


def complex_json(obj):
    if isinstance(obj, tuple):
        return tuple(complex_json(x) for x in obj)
    if isinstance(obj, list):
        return [complex_json(x) for x in obj]
    if isinstance(obj, dict):
        return {k: complex_json(v) for k, v in sorted(obj.items())}
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    return obj


def make_tech_arg(name, value, tooltip):
    arg = {
        "defaults": value,
        "label": make_label(name),
        "name": name,
        "tooltip": tooltip,
    }
    if isinstance(value, bool):
        arg["type"] = "checkbox"
    elif isinstance(value, (float, int)):
        arg["type"] = "number"
        if "angle" in name:
            arg["suffix"] = "°"
            arg["validates"] = ["min", "max"]
            arg["validatesArgs"] = {"min": [-90], "max": [90]}
        else:
            arg["suffix"] = "μm"
            if any(w in name for w in ("thickness", "depth", "separation", "gap")):
                arg["validates"] = ["min"]
                arg["validatesArgs"] = {"min": [0]}
    elif isinstance(value, lxt.technology._Medium):
        arg["type"] = "medium"
        d = value.dict()
        if value in mat_lib:
            arg["defaults"] = mat_lib[value]
        else:
            arg["defaults"] = {
                "type": "constructor",
                "value": complex_json({n: d[n] for n in ("type",) + tuple(value.__fields_set__)}),
            }
    elif isinstance(value, dict) and all(
        isinstance(v, lxt.technology._Medium) for v in value.values()
    ):
        children = []
        for k, v in value.items():
            child = {
                "type": "medium",
                "name": k,
                "hideLabel": True,
                "prefix": k.title(),
            }
            d = v.dict()
            if v in mat_lib:
                child["defaults"] = mat_lib[v]
            else:
                child["defaults"] = {
                    "type": "constructor",
                    "value": complex_json({n: d[n] for n in ("type",) + tuple(v.__fields_set__)}),
                }
            children.append(child)
        arg = {
            "itemSpan": 24,
            "label": make_label(name),
            "name": name,
            "tooltip": tooltip,
            "type": "subForm",
            "children": children,
        }
    return arg


technologies = []
for tech in (lxt.lnoi400,):
    parameters = inspect.signature(tech).parameters

    args = []
    go_args = False
    name = None
    tooltip = None

    for line in tech.__doc__.splitlines():
        if go_args:
            if len(line.strip()) == 0:
                args.append(make_tech_arg(name, parameters[name].default, tooltip))
                break
            if line.startswith("      "):
                tooltip += " " + line.strip()
            else:
                if name:
                    args.append(make_tech_arg(name, parameters[name].default, tooltip))
                name = line[4 : 4 + line[4:].find(" (")]
                tooltip = line[line.find(":") + 2 :]
        else:
            go_args = line.strip() == "Args:"
    technologies.append(
        {
            "arguments": args,
            "function": tech.__name__,
            "label": pf.config.default_technology.name,
        }
    )

json = {"components": components, "technologies": technologies}

pathlib.Path("luxtelligence_lnoi400_forge/_ui_.py").write_text("json = " + repr(json))
subprocess.run(["black", "-C", "--fast", "luxtelligence_lnoi400_forge/_ui_.py"])
