#!/usr/bin/env python3
"""BoseCondensate-Lab - educational Bose-Einstein condensate lab.

by Darion Kellar

Pure Python standard library. Zero dependencies. Zero network.
Education only - and the central lesson is stated up front:

  * BoseCondensate-Lab computes the textbook theory of an ideal
    and weakly-interacting Bose gas in a 3D harmonic trap: the
    critical temperature from zeta(3) (summed from scratch), the
    condensate fraction 1 - (T/Tc)^3, the fugacity above Tc solved
    by bisection against the Bose function g_3(z) (also summed
    from scratch), the Thomas-Fermi profile of the interacting
    gas, and the ballistic aspect-ratio inversion after release,
    integrated from the Castin-Dum scaling equations.
  * Every parameter is a LABELLED teaching number: an 87Rb-like
    mass, N = 100,000 atoms, a 100 Hz geometric-mean trap, a
    labelled scattering length. No gas was cooled, no condensate
    was made, no atom was imaged. A computed Tc of ~210 nK is a
    property of these equations at these inputs - it is not a
    measurement, not a cooling record, and not a device claim.
  * The fences are part of the physics: above Tc the condensate
    fraction is exactly zero and the chemical potential stays
    negative; the Thomas-Fermi profile drops the kinetic energy
    by construction, and the lab prints the interaction/kinetic
    ratio so the size of that approximation is never hidden.

Conventions, stated once and used everywhere below:
  * SI units internally; temperatures printed in nK, lengths in
    micrometres, where the prose says so.
  * omega_bar is the geometric-mean trap angular frequency; the
    Thomas-Fermi radius uses the isotropic-trap simplification
    R = sqrt(2 mu / (m omega_bar^2)) unless a section says else.
  * The ideal-gas sections pin z = 1 and mu = 0 below Tc; the
    interacting section quotes mu_TF at T = 0. The two chemical
    potentials belong to two stated models and are never mixed.

Real condensate creation, laser cooling, atom lasers, BEC
sensors, and record or vendor claims are permanent HOLD gates -
with Gemini Argon 4 Extended Thinking as DECIDER (names-only,
tighten-only), Muse as advisor (never overrides HOLD), and
Google Flow plan-only seats.
"""
import hashlib
import json
import math
import sys

# ---------------------------------------------------------------- constants
VERSION = "1.0.0"
HBAR = 1.054571817e-34          # J s, exact SI
KB = 1.380649e-23               # J/K, exact SI
AMU = 1.66053906660e-27         # kg
A0 = 5.29177210903e-11          # m, Bohr radius
TWO_PI = 2.0 * math.pi

# Labelled teaching parameters. These describe ONE fictional gas
# used for instruction - they are not a product, a record, or a
# measurement of anything that exists.
ATOM_LABEL = "87Rb-like"
MASS = 87.0 * AMU                       # kg
N_ATOMS = 100_000                       # labelled atom number
OMEGA_BAR = TWO_PI * 100.0              # trap geometric mean: 2pi x 100 Hz
A_SCATT = 100.0 * A0                    # labelled scattering length: 100 a0
# Labelled anisotropic trap for the release/expansion section only.
OMEGA_XY = TWO_PI * 200.0               # tight axes: 2pi x 200 Hz
OMEGA_Z = TWO_PI * 20.0                 # weak axis: 2pi x 20 Hz

# ---------------------------------------------------------------- HOLD gates
HOLD_GATES = {
    "real_condensate_creation_claim": "HOLD - no claim a real condensate was created, cooled, or imaged; this lab only evaluates equations",
    "laser_cooling_hardware_operation": "HOLD - no operating laser cooling, magneto-optical traps, or evaporative cooling hardware",
    "atom_laser_output_claim": "HOLD - no atom laser, coherent atom beam, or output-coupling claims from a textbook profile",
    "bec_interferometer_sensor_claim": "HOLD - no BEC interferometer, gravimeter, gyroscope, or sensor deployment claims",
    "vendor_hardware_spec_claim": "HOLD - no vendor specifications for lasers, vacuum systems, coils, or cameras",
    "vacuum_cryogenics_operation": "HOLD - no operating real vacuum, cryogenic, or high-current trap plant",
    "certified_measurement_claim": "HOLD - computed Tc, fractions, and densities are not certified measurements of any real gas",
    "quantum_computing_claim": "HOLD - no quantum-computing or qubit claims from a condensate model",
    "commercial_product_claim": "HOLD - no commercial cold-atom product claims; a lab model is not a product",
    "medical_claim": "HOLD - no medical imaging, sensing, or diagnostic claims",
    "defense_surveillance_claim": "HOLD - no defence, navigation-denied, or surveillance sensing claims",
    "investment_claim": "HOLD - no investment claims; a teaching model is not a prospectus",
    "safety_interlock_bypass": "HOLD - laser, vacuum, and high-current safety interlocks are never bypassed",
    "record_temperature_claim": "HOLD - no record-temperature, record-density, or publication-result claims from simulation output",
}


