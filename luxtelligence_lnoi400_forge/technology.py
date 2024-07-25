import tidy3d as td
import photonforge as pf
import typing
import math


_Medium = td.components.medium.MediumType

def lnoi400(
    *, 
    ln_thickness: float = 0.4,
    slab_thickness: float = 0.2,
    rwg_sidewall_angle: float = 13, # Double check this
    swg_sidewall_angle: float = 13,
    box_thickness: float = 4.7,
    clad_thickness: float = 2, # Double check this 
    tl_thickness: float = 0.9,
    tl_separation: float = 1,
    include_substrate: bool = True,
    include_top_opening: bool = True,
    sio2: _Medium = td.material_library["SiO2"]["Palik_Lossless"],
    si: _Medium = td.material_library["cSi"]["Li1993_293K"],
    ln: _Medium = td.material_library["LiNbO3"]["Zelmon1997"](optical_axis = 1), #for X-cut lithium niobate
    tl_metal: _Medium = td.material_library['Au']['JohnsonChristy1972'],
    opening: _Medium = td.Medium(permittivity=1.0, name="Opening"),
) -> pf.Technology:

    # Layers
    layers = {
        # As described in section 4.1 Layers in process order
        "LN_STRIP": pf.LayerSpec((2, 0), "Lithium niobate ridge etch", "#7d57de18", ":"),
        "LN_RIB": pf.LayerSpec((3, 0), "Display of the slab around the LN ridges", "#00008018", ":"),
        "RIB_NEGATIVE": pf.LayerSpec((3, 1), "Tone inversion for the LN slab etch", "#6750bf18", "hollow"),
        "LABELS": pf.LayerSpec((4, 0), "Labels - etched alongside with LN ridges", "#5179b518", ":"),
        "CHIP_CONTOUR": pf.LayerSpec((6, 0), "Chip frame extent (component placement area)", "#ffc6b818", "hollow"),
        "CHIP_EXCLUSION_ZONE": pf.LayerSpec((6, 1), "Chip boundary including the exclusion zone", "#00fe9c18", "hollow"),
        "TL": pf.LayerSpec((21, 0), "Metal transmission lines", "#ffbf0018", "\\\\"),
        "HT": pf.LayerSpec((21, 1), "Metal heaters", "#ffbf0018", "."),
        "DOC": pf.LayerSpec((201, 0), "Labels for GDS layout (not fabricated)", "#80a8ff18", "."),
    }

    # Extrusion specifications
    bounds = pf.MaskSpec() # Empty mask for all chip bounds
    swg_mask = pf.MaskSpec((2, 0))
    rwg_mask = pf.MaskSpec((3, 0))
    tl_mask = pf.MaskSpec((21, 0))
    ht_mask = pf.MaskSpec((21, 1))
    rib_negative_mask = pf.MaskSpec((3,1),(3,0), '-')

    extrusion_specs =[]

    z_sub = -box_thickness
    z_min_tl = ln_thickness+tl_separation
    z_max_tl = z_min_tl+tl_thickness
    
    # Substrate 
    if include_substrate:
        extrusion_specs.append(pf.ExtrusionSpec(bounds,si, (-pf.Z_INF, z_sub)))

    # Air region above the chip
    if include_top_opening:
        extrusion_specs.append(pf.ExtrusionSpec(bounds, opening, (ln_thickness+tl_thickness+tl_separation, pf.Z_INF)))

    # Optical layers
    extrusion_specs.extend(
        [
            # Lithium niobate layers
            pf.ExtrusionSpec(bounds, ln, (0, slab_thickness), 0),
            pf.ExtrusionSpec(swg_mask, ln, (0, ln_thickness), swg_sidewall_angle),
            pf.ExtrusionSpec(rib_negative_mask, sio2, (0, ln_thickness), -swg_sidewall_angle),
        ]
    )

    # Metal layers
    extrusion_specs.append(pf.ExtrusionSpec(tl_mask, tl_metal,(z_min_tl, z_max_tl)))

    # Heater layers
    extrusion_specs.append(pf.ExtrusionSpec(ht_mask, tl_metal,(z_min_tl, z_max_tl)))

    # Define ports

    ln_port_gap = min(1, box_thickness)
    ln_port_limits = (-ln_port_gap,ln_thickness+ln_port_gap)
    
    ports = {
        "RWG_1000": pf.PortSpec(
            description="LN single mode ridge waveguide for C-band, TE mode",
            width=5,
            limits=ln_port_limits,
            num_modes=2,
            target_neff=2.2,
            path_profiles=((1, 0, (2, 0)),(10, 0, (3, 0))),
        ),
        "RWG_3000": pf.PortSpec(
            description="LN multimode mode ridge for C-band, TE mode",
            width=5,
            limits=ln_port_limits,
            num_modes=2,
            target_neff=2.2,
            path_profiles=((3, 0, (2, 0)),(12, 0, (3, 0))),
        ),
        "SWG_250": pf.PortSpec(
            description="LN strip waveguide for C-band, TE mode",
            width=5,
            limits=ln_port_limits,
            num_modes=2,
            target_neff=2.2,
            path_profiles=((0.25, 0, (2, 0)),),
        ),
    }

    
    return pf.Technology("LNOI400","rev. 1", layers, extrusion_specs, ports, sio2)
    