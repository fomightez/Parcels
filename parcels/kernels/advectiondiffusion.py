"""Collection of pre-built advection-diffusion kernels

See `this tutorial <https://nbviewer.jupyter.org/github/OceanParcels/parcels/blob/master/parcels/examples/tutorial_diffusion.ipynb>`_ for a detailed explanation"""
import math

import parcels.rng as ParcelsRandom


__all__ = ['DiffusionUniformKh', 'AdvectionDiffusionM1', 'AdvectionDiffusionEM', ]


def AdvectionDiffusionM1(particle, fieldset, time):
    """Kernel for 2D advection-diffusion, solved using the Milstein scheme
    at first order (M1).

    Assumes that fieldset has fields `Kh_zonal` and `Kh_meridional`
    and variable `fieldset.dres`, setting the resolution for the central
    difference gradient approximation. This should be (of the order of) the 
    local gridsize.

    This Milstein scheme is of strong and weak order 1, which is higher than the 
    Euler-Maruyama scheme. It experiences less spurious diffusivity by 
    including extra correction terms that are computationally cheap.
    
    The Wiener increment `dW` is normally distributed with zero
    mean and a standard deviation of sqrt(dt).
    """
    # Wiener increment with zero mean and std of sqrt(dt)
    dWx = ParcelsRandom.normalvariate(0, math.sqrt(math.fabs(particle.dt)))
    dWy = ParcelsRandom.normalvariate(0, math.sqrt(math.fabs(particle.dt)))

    Kxp1 = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon + fieldset.dres]
    Kxm1 = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon - fieldset.dres]
    dKdx = (Kxp1 - Kxm1) / (2 * fieldset.dres)

    u = fieldset.U[time, particle.depth, particle.lat, particle.lon]
    bx = math.sqrt(2 * fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon])

    Kyp1 = fieldset.Kh_meridional[time, particle.depth, particle.lat + fieldset.dres, particle.lon]
    Kym1 = fieldset.Kh_meridional[time, particle.depth, particle.lat - fieldset.dres, particle.lon]
    dKdy = (Kyp1 - Kym1) / (2 * fieldset.dres)

    v = fieldset.V[time, particle.depth, particle.lat, particle.lon]
    by = math.sqrt(2 * fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon])

    # Particle positions are updated only after evaluating all terms.
    particle.lon += u * particle.dt + 0.5 * dKdx * (dWx**2 + particle.dt) + bx * dWx
    particle.lat += v * particle.dt + 0.5 * dKdy * (dWy**2 + particle.dt) + by * dWy


def AdvectionDiffusionEM(particle, fieldset, time):
    """Kernel for 2D advection-diffusion, solved using the Euler-Maruyama
    scheme (EM).

    Assumes that fieldset has fields `Kh_zonal` and `Kh_meridional`
    and variable `fieldset.dres`, setting the resolution for the central
    difference gradient approximation. This should be (of the order of) the 
    local gridsize.
    
    The Euler-Maruyama scheme is of strong order 0.5 and weak order 1.
    
    The Wiener increment `dW` is normally distributed with zero
    mean and a standard deviation of sqrt(dt).
    """
    # Wiener increment with zero mean and std of sqrt(dt)
    dWx = ParcelsRandom.normalvariate(0, math.sqrt(math.fabs(particle.dt)))
    dWy = ParcelsRandom.normalvariate(0, math.sqrt(math.fabs(particle.dt)))

    Kxp1 = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon + fieldset.dres]
    Kxm1 = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon - fieldset.dres]
    dKdx = (Kxp1 - Kxm1) / (2 * fieldset.dres)
    ax = fieldset.U[time, particle.depth, particle.lat, particle.lon] + dKdx
    bx = math.sqrt(2 * fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon])

    Kyp1 = fieldset.Kh_meridional[time, particle.depth, particle.lat + fieldset.dres, particle.lon]
    Kym1 = fieldset.Kh_meridional[time, particle.depth, particle.lat - fieldset.dres, particle.lon]
    dKdy = (Kyp1 - Kym1) / (2 * fieldset.dres)
    ay = fieldset.V[time, particle.depth, particle.lat, particle.lon] + dKdy
    by = math.sqrt(2 * fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon])

    # Particle positions are updated only after evaluating all terms.
    particle.lon += ax * particle.dt + bx * dWx
    particle.lat += ay * particle.dt + by * dWy


def DiffusionUniformKh(particle, fieldset, time):
    """Kernel for simple 2D diffusion where diffusivity (Kh) is assumed uniform.
    
    Assumes that fieldset has constants `Kh_zonal` and `Kh_meridional`. This kernel 
    assumes diffusivity gradients are zero and is therefore more efficient. Since 
    the perturbation due to diffusion is in this case isotropic independent, this 
    kernel contains no advection and can be used in combination with a seperate 
    advection kernel.

    The Wiener increment `dW` is normally distributed with zero
    mean and a standard deviation of sqrt(dt).
    """
    # Wiener increment with zero mean and std of sqrt(dt)
    dWx = ParcelsRandom.normalvariate(0, math.sqrt(math.fabs(particle.dt)))
    dWy = ParcelsRandom.normalvariate(0, math.sqrt(math.fabs(particle.dt)))

    bx = math.sqrt(2 * fieldset.Kh_zonal)
    by = math.sqrt(2 * fieldset.Kh_meridional)

    particle.lon += bx * dWx
    particle.lat += by * dWy