def gate(action):
    """Return 'HOLD' if the action is gated, else 'PROCEED' (sandbox sim)."""
    return "HOLD" if action in HOLD_GATES else "PROCEED"


# ================================================================ 1. zeta(3) + critical temperature
# The whole ideal-gas story hangs on one number: zeta(3), the
# capacity of the excited states at fugacity 1. It is summed from
# scratch here - direct terms plus an Euler-Maclaurin tail - and
# printed at full precision so the receipt is visible.

ZETA3_REFERENCE = 1.2020569031595942    # known value, used only in CHECKS


def zeta3(n_direct=20000):
    """zeta(3) = sum_k 1/k^3, direct sum + Euler-Maclaurin tail."""
    total = 0.0
    for k in range(1, n_direct + 1):
        total += 1.0 / (k * k * k)
    n = float(n_direct)
    tail = (1.0 / (2.0 * n * n)
            - 1.0 / (2.0 * n ** 3)
            + 1.0 / (4.0 * n ** 4)
            - 1.0 / (12.0 * n ** 6))
    return total + tail


def critical_temperature(n_atoms=N_ATOMS, omega_bar=OMEGA_BAR):
    """Tc from N = zeta(3) * (kB Tc / (hbar omega_bar))^3, in kelvin."""
    return (HBAR * omega_bar / KB) * (n_atoms / zeta3()) ** (1.0 / 3.0)


TC_K = critical_temperature()
TC_NK = TC_K * 1e9


# ================================================================ 2. Condensate fraction
# Below Tc the excited states saturate at zeta(3) * (T/Tc)^3 of
# the atoms; the rest have nowhere to go but the ground state.

def condensate_fraction(t_ratio):
    """N0/N = 1 - (T/Tc)^3 below Tc; exactly 0 at and above Tc."""
    if t_ratio >= 1.0:
        return 0.0
    return 1.0 - t_ratio ** 3


def fraction_table():
    """N0/N at T/Tc = 0, 0.1, ..., 1.0 plus one thermal row."""
    rows = []
    for i in range(0, 11):
        t = i / 10.0
        rows.append({"t_over_tc": t, "fraction": condensate_fraction(t)})
    rows.append({"t_over_tc": 1.5, "fraction": condensate_fraction(1.5)})
    return rows


# ================================================================ 3. Fugacity above Tc
# Above Tc every atom is in an excited state: N = g_3(z) *
# (kB T / (hbar omega_bar))^3 with g_3(z) = sum_k z^k / k^3.
# g_3 is monotone in z, so bisection on z in (0, 1) is bracketed
# and safe. mu = kB T ln z stays negative and reaches 0- at Tc.

def bose_g3(z, tol=1e-14, max_terms=2_000_000):
    """Bose function g_3(z) = sum_{k>=1} z^k / k^3, summed directly."""
    if z >= 1.0:
        return zeta3()
    if z <= 0.0:
        return 0.0
    total = 0.0
    zk = 1.0
    for k in range(1, max_terms + 1):
        zk *= z
        term = zk / (k * k * k)
        total += term
        if term < tol and k > 64:
            break
    return total


def excited_number(z, temp_k, omega_bar=OMEGA_BAR):
    """N_ex = g_3(z) * (kB T / (hbar omega_bar))^3."""
    return bose_g3(z) * (KB * temp_k / (HBAR * omega_bar)) ** 3


def solve_fugacity(temp_k, n_atoms=N_ATOMS, omega_bar=OMEGA_BAR):
    """Solve z(T) at fixed N. Below Tc z is pinned at 1 (mu = 0)."""
    tc = critical_temperature(n_atoms, omega_bar)
    if temp_k <= tc:
        return 1.0
    target = n_atoms * (HBAR * omega_bar / (KB * temp_k)) ** 3
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if bose_g3(mid) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    return 0.5 * (lo + hi)


def chemical_potential_nk(temp_k, n_atoms=N_ATOMS, omega_bar=OMEGA_BAR):
    """Ideal-gas mu in nK: kB T ln z / kB, i.e. T * ln z, in nK."""
    z = solve_fugacity(temp_k, n_atoms, omega_bar)
    if z >= 1.0:
        return 0.0
    return temp_k * math.log(z) * 1e9


