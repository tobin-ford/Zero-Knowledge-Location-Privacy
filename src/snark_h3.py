import argparse
from pysnark.runtime import PrivVal, PubVal, snark
from h3.api.basic_int import great_circle_distance

def main():
    parser = argparse.ArgumentParser(description="ZKP: Prove your location is within a distance threshold")
    parser.add_argument("--user-lat", type=float, required=True, help="User latitude")
    parser.add_argument("--user-lon", type=float, required=True, help="User longitude")
    parser.add_argument("--origin-lat", type=float, required=True, help="Origin latitude")
    parser.add_argument("--origin-lon", type=float, required=True, help="Origin longitude")
    parser.add_argument("--limit", type=int, required=True, help="Max distance allowed (km, public)")

    args = parser.parse_args()

    # Compute true distance outside the SNARK
    dist_km = great_circle_distance((args.user_lat, args.user_lon), (args.origin_lat, args.origin_lon))

    # Inject values
    calc_dist = PrivVal(int(dist_km))
    max_dist = PubVal(args.limit)

    # Assert within range
    max_dist.assert_ge(calc_dist)

    print(f"[ZKP] Proved distance {dist_km:.2f} km is within {args.limit} km.")

if __name__ == "__main__":
    main()