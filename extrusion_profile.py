import photonforge as pf
import luxtelligence_lnoi400_forge as lxt
from matplotlib import pyplot

pf.config.default_technology = lxt.lnoi400(include_substrate=True, include_top_opening=True)

c = pf.Component("Extrusion Test")

c.add(
    "LN_RIDGE",
    pf.Rectangle(center=(0, 0), size=(60, 1)),
    "LN_SLAB",
    pf.Rectangle(center=(-15, 0), size=(30, 8)),
    "TL",
    pf.Rectangle(center=(0, 5), size=(60, 5)),
    pf.Rectangle(center=(0, -5), size=(60, 5)),
    "LN_SLAB",
    pf.stencil.linear_taper(30, (8, 1)),
    "SLAB_NEGATIVE",
    pf.Rectangle(center=(15, 0), size=(30, 8)),
)

pf.tidy3d_plot(c, x=25)
pyplot.show()