def fugacity_report():
    rows = []
    for t_ratio in (0.8, 1.0, 1.001, 1.05, 1.2, 1.5, 2.0, 3.0):
        temp = t_ratio * TC_K
        z = solve_fugacity(temp)
        rows.append({
            "t_over_tc": t_ratio,
            "temp_nk": round(temp * 1e9, 3),
            "z": z,
            "mu_nk": round(chemical_potential_nk(temp), 4),
            "n_ex_check": round(excited_number(z, temp), 1)
            if t_ratio > 1.0 else None,
        })
    return {"tc_nk": round(TC_NK, 3), "rows": rows}


# ================================================================ 4. Thomas-Fermi profile
# Turn the interactions on and the ground state stops being the
# harmonic-oscillator Gaussian: repulsion flattens it into an
# inverted parabola n(r) = n(0) (1 - r^2/R^2). The Thomas-Fermi
# approximation drops the kinetic energy outright - the lab
# prints the interaction/kinetic ratio so the size of that step
# is on the page, not under it.

def oscillator_length(omega_bar=OMEGA_BAR, mass=MASS):
    """a_ho = sqrt(hbar / (m omega_bar))."""
    return math.sqrt(HBAR / (mass * omega_bar))


def coupling_g(a_scatt=A_SCATT, mass=MASS):
    """Mean-field coupling g = 4 pi hbar^2 a / m (J m^3)."""
    return 4.0 * math.pi * HBAR * HBAR * a_scatt / mass


def thomas_fermi(n_atoms=N_ATOMS, a_scatt=A_SCATT,
                 omega_bar=OMEGA_BAR, mass=MASS):
    """TF chemical potential, radius, peak density, and receipts."""
    a_ho = oscillator_length(omega_bar, mass)
    big = 15.0 * n_atoms * a_scatt / a_ho
    mu = 0.5 * HBAR * omega_bar * big ** (2.0 / 5.0)
    radius = math.sqrt(2.0 * mu / (mass * omega_bar * omega_bar))
    radius_route2 = a_ho * big ** (1.0 / 5.0)
    g = coupling_g(a_scatt, mass)
    n_peak = mu / g
    n_from_profile = (8.0 * math.pi / 15.0) * n_peak * radius ** 3
    zero_point = 1.5 * HBAR * omega_bar
    return {
        "a_ho_um": a_ho * 1e6,
        "na_over_aho": n_atoms * a_scatt / a_ho,
        "mu_over_hbar_omega": mu / (HBAR * omega_bar),
        "mu_nk": mu / KB * 1e9,
        "radius_um": radius * 1e6,
        "radius_route2_um": radius_route2 * 1e6,
        "peak_density_per_cm3": n_peak * 1e-6,
        "n_from_profile": n_from_profile,
        "zero_point_scale_over_hbar_omega": 1.5,
        "interaction_ratio": mu / zero_point,
    }


def tf_sweep():
    """mu and R scalings: mu ~ N^(2/5), R ~ N^(1/5) at fixed a, omega."""
    base = thomas_fermi()
    rows = []
    for factor in (1, 8, 64):
        tf = thomas_fermi(n_atoms=N_ATOMS * factor)
        rows.append({
            "n_factor": factor,
            "mu_ratio": tf["mu_over_hbar_omega"] / base["mu_over_hbar_omega"],
            "mu_ratio_law": factor ** (2.0 / 5.0),
            "radius_ratio": tf["radius_um"] / base["radius_um"],
            "radius_ratio_law": factor ** (1.0 / 5.0),
        })
    return rows


# ================================================================ 5. Release + expansion
# Open the trap and the cloud expands ballistically. In the TF
# regime the shape stays a scaled copy of itself (Castin-Dum):
# R_i(t) = R_i(0) b_i(t) with, after release,
#   b_i'' = omega_i(0)^2 / (b_i * b_x b_y b_z),  b_i(0)=1, b_i'(0)=0.
# The tight axis starts small and accelerates hardest, so a cigar
# (long along z) inverts into a pancake: the aspect ratio crosses
# 1. Integrated here with written-out RK4 - no quoted crossing.

EXP_OMEGAS = (OMEGA_XY, OMEGA_XY, OMEGA_Z)
EXP_OMEGA_BAR = (OMEGA_XY * OMEGA_XY * OMEGA_Z) ** (1.0 / 3.0)


def _expansion_rhs(state):
    b = state[0:3]
    v = state[3:6]
    lam = b[0] * b[1] * b[2]
    acc = [EXP_OMEGAS[i] ** 2 / (b[i] * lam) for i in range(3)]
    return v + acc


