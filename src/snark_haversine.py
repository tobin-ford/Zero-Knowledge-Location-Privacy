import argparse
import math
from pysnark.runtime import PrivVal, snark
from pysnark.fixedpoint import PrivValFxp, PubValFxp
from pysnark.branching import if_then_else

# Earth radius in kilometers (public constant)
EARTH_RADIUS = PubValFxp(6371.0)

def deg2rad(x):
    return x * PubValFxp(math.pi / 180.0)

# Hex resolution (public)
def hex_scale(res):
    return PubValFxp(math.sqrt(7) / res)

def deg2rad(x):
    return x * PubValFxp(math.pi / 180.0)

def sin_taylor(x):
    x3 = x * x * x
    x5 = x3 * x * x
    return x - x3 / 6 + x5 / 120

def cos_taylor(x):
    x2 = x * x
    x4 = x2 * x2
    return 1 - x2 / 2 + x4 / 24


def atan2_approx(y, x):
    pi_over_4 = math.pi / 4
    pi_over_2 = math.pi / 2
    abs_y = abs(y)
    abs_x = abs(x)

    use_y_dominant = abs_y > abs_x
    slope1 = y / x
    slope2 = x / y

    return if_then_else(
        use_y_dominant,
        pi_over_2 - pi_over_4 * slope2,
        pi_over_4 * slope1
    )
def acos_approx(x):
    x3 = x * x * x
    return math.pi / 2 - x - x3 / 6

def sqrt_approx(x, iters=4):
    """
    Approximate sqrt(x) using Newton-Raphson.
    x: LinCombFxp
    returns: LinCombFxp
    """
    from pysnark.branching import if_then_else

    y = x / 2 + 1

    for _ in range(iters):
        y = (y + x / y) / 2

    return y


def approx_haversine(lat1, lon1, lat2, lon2):
    # Convert to radians
    lat1_rad = deg2rad(lat1)
    lon1_rad = deg2rad(lon1)
    lat2_rad = deg2rad(lat2)
    lon2_rad = deg2rad(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # sin^2(x/2) ≈ (x/2)^2 approx
    # a = (dlat / PubValFxp(2))**2 + lat1_rad.cos() * lat2_rad.cos() * (dlon / PubValFxp(2))**2
    a = (dlat / PubValFxp(2))**2 + cos_taylor(lat1_rad) * cos_taylor(lat2_rad) * (dlon / PubValFxp(2))**2
    # c = PubValFxp(2) * a.sqrt()
    c = PubValFxp(2) * sqrt_approx(a)

    return EARTH_RADIUS * c

def main():
    parser = argparse.ArgumentParser(description="Prove two points are within a distance threshold (ZKP)")
    parser.add_argument("--lat1", type=float, required=True, help="Latitude of first point (private)")
    parser.add_argument("--lon1", type=float, required=True, help="Longitude of first point (private)")
    parser.add_argument("--lat2", type=float, required=True, help="Latitude of second point (private)")
    parser.add_argument("--lon2", type=float, required=True, help="Longitude of second point (private)")
    parser.add_argument("--limit", type=float, required=True, help="Maximum allowed distance (public, in km)")
    args = parser.parse_args()

    # Wrap private inputs
    lat1 = PrivValFxp(args.lat1)
    lon1 = PrivValFxp(args.lon1)
    lat2 = PrivValFxp(args.lat2)
    lon2 = PrivValFxp(args.lon2)

    # Public threshold
    limit = PubValFxp(args.limit)

    # Compute distance and assert it's within the threshold
    distance = approx_haversine(lat1, lon1, lat2, lon2)
    # (distance <= limit).assert_eq(1)
    (distance - limit).assert_lt(0)

    print(f"[ZKP] Success: distance is within {args.limit} km")

if __name__ == "__main__":
    main()

