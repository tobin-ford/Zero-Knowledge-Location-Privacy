# Zero-Knowledge Location Proof (ZKLP)

Zero-Knowledge Location Proofs enable geospatial verification without exposing exact coordiantes.


### Zero Knowledge Proofs

- 

## Methodology
ZKLP builds on a Discrete Global Grid System (DGGS) to partition space into higherarcial hexagonal cells. Instead of proving your location in cartesian (latitude, longitude) or polar coordinates ($\Theta, \Phi$), the protocol verifies membership in a public cell index provided by the DGGS.

See: "[H3: Uber’s Hexagonal Hierarchical Spatial Index](https://www.uber.com/blog/h3/)" for an example of discrete spatial indexing.


#### Protocol
1. $\Theta, \Phi$ -> 3D cartesian to determine closeset icoshaderon face.
2. Compute angular distance, $r=\arccos(1 - \frac{d^2}{2})$
3. Project to 2D, rotate by a face-specific reference axis to get polar coords $(r, \sigma)$
4. convert planar cartesian $(x, y)$ -> integer cell coordiantes $(I, J, K)$
5. prove in SNARK that private location $(\Theta, \Phi)$ maps to public $(I, J, K)$ 


#### NOTES:

sNARKS: https://crypto.stackexchange.com/questions/19884/what-are-snarks

| ✅ What a ZK-SNARK Adds (vs. a plain client-side boolean) | Without SNARKs (just sending boolean) | With SNARKs (zero-knowledge proof) |
|-----------------------------------------------------------|----------------------------------------|--------------------------------------|
| **Trust**                                                 | Trust-based. The server must trust the client is honest. | Trustless. The client proves it knows a valid location satisfying the constraint. |
| **Security**                                              | A malicious client can send True even if far away. | A cheating client can’t forge the proof without breaking crypto. |
| **Privacy**                                               | Revealing True/False leaks some info, but okay. | The server learns nothing about the actual location. |
| **Implementation**                                        | Easy to implement. | Requires ZKP circuit + trusted setup (in many schemes). |


❗ A SNARK isn't about checking a boolean. It's about proving the boolean was computed honestly over a private input.

use cases
A user wants to prove they are within a specific country or airspace (or not in a restricted one), without revealing where exactly.

    Client claims: “I’m inside Germany”

    Server wants assurance that this is true — without learning which hex, city, or coordinates the user is in.

This might be used in:

    Regulatory compliance (e.g. GDPR data access only from Europe)

    Geofencing for services (digital media, voting, etc.)

    Verifying location anonymously (e.g. protests, secure communication)


🧅 Cryptographic Guarantees of SNARK

Wrapping the location predicate in a SNARK gives you:

    ✅ Correctness (it really is within the circle)

    🛡️ Zero-knowledge (you learn nothing about the actual location)

    🚫 Unforgeability (malicious users can't lie and pretend they're nearby)

🤔 So why not just trust the client?

Because in any situation where:

    There’s an incentive to lie

    The server doesn’t trust the client

    But shouldn’t learn private data (like location)…

…you want to offload computation to the client, and then prove the result is valid cryptographically, not based on trust.


### DEPS
pysnark: ``pip3 install git+https://github.com/meilof/pysnark``  
uber h3: ``pip install h3``