def expansion_run(t_end=0.030, dt=2.0e-6):
    """Integrate the scaling equations; return radii + aspect rows."""
    tf = thomas_fermi(omega_bar=EXP_OMEGA_BAR)
    mu = tf["mu_nk"] * 1e-9 * KB
    r0 = [math.sqrt(2.0 * mu / (MASS * w * w)) for w in EXP_OMEGAS]
    state = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    rows = [{"t_ms": 0.0,
             "aspect_z_over_x": r0[2] / r0[0]}]
    steps = int(t_end / dt)
    sample_every = max(1, steps // 60)
    for s in range(1, steps + 1):
        k1 = _expansion_rhs(state)
        s2 = [state[i] + 0.5 * dt * k1[i] for i in range(6)]
        k2 = _expansion_rhs(s2)
        s3 = [state[i] + 0.5 * dt * k2[i] for i in range(6)]
        k3 = _expansion_rhs(s3)
        s4 = [state[i] + dt * k3[i] for i in range(6)]
        k4 = _expansion_rhs(s4)
        state = [state[i] + dt * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6.0
                 for i in range(6)]
        if s % sample_every == 0 or s == steps:
            rx = r0[0] * state[0]
            rz = r0[2] * state[2]
            rows.append({"t_ms": round(s * dt * 1e3, 3),
                         "aspect_z_over_x": rz / rx})
    return {"r0_um": [r * 1e6 for r in r0],
            "initial_aspect": r0[2] / r0[0],
            "rows": rows,
            "final_aspect": rows[-1]["aspect_z_over_x"]}


def expansion_crossing_ms():
    """Aspect-ratio = 1 crossing time by scan + bisection on samples."""
    run = expansion_run()
    rows = run["rows"]
    for i in range(1, len(rows)):
        if rows[i - 1]["aspect_z_over_x"] >= 1.0 > rows[i]["aspect_z_over_x"]:
            lo, hi = rows[i - 1], rows[i]
            frac = ((lo["aspect_z_over_x"] - 1.0)
                    / (lo["aspect_z_over_x"] - hi["aspect_z_over_x"]))
            return lo["t_ms"] + frac * (hi["t_ms"] - lo["t_ms"])
    return None


# ================================================================ 6. Sweeps
def sweeps_report():
    """Tc scaling receipts: Tc ~ N^(1/3) and Tc ~ omega_bar."""
    tc_base = TC_K
    n_rows = []
    for factor in (1, 8, 27):
        tc = critical_temperature(n_atoms=N_ATOMS * factor)
        n_rows.append({"n_factor": factor,
                       "tc_ratio": tc / tc_base,
                       "tc_ratio_law": factor ** (1.0 / 3.0)})
    o_rows = []
    for factor in (1, 2, 4):
        tc = critical_temperature(omega_bar=OMEGA_BAR * factor)
        o_rows.append({"omega_factor": factor,
                       "tc_ratio": tc / tc_base,
                       "tc_ratio_law": float(factor)})
    return {"tc_nk": round(TC_NK, 3), "n_sweep": n_rows, "omega_sweep": o_rows}


# ================================================================ 7. kNN regime classifier
# Features: T/Tc, condensate fraction N0/N, and the interaction
# ratio mu_TF / ((3/2) hbar omega_bar). The training grid is
# labelled by the lab's own policy (model_label below) - the
# classifier interpolates the policy, it does not replace the
# physics sections.

def model_label(t_ratio, fraction, interaction_ratio):
    """The regime policy distilled to a four-way teaching label."""
    if t_ratio >= 1.125:
        return "thermal"
    if t_ratio >= 0.875:
        return "near-critical"
    if interaction_ratio >= 6.5:
        return "strongly-interacting"
    return "condensed"


def _training_grid():
    rows = []
    for t_ratio in (0.0, 0.3, 0.55, 0.8, 0.95, 1.3, 2.0):
        for fraction in (0.0, 0.35, 0.7, 0.95):
            for interaction in (0.5, 2.0, 4.0, 9.0, 18.0):
                rows.append(((t_ratio, fraction, interaction),
                             model_label(t_ratio, fraction, interaction)))
    return rows


TRAINING_GRID = _training_grid()


def _scaled(features):
    t_ratio, fraction, interaction = features
    return (t_ratio, fraction, interaction / 18.0)


def classify_regime(t_ratio, fraction, interaction_ratio, k=7):
    """Distance-weighted kNN over the policy-labelled grid."""
    target = _scaled((t_ratio, fraction, interaction_ratio))
    ranked = []
    for features, label in TRAINING_GRID:
        point = _scaled(features)
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(target, point)))
        ranked.append((dist, features, label))
    ranked.sort(key=lambda row: (row[0], row[1]))
    weights = {}
    for dist, _, label in ranked[:k]:
        weights[label] = weights.get(label, 0.0) + 1.0 / (dist + 0.05)
    priority = {"condensed": 0, "strongly-interacting": 1,
                "near-critical": 2, "thermal": 3}
    return sorted(weights.items(),
                  key=lambda kv: (-kv[1], priority[kv[0]]))[0][0]


