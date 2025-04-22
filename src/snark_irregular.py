from pysnark.runtime import snark
from pysnark.fixedpoint import PrivValFxp, PubValFxp
from pysnark.branching import if_then_else
import math
import argparse

NUM_BINS = 36
SCALE = 256

def deg2rad(x):
    return x * PubValFxp(math.pi / 180)

def sin_taylor(x):
    x3 = x * x * x
    x5 = x3 * x * x
    return x - x3 / 6 + x5 / 120

def cos_taylor(x):
    x2 = x * x
    x4 = x2 * x2
    return 1 - x2 / 2 + x4 / 24

# def atan2_approx(y, x):
#     pi_4 = PubValFxp(math.pi / 4)
#     pi_2 = PubValFxp(math.pi / 2)
#     abs_y = abs(y)
#     abs_x = abs(x)
#     cond = abs_y > abs_x
#     return if_then_else(cond, pi_2 - pi_4 * (x / y), pi_4 * (y / x))

def safe_div(numer, denom, epsilon=1e-3):
    abs_denom = abs(denom)
    safe_denom = if_then_else(abs_denom < PubValFxp(epsilon), PubValFxp(epsilon), denom)
    return numer / safe_denom


def atan2_approx(y, x):
    pi_4 = PubValFxp(math.pi / 4)
    pi_2 = PubValFxp(math.pi / 2)

    # Always-safe denominators
    epsilon = PubValFxp(1e-3)
    safe_x = if_then_else(abs(x) < epsilon, epsilon, x)
    safe_y = if_then_else(abs(y) < epsilon, epsilon, y)

    slope1 = y / safe_x
    slope2 = x / safe_y

    return if_then_else(abs(y) > abs(x),
                        pi_2 - pi_4 * slope2,
                        pi_4 * slope1)

def spherical_to_plane(lat, lon, lat0, lon0):
    R = PubValFxp(6371.0)
    lat_rad = deg2rad(lat)
    lon_rad = deg2rad(lon)
    lat0_rad = deg2rad(lat0)
    lon0_rad = deg2rad(lon0)
    x = R * (lon_rad - lon0_rad) * cos_taylor(lat0_rad)
    y = R * (lat_rad - lat0_rad)
    return x, y

def prove_location(lat_priv, lon_priv, reference_lat, reference_lon):
    lookup_table = []
    for i in range(NUM_BINS):
        angle = i * 2 * math.pi / NUM_BINS
        # max_dist = 5 + 3 * math.sin(angle)
        max_dist = 20 + 10 * math.sin(angle)  # allow up to 30 km
        max_dist2_scaled = int((max_dist ** 2) * SCALE)
        lookup_table.append(PubValFxp(max_dist2_scaled))

    user_lat = PrivValFxp(lat_priv)
    user_lon = PrivValFxp(lon_priv)
    ref_lat = PubValFxp(reference_lat)
    ref_lon = PubValFxp(reference_lon)

    user_x, user_y = spherical_to_plane(user_lat, user_lon, ref_lat, ref_lon)

    dx = user_x
    dy = user_y

    dist2 = dx * dx + dy * dy
    azimuth = atan2_approx(dy, dx)

    INV_BUCKET_WIDTH = PubValFxp(NUM_BINS / (2 * math.pi))
    bucket_est = azimuth * INV_BUCKET_WIDTH

    # circuit safe one hot
    bucket = [0] * NUM_BINS
    for i in range(NUM_BINS):
        bucket[i] = (bucket_est - i).abs() < PubValFxp(0.5)  # crude bucketing

    # one-hot select max radius from public lookup
    max_allowed_sq = PubValFxp(0)
    for i in range(NUM_BINS):
        max_allowed_sq += lookup_table[i] * bucket[i]

    (dist2 <= max_allowed_sq).assert_eq(1)

    print("[ZKP] Location verified within allowed sector")
    snark.prove()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZKP: Prove you are inside a public angular sector")
    parser.add_argument("--user-lat", type=float, required=True)
    parser.add_argument("--user-lon", type=float, required=True)
    parser.add_argument("--center-lat", type=float, required=True)
    parser.add_argument("--center-lon", type=float, required=True)
    args = parser.parse_args()

    prove_location(args.user_lat, args.user_lon, args.center_lat, args.center_lon)

