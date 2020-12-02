from ..common import *


@ti.data_oriented
class Material:
    def __init__(self, **kwargs):
        @ti.materialize_callback
        def _():
            for k, v in kwargs.items():
                getattr(self, k)[None] = v

    @ti.func
    def brdf(self, nrm, idir, odir):
        return 1


class CookTorrance(Material):
    def __init__(self, **kwargs):
        self.roughness = ti.field(float, ())
        self.metallic = ti.field(float, ())
        self.specular = ti.field(float, ())
        self.basecolor = ti.Vector.field(3, float, ())

        kwargs.setdefault('roughness', 0.4)
        kwargs.setdefault('metallic', 0.0)
        kwargs.setdefault('specular', 0.5)
        kwargs.setdefault('basecolor', (1, 1, 1))

        super().__init__(**kwargs)

    @ti.func
    def brdf(self, nrm, idir, odir):
        EPS = 1e-10
        roughness = self.roughness[None]
        metallic = self.metallic[None]
        specular = self.specular[None]
        basecolor = self.basecolor[None]

        half = (idir + odir).normalized()
        NoH = max(EPS, half.dot(nrm))
        NoL = max(EPS, idir.dot(nrm))
        NoV = max(EPS, odir.dot(nrm))
        HoV = min(1 - EPS, max(EPS, half.dot(odir)))

        # Trowbridge-Reitz GGX microfacet distribution
        ndf = roughness**2 / (NoH**2 * (roughness**2 - 1) + 1)**2 / ti.pi

        # Smith's method with Schlick-GGX
        k = (roughness + 1)**2 / 8
        vdf = NoV * NoL / ((NoV * (1 - k) + k) * (NoL * (1 - k) + k))

        # Fresnel-Schlick approximation
        f0 = metallic * basecolor + (1 - metallic) * 0.16 * specular**2
        ks, kd = f0, (1 - f0) * (1 - self.metallic)
        fdf = f0 + (1 - f0) * (1 - HoV)**5

        return kd * basecolor + ks * fdf * vdf * ndf / (NoV * NoL)


class BlinnPhong(Material):
    def __init__(self, **kwargs):
        self.shineness = ti.field(float, ())

        kwargs.setdefault('shineness', 10)

        super().__init__(**kwargs)

    @ti.func
    def brdf(self, nrm, idir, odir):
        shineness = self.shineness[None]
        half = (odir + idir).normalized()
        return (shineness + 8) / 8 * pow(max(0, half.dot(nrm)), shineness)