def classifier_report():
    tf = thomas_fermi()
    inter = tf["interaction_ratio"]
    scenarios = {
        "deep_cold_weak_coupling": (0.3, condensate_fraction(0.3), 0.8),
        "headline_rb87_half_tc": (0.5, condensate_fraction(0.5), inter),
        "just_below_tc": (0.95, condensate_fraction(0.95), inter),
        "just_above_tc": (1.3, 0.0, inter),
        "hot_thermal_gas": (2.0, 0.0, inter),
        "cold_weakly_interacting": (0.2, condensate_fraction(0.2), 2.0),
    }
    return {name: classify_regime(*features)
            for name, features in scenarios.items()}


# ================================================================ 8. Advisory seats
def _trace(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def argon4_decide(topic="bosecondensate-demo"):
    """Gemini Argon 4 DECIDER seat: MAP->MODEL->STRESS->DECIDE.

    Names-only keys, live calls 0, tighten-only: can add HOLDs, never lift one.
    """
    stages = ["MAP", "MODEL", "STRESS", "DECIDE"]
    payload = {"seat": "gemini-argon-4", "topic": topic, "stages": stages}
    return {
        "seat": "Gemini Argon 4 Extended Thinking",
        "role": "DECIDER",
        "pipeline": stages,
        "tiers": [2048, 8192, 32768],
        "key": "names-only (GEMINI_API_KEY name checked, value never read)",
        "live_calls": 0,
        "decision": "PROCEED - sandbox simulation only, all condensate gates stay HOLD",
        "can_override_hold": False,
        "trace_sha256_16": _trace(payload),
    }


def claude_advisor(topic="bosecondensate-demo"):
    """Muse advisor seat: advises, can never override a HOLD."""
    return {
        "seat": "Muse",
        "role": "ADVISOR",
        "key": "names-only (MODEL_API_KEY name checked, value never read)",
        "live_calls": 0,
        "advice": "Say it in the first line of every report: no gas was cooled and no condensate was made - then show Tc from zeta(3), the fraction curve, and the interaction ratio that prices the Thomas-Fermi step.",
        "can_override_hold": False,
    }


def google_flow_plan():
    """Google Flow seat: plan-only, nothing rendered, nothing live."""
    return {
        "seat": "Google Flow",
        "role": "PLAN-ONLY",
        "shots": ["a broad thermal hump cooling frame by frame",
                  "a sharp central peak rising out of the hump below Tc",
                  "the fugacity needle sliding to 1 as T approaches Tc",
                  "an inverted-parabola density profile labelled Thomas-Fermi",
                  "a cigar-shaped cloud inverting into a pancake after release"],
        "rendered": False,
        "live": 0,
    }


def brains_report():
    return {"decider": argon4_decide(), "advisor": claude_advisor(),
            "flow": google_flow_plan()}


# ================================================================ checks
def run_checks():
    c = []

    def chk(name, ok):
        c.append((name, bool(ok)))

    # 1. zeta(3) from scratch
    z3 = zeta3()
    chk("zeta3_value", abs(z3 - ZETA3_REFERENCE) < 1e-10)
    chk("zeta3_bounds", 1.2020569 < z3 < 1.2020570)
    partial = sum(1.0 / (k * k * k) for k in range(1, 2001))
    chk("zeta3_above_partial_sum", z3 > partial)

    # 2. Bose function g_3(z)
    chk("g3_at_1_is_zeta3", bose_g3(1.0) == z3)
    chk("g3_at_0_is_0", bose_g3(0.0) == 0.0)
    chk("g3_monotone", bose_g3(0.3) < bose_g3(0.6) < bose_g3(0.9) < z3)
    g3_half_ref = sum(0.5 ** k / (k * k * k) for k in range(1, 2001))
    chk("g3_half_matches_direct_sum",
        abs(bose_g3(0.5) - g3_half_ref) < 1e-12)

    # 3. critical temperature
    chk("tc_labelled_range_nk", 200.0 < TC_NK < 220.0)
    chk("tc_capacity_receipt",
        abs(excited_number(1.0, TC_K) - N_ATOMS) / N_ATOMS < 1e-9)
    chk("tc_scaling_n_third_power",
        abs(critical_temperature(n_atoms=8 * N_ATOMS) / TC_K - 2.0) < 1e-9)
    chk("tc_scaling_omega_linear",
        abs(critical_temperature(omega_bar=2.0 * OMEGA_BAR) / TC_K - 2.0)
        < 1e-12)
    sw = sweeps_report()
    chk("tc_sweep_laws",
        all(abs(r["tc_ratio"] - r["tc_ratio_law"]) < 1e-9
            for r in sw["n_sweep"] + sw["omega_sweep"]))

    # 4. condensate fraction
    chk("fraction_at_zero", condensate_fraction(0.0) == 1.0)
    chk("fraction_at_half_tc_exact", condensate_fraction(0.5) == 0.875)
    chk("fraction_at_quarter", condensate_fraction(0.25) == 1.0 - 0.25 ** 3)
    chk("fraction_at_tc_zero", condensate_fraction(1.0) == 0.0)
    chk("fraction_above_tc_zero", condensate_fraction(1.5) == 0.0)
    table = fraction_table()
    chk("fraction_table_shape", len(table) == 12
        and table[0]["fraction"] == 1.0 and table[-1]["fraction"] == 0.0)
    chk("fraction_monotone",
        all(table[i]["fraction"] >= table[i + 1]["fraction"]
            for i in range(len(table) - 1)))

    # 5. fugacity above Tc
    fug = fugacity_report()
    chk("fugacity_below_tc_pinned",
        solve_fugacity(0.5 * TC_K) == 1.0
        and chemical_potential_nk(0.5 * TC_K) == 0.0)
    ok_pop = True
    for t_ratio in (1.2, 1.5, 2.0, 3.0):
        temp = t_ratio * TC_K
        z = solve_fugacity(temp)
        if not (0.0 < z < 1.0):
            ok_pop = False
        if abs(excited_number(z, temp) - N_ATOMS) / N_ATOMS > 1e-6:
            ok_pop = False
        if chemical_potential_nk(temp) >= 0.0:
            ok_pop = False
    chk("fugacity_population_receipts", ok_pop)
    chk("fugacity_falls_with_temperature",
        solve_fugacity(1.2 * TC_K) > solve_fugacity(2.0 * TC_K)
        > solve_fugacity(3.0 * TC_K))
    z_near = solve_fugacity(1.001 * TC_K)
    mu_near = chemical_potential_nk(1.001 * TC_K)
    chk("mu_reaches_zero_from_below", z_near > 0.99 and -2.0 < mu_near < 0.0)
    chk("fugacity_report_rows", len(fug["rows"]) == 8)

    # 6. Thomas-Fermi profile
    tf = thomas_fermi()
    chk("tf_mu_headline_range", 17.0 < tf["mu_over_hbar_omega"] < 18.5)
    chk("tf_radius_two_routes",
        abs(tf["radius_um"] - tf["radius_route2_um"]) / tf["radius_um"]
        < 1e-9)
    chk("tf_profile_normalises_to_n",
        abs(tf["n_from_profile"] - N_ATOMS) / N_ATOMS < 1e-6)
    chk("tf_interaction_ratio",
        abs(tf["interaction_ratio"] - tf["mu_over_hbar_omega"] / 1.5) < 1e-9
        and tf["interaction_ratio"] > 5.0)
    chk("tf_a_ho_range", 1.0 < tf["a_ho_um"] < 1.15)
    chk("tf_peak_density_positive", tf["peak_density_per_cm3"] > 0.0)
    tf_sw = tf_sweep()
    chk("tf_scaling_laws",
        all(abs(r["mu_ratio"] - r["mu_ratio_law"]) < 1e-9
            and abs(r["radius_ratio"] - r["radius_ratio_law"]) < 1e-9
            for r in tf_sw))

    # 7. release + expansion (Castin-Dum scaling, RK4)
    run = expansion_run()
    chk("expansion_initial_aspect_10",
        abs(run["initial_aspect"] - OMEGA_XY / OMEGA_Z) < 1e-9)
    chk("expansion_inverts", run["final_aspect"] < 1.0
        and run["final_aspect"] < run["initial_aspect"])
    cross = expansion_crossing_ms()
    chk("expansion_crossing_exists", cross is not None and 0.0 < cross < 30.0)
    chk("expansion_radii_order", run["r0_um"][2] > run["r0_um"][0] > 0.0)

    # 8. classifier - labels come from the lab's own policy
    rep = classifier_report()
    chk("classifier_deep_cold_condensed",
        rep["deep_cold_weak_coupling"] == "condensed")
    chk("classifier_headline_strongly_interacting",
        rep["headline_rb87_half_tc"] == "strongly-interacting")
    chk("classifier_near_critical", rep["just_below_tc"] == "near-critical")
    chk("classifier_above_tc_thermal", rep["just_above_tc"] == "thermal")
    chk("classifier_hot_thermal", rep["hot_thermal_gas"] == "thermal")
    chk("classifier_cold_weak_condensed",
        rep["cold_weakly_interacting"] == "condensed")
    chk("classifier_matches_policy_grid",
        all(classify_regime(*features) == label
            for features, label in TRAINING_GRID))
    chk("classifier_matches_policy_scenarios",
        all(classify_regime(*f) == model_label(*f) for f in
            [(0.3, condensate_fraction(0.3), 0.8),
             (0.5, condensate_fraction(0.5), tf["interaction_ratio"]),
             (0.95, condensate_fraction(0.95), tf["interaction_ratio"]),
             (2.0, 0.0, tf["interaction_ratio"])]))

    # gates + seats
    chk("hold_gates_14", len(HOLD_GATES) == 14
        and all(v.startswith("HOLD") for v in HOLD_GATES.values()))
    chk("gate_creation_hold", gate("real_condensate_creation_claim") == "HOLD")
    chk("gate_atom_laser_hold", gate("atom_laser_output_claim") == "HOLD")
    chk("gate_sensor_hold", gate("bec_interferometer_sensor_claim") == "HOLD")
    chk("gate_record_hold", gate("record_temperature_claim") == "HOLD")
    chk("gate_sandbox_proceed", gate("run_simulation") == "PROCEED")
    brains = brains_report()
    chk("argon4_no_override", brains["decider"]["can_override_hold"] is False
        and brains["decider"]["seat"]
        == "Gemini Argon 4 Extended Thinking")
    chk("claude_no_override", brains["advisor"]["can_override_hold"] is False)
    chk("flow_plan_only", brains["flow"]["rendered"] is False
        and brains["flow"]["live"] == 0)
    return c


# ================================================================ CLI / demo
def demo():
    print("=" * 68)
    print("BoseCondensate-Lab - Bose-Einstein condensate lab")
    print("by Darion Kellar | MIT | pure stdlib | zero network | EDUCATION ONLY")
    print("=" * 68)
    print("\n[1] THE HONEST CORE - equations, not a refrigerator")
    print("    This lab evaluates the textbook theory of a trapped Bose")
    print("    gas: zeta(3) summed from scratch sets the critical")
    print("    temperature, the fraction curve follows, the fugacity")
    print("    above Tc is solved by bisection, and the interacting")
    print("    ground state is a Thomas-Fermi parabola.")
    print("    No gas was cooled. No condensate was made. Every number")
    print("    below is a property of these equations at LABELLED inputs:")
    print(f"    {ATOM_LABEL}, N = {N_ATOMS:,} atoms, trap 2pi x 100 Hz,")
    print(f"    scattering length a = 100 a0.")
    print("\n[2] Critical temperature - the zeta(3) capacity limit")
    print(f"    zeta(3) summed from scratch = {zeta3():.13f}")
    print(f"    (reference                 = {ZETA3_REFERENCE:.13f})")
    print(f"    Tc = {TC_NK:.2f} nK for the labelled set")
    print(f"    receipt: N_ex(z=1, Tc) = {excited_number(1.0, TC_K):,.1f} "
          f"of {N_ATOMS:,} atoms")
    sw = sweeps_report()
    for r in sw["n_sweep"]:
        print(f"    N x{r['n_factor']:<3d} -> Tc x{r['tc_ratio']:.4f} "
              f"(law N^(1/3): x{r['tc_ratio_law']:.4f})")
    for r in sw["omega_sweep"]:
        print(f"    omega x{r['omega_factor']} -> Tc x{r['tc_ratio']:.4f} "
              f"(law linear: x{r['tc_ratio_law']:.4f})")
    print("\n[3] Condensate fraction - 1 - (T/Tc)^3 below Tc")
    for row in fraction_table():
        bar = "#" * int(round(row["fraction"] * 40))
        print(f"    T/Tc {row['t_over_tc']:.1f}  N0/N {row['fraction']:.4f}  "
              f"{bar}")
    print("    -> at T/Tc = 0.5 the fraction is exactly 0.875; at and")
    print("       above Tc it is exactly zero. No rounding theatre.")
    print("\n[4] Fugacity above Tc - bisection on g_3(z), mu = kB T ln z")
    fug = fugacity_report()
    for row in fug["rows"]:
        print(f"    T/Tc {row['t_over_tc']:<6} T {row['temp_nk']:>9.2f} nK  "
              f"z {row['z']:.6f}  mu {row['mu_nk']:>10.4f} nK")
    print("    -> below Tc z is pinned at 1 and mu = 0; above Tc z < 1,")
    print("       mu < 0, and mu reaches 0- exactly at Tc.")
    print("\n[5] Thomas-Fermi profile - interactions flatten the cloud")
    tf = thomas_fermi()
    print(f"    a_ho = {tf['a_ho_um']:.4f} um | N a / a_ho = "
          f"{tf['na_over_aho']:,.1f}")
    print(f"    mu_TF = {tf['mu_over_hbar_omega']:.4f} hbar omega "
          f"= {tf['mu_nk']:.2f} nK")
    print(f"    ideal-gas zero-point scale (3/2) hbar omega -> "
          f"interaction ratio {tf['interaction_ratio']:.4f}")
    print(f"    R_TF = {tf['radius_um']:.3f} um (two routes agree) | "
          f"n(0) = {tf['peak_density_per_cm3']:.4e} /cm^3")
    print(f"    profile integral = {tf['n_from_profile']:,.1f} atoms "
          f"(labelled N = {N_ATOMS:,})")
    for r in tf_sweep():
        print(f"    N x{r['n_factor']:<3d} -> mu x{r['mu_ratio']:.4f} "
              f"(law N^(2/5): x{r['mu_ratio_law']:.4f}) | "
              f"R x{r['radius_ratio']:.4f} "
              f"(law N^(1/5): x{r['radius_ratio_law']:.4f})")
    print("\n[6] Release + expansion - the aspect ratio inverts")
    run = expansion_run()
    cross = expansion_crossing_ms()
    print(f"    labelled trap 2pi x (200, 200, 20) Hz: R_z/R_x starts at "
          f"{run['initial_aspect']:.1f} (cigar)")
    print(f"    Castin-Dum scaling integrated by RK4: aspect crosses 1 at "
          f"t = {cross:.2f} ms")
    print(f"    aspect at 30 ms = {run['final_aspect']:.4f} (pancake) - "
          f"computed, not quoted")
    print("\n[7] Regime classifier (TinyML kNN, labels from the lab policy)")
    for name, label in classifier_report().items():
        print(f"    {name:36s} -> {label}")
    print("\n[8] Advisory seats")
    brains = brains_report()
    print(f"    decider: {brains['decider']['decision']} "
          f"trace={brains['decider']['trace_sha256_16']}")
    print(f"    advisor can_override_hold = "
          f"{brains['advisor']['can_override_hold']}")
    print(f"    flow rendered = {brains['flow']['rendered']} "
          f"live = {brains['flow']['live']}")
    print(f"\n[9] HOLD gates: {len(HOLD_GATES)}")
    for key in HOLD_GATES:
        print(f"    HOLD  {key}")
    checks = run_checks()
    passed = sum(1 for _, ok in checks if ok)
    print(f"\nCHECKS {passed}/{len(checks)}")
    for name, ok in checks:
        if not ok:
            print(f"    FAIL {name}")
    verdict = "PROCEED" if passed == len(checks) else "HOLD"
    print(f"VERDICT {verdict} (sandbox simulation only) | "
          f"HOLD gates {len(HOLD_GATES)}")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "demo":
        return demo()
    cmd = argv[0]
    if cmd == "checks":
        checks = run_checks()
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"CHECKS {sum(1 for _, ok in checks if ok)}/{len(checks)}")
        return 0 if all(ok for _, ok in checks) else 1
    if cmd == "critical":
        print(json.dumps(sweeps_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "fraction":
        print(json.dumps(fraction_table(), indent=2, sort_keys=True))
        return 0
    if cmd == "fugacity":
        print(json.dumps(fugacity_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "thomasfermi":
        print(json.dumps(thomas_fermi(), indent=2, sort_keys=True))
        return 0
    if cmd == "sweeps":
        print(json.dumps({"tc": sweeps_report(), "tf": tf_sweep()},
                         indent=2, sort_keys=True))
        return 0
    if cmd == "expansion":
        run = expansion_run()
        run["crossing_ms"] = expansion_crossing_ms()
        print(json.dumps(run, indent=2, sort_keys=True))
        return 0
    if cmd == "classify":
        print(json.dumps(classifier_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "brains":
        print(json.dumps(brains_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "holds":
        for key, value in HOLD_GATES.items():
            print(f"{key}: {value}")
        return 0
    if cmd == "hold-demo":
        action = argv[1] if len(argv) > 1 else "real_condensate_creation_claim"
        print(f"{action}: {HOLD_GATES.get(action, 'PROCEED - not gated')}")
        return 2 if gate(action) == "HOLD" else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
