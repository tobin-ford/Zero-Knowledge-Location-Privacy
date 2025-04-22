import subprocess
import time

def test_snark_h3():
    import subprocess, time

    base_lat = 40.37
    base_lon = -105.2
    total_time = 0.0

    for i in range(50):
        user_lat = base_lat + 0.0001 * i
        user_lon = base_lon + 0.0001 * i

        args = [
            "python", "snark_h3.py",
            "--user-lat", f"{user_lat:.6f}",
            "--user-lon", f"{user_lon:.6f}",
            "--origin-lat", "40.36",
            "--origin-lon", "-105.21",
            "--limit", "50"
        ]

        print(f"\n[H3 Run {i+1}] User location: ({user_lat:.6f}, {user_lon:.6f})")

        start = time.perf_counter()
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = e.stderr
        end = time.perf_counter()

        elapsed = end - start
        total_time += elapsed

        print(f"Time: {elapsed:.3f}s\n{output.strip()}")

    print(f"\n[Summary] H3 ZKP: Total time = {total_time:.2f}s | Avg = {total_time/50:.2f}s")

def test_haversine_distance():
    import subprocess, time

    base_lat = 40.37
    base_lon = -105.2
    total_time = 0.0

    for i in range(50):
        lat2 = base_lat + 0.0001 * i
        lon2 = base_lon + 0.0001 * i

        args = [
            "python", "snark_haversine.py",
            "--lat1", f"{base_lat:.6f}",
            "--lon1", f"{base_lon:.6f}",
            "--lat2", f"{lat2:.6f}",
            "--lon2", f"{lon2:.6f}",
            "--limit", "50"
        ]

        print(f"\n[Haversine Run {i+1}] Target: ({lat2:.6f}, {lon2:.6f})")

        start = time.perf_counter()
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = e.stderr
        end = time.perf_counter()

        elapsed = end - start
        total_time += elapsed

        print(f"Time: {elapsed:.3f}s\n{output.strip()}")

    print(f"\n[Summary] Haversine ZKP: Total time = {total_time:.2f}s | Avg = {total_time/50:.2f}s")


def test_snark_paper():
    import subprocess, time
    import h3

    base_lat = 40.37
    base_lon = -105.2
    res = 8
    total_time = 0.0

    for i in range(50):
        lat = base_lat + 0.0001 * i
        lon = base_lon + 0.0001 * i

        hex_id = h3.latlng_to_cell(lat, lon, res)
        i, j = h3.cell_to_local_ij(h3.latlng_to_cell(base_lat, base_lon, res), hex_id)
        
        # i, j = ijk[0], ijk[1]
        k = -i - j

        args = [
            "python", "snark_paper.py",
            "--theta", f"{lat:.6f}",
            "--phi", f"{lon:.6f}",
            "--res", str(res),
            "--I", str(i),
            "--J", str(j),
            "--K", str(k)
        ]

        print(f"\n[ZKLP Run {i+1}] Location: ({lat:.6f}, {lon:.6f}) | IJK: {i, j, k}")

        start = time.perf_counter()
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = e.stderr
        end = time.perf_counter()

        elapsed = end - start
        total_time += elapsed

        print(f"Time: {elapsed:.3f}s\n{output.strip()}")

    print(f"\n[Summary] ZKLP Hex ZKP: Total time = {total_time:.2f}s | Avg = {total_time/50:.2f}s")

def test_angle_lookup_proof():

    center_lat = 40.37
    center_lon = -105.21
    total_time = 0.0
    num_passed = 0

    print(f"[Testing ZKP angle lookup against center: ({center_lat}, {center_lon})]")

    for i in range(50):
        lat = center_lat + 0.0001 * i
        lon = center_lon + 0.0001 * i

        args = [
            "python", "snark_irregular.py",  # using lut
            "--user-lat", f"{lat:.6f}",
            "--user-lon", f"{lon:.6f}",
            "--center-lat", f"{center_lat:.6f}",
            "--center-lon", f"{center_lon:.6f}",
        ]

        print(f"\n[Run {i+1}] User location: ({lat:.6f}, {lon:.6f})")

        start = time.perf_counter()
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            output = result.stdout
            num_passed += 1
        except subprocess.CalledProcessError as e:
            output = e.stderr
        end = time.perf_counter()

        elapsed = end - start
        total_time += elapsed

        print(f"Time: {elapsed:.3f}s\n{output.strip()}")

    print(f"\n[Summary] ZKLP Angle Lookup ZKP:")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Avg time per run: {total_time / 50:.3f} seconds")
    print(f"  Passed: {num_passed} / 50")


if __name__ == "__main__":
    test_snark_h3()
    test_haversine_distance()
    test_snark_paper()
    test_angle_lookup_proof()
