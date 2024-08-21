# Luxtelligence LNOI400

This python module implements the Luxtelligence LNOI400 PDK as components and
technology specification for
[PhotonForge](https://docs.flexcompute.com/projects/photonforge/)


## Installation

### Python interface

Installation via `pip`:

    pip install --user luxtelligence_lnoi400_forge-0.9.0-py3-none-any.whl

### PhotonForge Web UI

In the Tidy3D web interface, go to your [*Account
Center*](https://tidy3d.simulation.cloud/account) and upload the token file
(.tok) under *PhotonForge Libraries* to enable this module.


## Usage

The simplest way to use the this PDK in PhotonForge is to set its technology as
default:

    import photonforge as pf
    import luxtelligence_lnoi400_forge as lxt

    tech = lxt.lnoi400()
    pf.config.default_technology = tech


The `lnoi400` function creates a parametric technology and accepts a number of
parameters to fine-tune the technology.

PDK components are available in the `component` submodule. The list of
components can be discovered by:

    dir(lxt.component)
    
    pdk_component = lxt.component.mmi1x2()

Utility functions `cpw_spec` and `place_edge_couplers` are also available for
generating CPW port specifications and placing edge couplers at chip boudaries.

More information can be obtained in the documentation for each function:

    help(lxt.lnoi400)

    help(lxt.component.mmi1x2)

    help(lxt.place_edge_couplers)


## Warnings

Please note that the 3D structures obtained by extrusion through this module's
technologies are a best approximation of the intended fabricated structures,
but the actual final dimensions may differ due to several fabrication-specific
effects. In particular, doping profiles are represented with hard-boundary,
homogeneous solids, but, in practice will present process-dependent variations
with smooth boundaries.
