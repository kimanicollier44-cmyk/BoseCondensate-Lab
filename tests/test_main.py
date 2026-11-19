"""Tests for BoseCondensate-Lab. Pure stdlib lab; pytest only."""
import math

import main


# --- zeta(3) + critical temperature -----------------------------------
def test_zeta3_value():
    assert abs(main.zeta3() - 1.2020569031595942) < 1e-10


def test_g3_at_one_is_zeta3():
    assert main.bose_g3(1.0) == main.zeta3()


def test_g3_half_direct_sum():
    ref = sum(0.5 ** k / (k * k * k) for k in range(1, 2001))
    assert abs(main.bose_g3(0.5) - ref) < 1e-12


def test_tc_labelled_range():
    assert 200.0 < main.TC_NK < 220.0


def test_tc_capacity_receipt():
    assert abs(main.excited_number(1.0, main.TC_K) - main.N_ATOMS) \
        / main.N_ATOMS < 1e-9


def test_tc_scaling_n():
    ratio = main.critical_temperature(n_atoms=8 * main.N_ATOMS) / main.TC_K
    assert abs(ratio - 2.0) < 1e-9


def test_tc_scaling_omega():
    ratio = main.critical_temperature(omega_bar=2.0 * main.OMEGA_BAR) \
        / main.TC_K
    assert abs(ratio - 2.0) < 1e-12


# --- condensate fraction ----------------------------------------------
def test_fraction_half_tc_exact():
    assert main.condensate_fraction(0.5) == 0.875


def test_fraction_endpoints():
    assert main.condensate_fraction(0.0) == 1.0
    assert main.condensate_fraction(1.0) == 0.0
    assert main.condensate_fraction(2.5) == 0.0


def test_fraction_table_monotone():
    table = main.fraction_table()
    assert len(table) == 12
    assert all(table[i]["fraction"] >= table[i + 1]["fraction"]
               for i in range(len(table) - 1))


# --- fugacity ----------------------------------------------------------
def test_fugacity_pinned_below_tc():
    assert main.solve_fugacity(0.5 * main.TC_K) == 1.0
    assert main.chemical_potential_nk(0.5 * main.TC_K) == 0.0


def test_fugacity_population_receipt():
    for t_ratio in (1.2, 1.5, 2.0, 3.0):
        temp = t_ratio * main.TC_K
        z = main.solve_fugacity(temp)
        assert 0.0 < z < 1.0
        assert abs(main.excited_number(z, temp) - main.N_ATOMS) \
            / main.N_ATOMS < 1e-6


def test_mu_negative_above_tc():
    for t_ratio in (1.05, 1.2, 2.0):
        assert main.chemical_potential_nk(t_ratio * main.TC_K) < 0.0


def test_mu_reaches_zero_from_below():
    z = main.solve_fugacity(1.001 * main.TC_K)
    mu = main.chemical_potential_nk(1.001 * main.TC_K)
    assert z > 0.99
    assert -2.0 < mu < 0.0


def test_fugacity_falls_with_temperature():
    assert main.solve_fugacity(1.2 * main.TC_K) \
        > main.solve_fugacity(2.0 * main.TC_K) \
        > main.solve_fugacity(3.0 * main.TC_K)


# --- Thomas-Fermi -------------------------------------------------------
def test_tf_headline_numbers():
    tf = main.thomas_fermi()
    assert 17.0 < tf["mu_over_hbar_omega"] < 18.5
    assert tf["interaction_ratio"] > 5.0
    assert 1.0 < tf["a_ho_um"] < 1.15


def test_tf_radius_two_routes():
    tf = main.thomas_fermi()
    assert abs(tf["radius_um"] - tf["radius_route2_um"]) \
        / tf["radius_um"] < 1e-9


def test_tf_profile_normalises():
    tf = main.thomas_fermi()
    assert abs(tf["n_from_profile"] - main.N_ATOMS) / main.N_ATOMS < 1e-6


def test_tf_scaling_laws():
    for row in main.tf_sweep():
        assert abs(row["mu_ratio"] - row["mu_ratio_law"]) < 1e-9
        assert abs(row["radius_ratio"] - row["radius_ratio_law"]) < 1e-9


# --- expansion -----------------------------------------------------------
def test_expansion_initial_aspect():
    run = main.expansion_run()
    assert abs(run["initial_aspect"] - 10.0) < 1e-9


def test_expansion_inverts():
    run = main.expansion_run()
    assert run["final_aspect"] < 1.0


def test_expansion_crossing():
    cross = main.expansion_crossing_ms()
    assert cross is not None and 0.0 < cross < 30.0


# --- classifier ----------------------------------------------------------
def test_classifier_scenarios():
    rep = main.classifier_report()
    assert rep["deep_cold_weak_coupling"] == "condensed"
    assert rep["headline_rb87_half_tc"] == "strongly-interacting"
    assert rep["just_below_tc"] == "near-critical"
    assert rep["just_above_tc"] == "thermal"
    assert rep["hot_thermal_gas"] == "thermal"
    assert rep["cold_weakly_interacting"] == "condensed"


def test_classifier_matches_policy_grid():
    for features, label in main.TRAINING_GRID:
        assert main.classify_regime(*features) == label


def test_policy_thresholds():
    assert main.model_label(1.2, 0.0, 1.0) == "thermal"
    assert main.model_label(0.9, 0.2, 1.0) == "near-critical"
    assert main.model_label(0.5, 0.875, 10.0) == "strongly-interacting"
    assert main.model_label(0.5, 0.875, 1.0) == "condensed"


# --- gates + seats --------------------------------------------------------
def test_hold_gates_14():
    assert len(main.HOLD_GATES) == 14
    assert all(v.startswith("HOLD") for v in main.HOLD_GATES.values())


def test_gate_outcomes():
    assert main.gate("real_condensate_creation_claim") == "HOLD"
    assert main.gate("atom_laser_output_claim") == "HOLD"
    assert main.gate("record_temperature_claim") == "HOLD"
    assert main.gate("run_simulation") == "PROCEED"


def test_seats_never_override():
    brains = main.brains_report()
    assert brains["decider"]["can_override_hold"] is False
    assert brains["decider"]["seat"] == "Gemini Argon 4 Extended Thinking"
    assert brains["advisor"]["can_override_hold"] is False
    assert brains["flow"]["rendered"] is False
    assert brains["flow"]["live"] == 0


def test_cli_hold_demo_exit_2():
    assert main.main(["hold-demo"]) == 2


def test_cli_checks_pass():
    assert main.main(["checks"]) == 0
