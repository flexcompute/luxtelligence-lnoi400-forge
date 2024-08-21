from .utils import _cpw_info

import photonforge as _pf

import warnings as _warn
import typing as _typ


@_pf.parametric_component(name_prefix="MMI1x2")
def mmi1x2(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    width: float = 6.0,
    length: float = 26.75,
    taper_width: float = 1.5,
    taper_length: float = 25.0,
    port_ratio: float = 0.55,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """MMI with 1 port on one side and 2 ports on the other.

    Args:
        port_spec: Port specification describing waveguide cross-section.
        width: Width of the MMI section.
        length: Length of the MMI section.
        taper_width: Width of the taper.
        taper_length: Length of the taper.
        port_ratio: Ratio of the distance between the waveguides and the MMI
          width.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        MMI Component with layout, ports and model.
    """
    if port_ratio * width + taper_width > width:
        raise ValueError("Condition 'port_ratio * width + taper_width ≤ width' is not satisfied.")
    if port_ratio * width < taper_width:
        _warn.warn("Waveguide tapers will overlap.", RuntimeWarning, 1)

    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)

    core_width, _, core_layer = min(p for p in port_spec.path_profiles if p[1] == 0)
    clad_width, _, clad_layer = max(p for p in port_spec.path_profiles if p[1] == 0)
    margin = 0.5 * (clad_width - core_width)

    c.add(
        core_layer,
        _pf.Rectangle((0, -0.5 * width), (length, 0.5 * width)),
        clad_layer,
        _pf.Rectangle((0, -0.5 * width - margin), (length, 0.5 * width + margin)),
    )

    for layer, path in port_spec.get_paths((-taper_length, 0)):
        if layer == core_layer:
            c.add(layer, path.segment((0, 0), taper_width))
        else:
            c.add(layer, path.segment((0, 0)))

    x = length + taper_length
    offset = width * port_ratio * 0.5
    for y in (-offset, offset):
        for layer, path in port_spec.get_paths((x, y)):
            if layer == core_layer:
                c.add(layer, path.segment((length, y), taper_width))
            else:
                c.add(layer, path.segment((length, y)))

    c.add_port(_pf.Port((-taper_length, 0), 0, port_spec))
    c.add_port(_pf.Port((x, -offset), 180, port_spec, inverted=True))
    c.add_port(_pf.Port((x, offset), 180, port_spec, inverted=True))

    model_kwargs = {"port_symmetries": [("P1", "P2", {"P0": "P0", "P2": "P1"})]}
    model_kwargs.update(tidy3d_model_kwargs)
    c.add_model(_pf.Tidy3DModel(**model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="MMI2x2")
def mmi2x2(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    width: float = 5.0,
    length: float = 76.5,
    taper_width: float = 1.5,
    taper_length: float = 25.0,
    port_ratio: float = 0.7,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """MMI with 2 ports on each side.

    Args:
        port_spec: Port specification describing waveguide cross-section.
        width: Width of the MMI section.
        length: Length of the MMI section.
        taper_width: Width of the taper.
        taper_length: Length of the taper.
        port_ratio: Ratio of the distance between the waveguides and the MMI
          width.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        MMI Component with layout, ports and model.
    """
    if port_ratio * width + taper_width > width:
        raise ValueError("Condition 'port_ratio * width + taper_width ≤ width' is not satisfied.")
    if port_ratio * width < taper_width:
        _warn.warn("Waveguide tapers will overlap.", RuntimeWarning, 1)

    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)

    core_width, _, core_layer = min(p for p in port_spec.path_profiles if p[1] == 0)
    clad_width, _, clad_layer = max(p for p in port_spec.path_profiles if p[1] == 0)
    margin = 0.5 * (clad_width - core_width)

    c.add(
        core_layer,
        _pf.Rectangle((0, -0.5 * width), (length, 0.5 * width)),
        clad_layer,
        _pf.Rectangle((0, -0.5 * width - margin), (length, 0.5 * width + margin)),
    )

    offset = width * port_ratio * 0.5
    for y in (-offset, offset):
        for layer, path in port_spec.get_paths((-taper_length, y)):
            if layer == core_layer:
                c.add(layer, path.segment((0, y), taper_width))
            else:
                c.add(layer, path.segment((0, y)))

    x = length + taper_length
    for y in (-offset, offset):
        for layer, path in port_spec.get_paths((x, y)):
            if layer == core_layer:
                c.add(layer, path.segment((length, y), taper_width))
            else:
                c.add(layer, path.segment((length, y)))

    c.add_port(_pf.Port((-taper_length, -offset), 0, port_spec))
    c.add_port(_pf.Port((-taper_length, offset), 0, port_spec))
    c.add_port(_pf.Port((x, -offset), 180, port_spec, inverted=True))
    c.add_port(_pf.Port((x, offset), 180, port_spec, inverted=True))

    model_kwargs = {"port_symmetries": [("P1", "P2", {"P0": "P0", "P2": "P1"})]}
    model_kwargs.update(tidy3d_model_kwargs)
    c.add_model(_pf.Tidy3DModel(**model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="SBEND")
def s_bend_vert(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    h_extent: float = 100.0,
    v_offset: float = 25.0,
    dx_straight: float = 5.0,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """S-bend waveguide section.

    Args:
        port_spec: Port specification describing waveguide cross-section.
        dx_straight: Horizontal extent of the straight segments at the bend
          input and output.
        v_offset: The vertical offset of the bend.
        h_extent: The horizontal extent of the bend.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        Component with the S-bend, ports and model.
    """
    h_extent = abs(h_extent)
    dx_straight = abs(dx_straight)
    ratio = abs(v_offset) / max(h_extent, 1e-12)
    if ratio > 0.285714:
        _warn.warn(
            "S bend might be too tight. Make sure the geometry is correct.", RuntimeWarning, 1
        )

    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)
    for layer, path in port_spec.get_paths((0, 0)):
        if dx_straight > 0:
            path.segment((dx_straight, 0))
        path.bezier(
            [(h_extent / 3, 0), (h_extent * 2 / 3, v_offset), (h_extent, v_offset)], relative=True
        )
        if dx_straight > 0:
            path.segment((h_extent + 2 * dx_straight, v_offset))
        c.add(layer, path)

    c.add_port(_pf.Port((0, 0), 0, port_spec))
    c.add_port(_pf.Port((h_extent + 2 * dx_straight, v_offset), 180, port_spec, inverted=True))

    model_kwargs = {"port_symmetries": [("P0", "P1", {"P1": "P0"})]}
    model_kwargs.update(tidy3d_model_kwargs)
    c.add_model(_pf.Tidy3DModel(**model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="UBEND")
def u_turn_bend(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    v_offset: float = 80.0,
    euler_fraction: float = 1.0,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """180° bend.

    Args:
        port_spec: Port specification describing waveguide cross-section.
        v_offset: The vertical offset of the bend.
        euler_fraction: Fraction of the bend that is created using an Euler
          spiral (see :func:`photonforge.Path.arc`).
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        Component with the bend, ports and model.
    """
    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)

    endpoint = (0, v_offset)
    radius = abs(v_offset) / 2
    a0, a1 = (-90, 90) if v_offset > 0 else (90, -90)
    for layer, path in port_spec.get_paths((0, 0)):
        path.arc(a0, a1, radius, euler_fraction=euler_fraction, endpoint=endpoint)
        c.add(layer, path)

    c.add_port(_pf.Port((0, 0), 0, port_spec))
    c.add_port(_pf.Port(endpoint, 0, port_spec, inverted=True))

    model_kwargs = {"port_symmetries": [("P0", "P1", {"P1": "P0"})]}
    model_kwargs.update(tidy3d_model_kwargs)
    c.add_model(_pf.Tidy3DModel(**model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="UBEND_RACETRACK")
def u_bend_racetrack(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG3000",
    v_offset: float = 90.0,
    euler_fraction: float = 1.0,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """180° bend with defaults suitable for low-loss racetrack resonator.

    Args:
        port_spec: Port specification describing waveguide cross-section.
        v_offset: The vertical offset of the bend.
        euler_fraction: Fraction of the bend that is created using an Euler
          spiral (see :func:`photonforge.Path.arc`).
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        Component with the bend, ports and model.
    """
    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)

    endpoint = (0, v_offset)
    radius = abs(v_offset) / 2
    a0, a1 = (-90, 90) if v_offset > 0 else (90, -90)
    for layer, path in port_spec.get_paths((0, 0)):
        path.arc(a0, a1, radius, euler_fraction=euler_fraction, endpoint=endpoint)
        c.add(layer, path)

    c.add_port(_pf.Port((0, 0), 0, port_spec))
    c.add_port(_pf.Port(endpoint, 0, port_spec, inverted=True))

    model_kwargs = {"port_symmetries": [("P0", "P1", {"P1": "P0"})]}
    model_kwargs.update(tidy3d_model_kwargs)
    c.add_model(_pf.Tidy3DModel(**model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="LBEND")
def l_turn_bend(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    effective_radius: float = 80.0,
    euler_fraction: float = 1.0,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """90° bend.

    Args:
        port_spec: Port specification describing waveguide cross-section.
        effective_radius: Effective radius of the bend (horizontal/vertical
          extent).
        euler_fraction: Fraction of the bend that is created using an Euler
          spiral (see :func:`photonforge.Path.arc`).
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        Component with the bend, ports and model.
    """
    if effective_radius <= 0:
        raise ValueError("'radius' must be positive.")

    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)

    endpoint = (effective_radius, effective_radius)
    for layer, path in port_spec.get_paths((0, 0)):
        path.arc(-90, 0, effective_radius, euler_fraction=euler_fraction, endpoint=endpoint)
        c.add(layer, path)

    c.add_port(_pf.Port((0, 0), 0, port_spec))
    c.add_port(_pf.Port(endpoint, -90, port_spec, inverted=True))

    model_kwargs = {"port_symmetries": [("P0", "P1", {"P1": "P0"})]}
    model_kwargs.update(tidy3d_model_kwargs)
    c.add_model(_pf.Tidy3DModel(**model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="EDGE_COUPLER_LIN_LIN")
def double_linear_inverse_taper(
    *,
    start_port_spec: _typ.Union[str, _pf.PortSpec] = "SWG250",
    end_port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    lower_taper_end_width: float = 2.05,
    lower_taper_length: float = 120.0,
    upper_taper_start_width: float = 0.25,
    upper_taper_length: float = 240.0,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """Dual layer inverse taper designed for matching with a lensed fiber.

    The taper transitions from a wire to a rib waveguide.

    Args:
        start_port_spec: Port specification describing the wire waveguide.
        end_port_spec: Port specification describing rib waveguide.
        lower_taper_end_width: Lower taper width at the start of the upper
          taper.
        lower_taper_length: Length of the wire waveguide taper section.
        upper_taper_start_width: The start width of the rib waveguide
          section.
        upper_taper_length: Length of the rib waveguide taper.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        Component with the taper, ports and model.
    """
    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(start_port_spec, str):
        start_port_spec = technology.ports[start_port_spec]
    if isinstance(end_port_spec, str):
        end_port_spec = technology.ports[end_port_spec]

    c = _pf.Component(name, technology=technology)

    lower_taper_start_width = min(p[0] for p in start_port_spec.path_profiles if p[1] == 0)
    upper_taper_end_width = min(p[0] for p in end_port_spec.path_profiles if p[1] == 0)

    slope = (lower_taper_end_width - lower_taper_start_width) / lower_taper_length
    lower_taper_end_width = lower_taper_start_width + slope * (
        lower_taper_length + upper_taper_length
    )

    length = lower_taper_length + upper_taper_length
    c.add(
        "LN_STRIP",
        _pf.stencil.linear_taper(
            upper_taper_length, (upper_taper_start_width, upper_taper_end_width)
        ).translate((lower_taper_length, 0)),
        "LN_RIB",
        _pf.stencil.linear_taper(length, (lower_taper_start_width, lower_taper_end_width)),
    )

    c.add_port(_pf.Port((0, 0), 0, start_port_spec))
    c.add_port(_pf.Port((length, 0), 180, end_port_spec, inverted=True))

    c.add_model(_pf.Tidy3DModel(**tidy3d_model_kwargs), "Tidy3D")
    return c


@_pf.parametric_component(name_prefix="GSG_PAD_LINEAR")
def cpw_probe_pad_linear(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "UniCPW",
    pad_width: float = 80.0,
    length_straight: float = 30.0,
    length_tapered: float = 100.0,
    technology: _pf.Technology = None,
    name: str = "",
    tidy3d_model_kwargs: dict = {},
) -> _pf.Component:
    """Dual layer inverse taper designed for matching with a lensed fiber.

    The taper transitions from a wire to a rib waveguide.

    Args:
        port_spec: Port specification describing the transmission line
          cross-section.
        pad_width: Width of the central conductor on the pad side.
        length_straight: Length of the straight section of the taper on the
          pad side.
        length_tapered: Length of the tapered section.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        tidy3d_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.Tidy3DModel`.

    Returns:
        Component with the taper and port.
    """
    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]

    c = _pf.Component(name, technology=technology)

    central_width, gap, ground_width, offset, layer = _cpw_info(port_spec)

    scaling = pad_width / central_width
    y_max = offset + 0.5 * ground_width
    y_gnd = offset - 0.5 * ground_width
    y_sig = 0.5 * central_width
    length = length_straight + length_tapered

    if scaling * y_gnd >= y_max:
        raise ValueError(
            f"'pad_width' must be less than {y_max / y_gnd * central_width} for the selected "
            f"port specification."
        )

    sig_vertices = [
        (0, -scaling * y_sig),
        (length_straight, -scaling * y_sig),
        (length, -y_sig),
        (length, y_sig),
        (length_straight, scaling * y_sig),
        (0, scaling * y_sig),
    ]

    gnd_vertices = [
        (0, scaling * y_gnd),
        (length_straight, scaling * y_gnd),
        (length, y_gnd),
        (length, y_max),
        (0, y_max),
    ]

    c.add(
        layer,
        _pf.Polygon(sig_vertices),
        _pf.Polygon(gnd_vertices),
        _pf.Polygon([(x, -y) for x, y in gnd_vertices]),
    )

    c.add_port(_pf.Port((length, 0), 180, port_spec, inverted=True))
    return c


@_pf.parametric_component(name_prefix="EO_SHIFTER")
def eo_phase_shifter(
    *,
    port_spec: _typ.Union[str, _pf.PortSpec] = "RWG1000",
    tl_port_spec: _typ.Union[str, _pf.PortSpec] = "UniCPW-EO",
    taper_length: float = 100.0,
    rib_core_width_modulator: float = 2.5,
    modulation_length: float = 1000.0,
    draw_cpw: bool = True,
    technology: _pf.Technology = None,
    name: str = "",
    circuit_model_kwargs: dict = {},
) -> _pf.Component:
    """Dual layer inverse taper designed for matching with a lensed fiber.

    The taper transitions from a wire to a rib waveguide.

    Args:
        port_spec: Port specification for the optical waveguide.
        tl_port_spec: Port specification for the CPW transmission line.
        taper_length: Length of the tapering section between the modulation
          and routing waveguides.
        rib_core_width_modulator: Waveguide core width in the phase
          modulation section.
        modulation_length: Length of the phase modulation section.
        draw_cpw: If ``False``, the CPW transmission line is not included.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        circuit_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.CircuitModel`.

    Returns:
        Component with the modulator, ports, and model.
    """
    if taper_length <= 0:
        raise ValueError("'taper_length' must be positive.")
    if modulation_length <= 2 * taper_length:
        raise ValueError("'modulation_length' must be larger than '2 * taper_length'.")

    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )
    if isinstance(port_spec, str):
        port_spec = technology.ports[port_spec]
    if isinstance(tl_port_spec, str):
        tl_port_spec = technology.ports[tl_port_spec]

    core_width, _, _ = min(port_spec.path_profiles)
    added_width = rib_core_width_modulator - core_width
    mod_spec = port_spec.copy()
    mod_spec.path_profiles = {(w + added_width, g, a) for w, g, a in port_spec.path_profiles}

    taper = _pf.parametric.transition(
        port_spec1=port_spec, port_spec2=mod_spec, length=taper_length, technology=technology
    )
    straight = _pf.parametric.straight(
        port_spec=mod_spec, length=modulation_length - 2 * taper_length, technology=technology
    )

    central_width, gap, _, _, _ = _cpw_info(tl_port_spec)
    y = 0.5 * (central_width + gap)

    c = _pf.Component(name, technology=technology)
    r = _pf.Reference(taper, (0, y))
    c.add(r)
    c.add_port(r["P0"])
    r = c.add_reference(straight).connect("P0", r["P1"])
    r = c.add_reference(taper).connect("P1", r["P1"])
    c.add_port(r["P0"])

    if draw_cpw:
        tl = _pf.parametric.straight(
            port_spec=tl_port_spec, length=modulation_length, technology=technology
        )
        r = c.add_reference(tl)
        tl.remove_port("P0")
        tl.remove_port("P1")
        # c.add_port((r["P0"], r["P1"]))

    c.add_model(_pf.CircuitModel(**circuit_model_kwargs), "Circuit")
    return c


@_pf.parametric_component(name_prefix="MZM")
def mz_modulator_unbalanced(
    *,
    splitter: _pf.Component = None,
    tl_port_spec: _typ.Union[str, _pf.PortSpec] = "UniCPW-EO",
    taper_length: float = 100.0,
    rib_core_width_modulator: float = 2.5,
    modulation_length: float = 7500.0,
    length_imbalance: float = 100.0,
    bias_tuning_section_length: float = 750.0,
    rf_pad_start_width: float = 80.0,
    rf_pad_length_straight: float = 10.0,
    rf_pad_length_tapered: float = 190.0,
    draw_cpw: bool = True,
    technology: _pf.Technology = None,
    name: str = "",
    circuit_model_kwargs: dict = {},
) -> _pf.Component:
    """Mach-Zehnder modulator based on the Pockels effect.

    The modulator works in a differential push-pull configuration driven by
    a single GSG line.

    Args:
        splitter: 1×2 MMI splitter used in the modulator. If not set, the
          default MMI is used.
        tl_port_spec: Port specification for the CPW transmission line.
        taper_length: Length of the tapering section between the modulation
          and routing waveguides.
        rib_core_width_modulator: Waveguide core width in the phase
          modulation section.
        modulation_length: Length of the phase modulation section.
        length_imbalance: Length difference between the two arms of the MZI.
        bias_tuning_section_length: Length of the horizontal section that
          can be used for phase tuning.
        rf_pad_start_width: Width of the central conductor on the pad side.
        rf_pad_length_straight: Length of the straight section of the taper
          on the pad side.
        rf_pad_length_tapered: Length of the tapered section.
        draw_cpw: If ``False``, the CPW transmission line is not included.
        technology: Component technology. If ``None``, the default
          technology is used.
        name: Component name.
        circuit_model_kwargs: Dictionary of keyword arguments passed to the
          component's :class:`photonforge.CircuitModel`.

    Returns:
        Component with the modulator, ports, and model.
    """
    if taper_length <= 0:
        raise ValueError("'taper_length' must be positive.")
    if modulation_length <= 2 * taper_length:
        raise ValueError("'modulation_length' must be larger than '2 * taper_length'.")

    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )

    if isinstance(tl_port_spec, str):
        tl_port_spec = technology.ports[tl_port_spec]

    if splitter is None:
        splitter = mmi1x2(technology=technology)

    splitter_ports = sorted(splitter.ports.items())
    if len(splitter_ports) < 3:
        raise TypeError("'splitter' is expected to be a component with 3 ports.")
    port_spec = splitter_ports[0][1].spec
    splitter_port_distance = abs(splitter_ports[2][1].center[1] - splitter_ports[1][1].center[1])

    central_width, tl_gap, _, _, _ = _cpw_info(tl_port_spec)
    phase_shifters_distance = central_width + tl_gap
    phase_shifter = eo_phase_shifter(
        port_spec=port_spec,
        tl_port_spec=tl_port_spec,
        taper_length=taper_length,
        rib_core_width_modulator=rib_core_width_modulator,
        modulation_length=modulation_length,
        draw_cpw=False,
        technology=technology,
    )

    scaling = rf_pad_start_width / central_width
    pad_gap_distance = scaling * (central_width + tl_gap)
    input_s_offset = 0.5 * (pad_gap_distance - splitter_port_distance)
    input_s_bend = s_bend_vert(
        port_spec=port_spec,
        h_extent=input_s_offset * 3.6,
        v_offset=input_s_offset,
        dx_straight=5.0,
        technology=technology,
    )

    pad_s_straight = rf_pad_length_straight * 0.5
    pad_s_offset = 0.5 * (phase_shifters_distance - pad_gap_distance)
    pad_s_bend = s_bend_vert(
        port_spec=port_spec,
        h_extent=rf_pad_length_straight + rf_pad_length_tapered - 2 * pad_s_straight,
        v_offset=pad_s_offset,
        dx_straight=pad_s_straight,
        technology=technology,
    )

    bend = l_turn_bend(
        port_spec=port_spec, effective_radius=75, euler_fraction=1.0, technology=technology
    )

    short_length = 20.0
    long_straight = _pf.parametric.straight(
        port_spec=port_spec, length=short_length + abs(length_imbalance) / 2, technology=technology
    )
    short_straight = _pf.parametric.straight(
        port_spec=port_spec, length=short_length, technology=technology
    )
    if length_imbalance > 0:
        top_straight = long_straight
        bot_straight = short_straight
    else:
        top_straight = short_straight
        bot_straight = long_straight

    bias_straight = _pf.parametric.straight(
        port_spec=port_spec, length=bias_tuning_section_length, technology=technology
    )

    c = _pf.Component(name, technology=technology)
    ps_top = _pf.Reference(phase_shifter)
    ps_bot = _pf.Reference(phase_shifter, (0, -phase_shifters_distance))
    c.add(ps_top, ps_bot)

    # Input side, top
    r_top = c.add_reference(pad_s_bend).connect("P1", ps_top["P0"])
    r_top = c.add_reference(input_s_bend).connect("P1", r_top["P0"])

    r_input = c.add_reference(splitter).connect(splitter_ports[2][0], r_top["P0"])
    c.add_port(r_input[splitter_ports[0][0]])

    # Input side, bottom
    r_bot = c.add_reference(pad_s_bend).mirror().connect("P1", ps_bot["P0"])
    r_bot = c.add_reference(input_s_bend).mirror().connect("P1", r_bot["P0"])

    # Output side, top
    r_top = c.add_reference(pad_s_bend).mirror().connect("P0", ps_top["P1"])
    r_top = c.add_reference(bend).connect("P0", r_top["P1"])
    r_top = c.add_reference(top_straight).connect("P0", r_top["P1"])
    r_top = c.add_reference(bend).connect("P1", r_top["P1"])
    r_top = c.add_reference(bias_straight).connect("P0", r_top["P0"])
    r_top = c.add_reference(bend).connect("P1", r_top["P1"])
    r_top = c.add_reference(top_straight).connect("P0", r_top["P0"])

    # Output side, bottom
    r_bot = c.add_reference(pad_s_bend).connect("P0", ps_bot["P1"])
    r_bot = c.add_reference(bend).connect("P1", r_bot["P1"])
    r_bot = c.add_reference(bot_straight).connect("P0", r_bot["P0"])
    r_bot = c.add_reference(bend).connect("P0", r_bot["P1"])
    r_bot = c.add_reference(bias_straight).connect("P0", r_bot["P1"])
    r_bot = c.add_reference(bend).connect("P0", r_bot["P1"])
    r_bot = c.add_reference(bot_straight).connect("P0", r_bot["P1"])

    out_bend = l_turn_bend(
        port_spec=port_spec,
        effective_radius=r_top["P1"].center[1] - 0.5 * splitter_port_distance,
        euler_fraction=1.0,
        technology=technology,
    )

    r_top = c.add_reference(out_bend).connect("P0", r_top["P1"])
    r_bot = c.add_reference(out_bend).connect("P1", r_bot["P1"])

    r_output = c.add_reference(splitter).connect(splitter_ports[2][0], r_bot["P0"])
    c.add_port(r_output[splitter_ports[0][0]])

    if draw_cpw:
        pad = cpw_probe_pad_linear(
            port_spec=tl_port_spec,
            pad_width=rf_pad_start_width,
            length_straight=rf_pad_length_straight,
            length_tapered=rf_pad_length_tapered,
            technology=technology,
        )
        tl = _pf.parametric.straight(
            port_spec=tl_port_spec, length=modulation_length, technology=technology
        )
        tl_ref = c.add_reference(tl)
        c.add_reference(pad).connect("P0", tl_ref["P0"])
        c.add_reference(pad).connect("P0", tl_ref["P1"])

    c.add_model(_pf.CircuitModel(**circuit_model_kwargs), "Circuit")
    return c


@_pf.parametric_component(name_prefix="CHIP_FRAME")
def chip_frame(
    *,
    x_size: _typ.Literal[5000, 5050, 10000, 10100, 20000, 20200] = 10100,
    y_size: _typ.Literal[5000, 5050, 10000, 10100, 20000, 20200] = 5050,
    name: str = "",
    technology: _pf.Technology = None,
) -> _pf.Component:
    """Chip extent and exclusion zone.

    Provide the chip extent and the exclusion zone around the chip frame.
    In the exclusion zone, only the edge couplers routing to the chip facet
    should be placed. Allowed chip dimensions (in either direction) are
    5050 μm, 10100 μm, and 20200 μm.

    Args:
        x_size: Chip dimension in the horizontal direction.
        y_size: Chip dimension in the vertical direction.

    Returns:
        Component with chip frame.
    """
    if technology is None:
        technology = _pf.config.default_technology
        if "LNOI400" not in technology.name:
            _warn.warn(
                f"Current default technology {technology.name} does not seem supported by the "
                "Luxtelligence LNOI400 component library.",
                RuntimeWarning,
                1,
            )

    if x_size < 10000:
        x_size = 5050
    elif x_size < 20000:
        x_size = 10100
    else:
        x_size = 20200

    if y_size < 10000:
        y_size = 5050
    elif y_size < 20000:
        y_size = 10100
    else:
        y_size = 20200

    if x_size == 5050 and y_size == 5050:
        raise ValueError("The minimal die size is 5050 μm × 10100 μm.")

    return _pf.Component(name, technology=technology).add(
        (6, 1),
        _pf.Rectangle((0, 0), (x_size, y_size)),
        (6, 0),
        _pf.Rectangle((50, 50), (x_size - 50, y_size - 50)),
        # (201, 0),
        # _pf.Rectangle((0, 0), (75, 75)),
        # _pf.Rectangle((x_size - 75, 0), (x_size, 75)),
        # _pf.Rectangle((0, y_size - 75), (75, y_size)),
        # _pf.Rectangle((x_size - 75, y_size - 75), (x_size, y_size)),
    )
