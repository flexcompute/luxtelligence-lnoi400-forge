try:
    from importlib.resources import files, as_file
except ImportError:
    from importlib_resources import files, as_file


import warnings

import photonforge as pf


# Data for the components contains cell_name, gds folder, gds file name, and port data
_component_data = {
    "MMI1x2_OPTIMIZED_1550": (
        "gdscells",
        "MMI1x2",
        [
            ((-25.0, 0.0), 0, "RWG_1000"),
            ((51.75, -1.65), 180, "RWG_1000"),
            ((51.75, 1.65), 180, "RWG_1000"),
        ],
    ),
    "MMI2x2_OPTIMIZED_1550": (
        "gdscells",
        "MMI2x2",
        [
            ((-25.0, -1.75), 0, "RWG_1000"),
            ((-25.0, 1.75), 0, "RWG_1000"),
            ((101.5,-1.75), 180, "RWG_1000"),
            ((101.5,1.75), 180, "RWG_1000"),
        ],
    ),
    "SBEND_1": (
        "gdscells",
        "SBEND",
        [
            ((0.0, 0.0), 0, "RWG_1000"),
            ((110, 25), 180, "RWG_1000"),
        ],
    ),
    "UBEND_3": (
        "gdscells",
        "UBEND",
        [
            ((0.0, 0.0), 0, "RWG_3000"),
            ((0.0, 90.0), 180, "RWG_3000"),
        ],
    ),
    "LBEND_1": (
        "gdscells",
        "LBEND",
        [
            ((0.0, 0.0), 0, "RWG_1000"),
            ((80.0, 80.0), 90, "RWG_1000"),
        ],
    ),
    "EDGE_COUPLER_LIN_LIN_2": (
        "gdscells",
        "EDGE_COUPLER_LIN_LIN",
        [
            ((0.0, 0.0), 0, "SWG_250"),
            ((360.0, 0.0), 180, "RWG_1000"),
        ], 
    ),
    "GSG_PAD_LINEAR_1": (
        "gdscells",
        "GSG_PAD_LINEAR",
        [], 
    ),
    "EO_SHIFTER_1":(
        "gdscells",
        "EO_SHIFTER",
        [
            ((0.0, 7.0), 0, "RWG_1000"),
            ((1000.0, 7.0), 180, "RWG_1000"),
        ],
    ),
    "CHIP_FRAME_1":(
        "gdscells",
        "CHIP_FRAME",
        [],
    ),
}

component_names = tuple(_component_data.keys())


def component(component_name:str, technology: pf.Technology = None, **model_kwargs)-> pf.Component:
    family, libname, port_data = _component_data.get(component_name, (None,None, None))

    if family is None:
        raise KeyError(f"{component_name} is not a library component.")

    if technology is None:
        technology = pf.config.default_technology
        if not technology.name.startswith("LNOI400"):
            warnings.warn(
                f"Current default technology {technology.name} does not seems to be suppoted by "
                "the LNOI400 component library.",
                RuntimeWarning,
                1,
            )

    # Load gds files
    gdsii = files("luxtelligence_lnoi400_forge") / "library" / family / (libname + ".gds")
    with as_file(gdsii) as fname:
        c = pf.load_layout(fname, technology=technology)[component_name]

    # Add ports
    if len(port_data) > 0:
        # Add ports
        for center, input_direction, spec in port_data:
            port = pf.Port(center, input_direction, technology.ports[spec])
            c.add_port(port)


    # Add models and symmetries 
    kwargs = {}
    if any(component_name.startswith(p) for p in ("SBEND_", "UBEND_", "LBEND_")):
        kwargs["port_symmetries"] = [("P0", "P1", {"P1": "P0"})]
    elif component_name.startswith("MMI1x2_"):
        kwargs["port_symmetries"] = [("P1", "P2", {"P0": "P0", "P2": "P1"})]
    elif component_name.startswith("MMI2x2_"):
        kwargs["port_symmetries"] = [
                ("P0", "P1", {"P1": "P0", "P2": "P3", "P3": "P2"}),
                ("P0", "P2", {"P1": "P3", "P2": "P0", "P3": "P1"}),
                ("P0", "P3", {"P1": "P2", "P2": "P1", "P3": "P0"}),
            ]
    
    # Not all components like device region need a Tidy3D model
    if any(component_name.startswith(p) for p in ("MMI1x2_","MMI2x2_","SBEND_", "UBEND_", "LBEND_")):
        kwargs.update(model_kwargs)  
        tidy3d_model = pf.Tidy3DModel(**kwargs)
        c.add_model(tidy3d_model, "Tidy3DModel")

    return c