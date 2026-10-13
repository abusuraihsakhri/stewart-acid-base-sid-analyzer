"""Numerical regression tests for the Stewart–Figge calculator."""
import csv
import json
import math
import pytest
from stewart_sid import calculate_metrics, process_batch, main, INPUT_FIELDS

NORMAL = dict(sodium=140, potassium=4, ionized_calcium=1.2,
              ionized_magnesium=0.8, chloride=104, lactate=1.5,
              ph=7.4, pco2=40, albumin=40, phosphate=1.2)


def test_reference_calculation():
    result = calculate_metrics(**NORMAL)
    assert result["sida_mEq_L"] == pytest.approx(42.5)
    assert result["bicarbonate_mmol_L"] == pytest.approx(24.023, abs=0.001)
    assert result["albumin_charge_mEq_L"] == pytest.approx(11.168)
    assert result["phosphate_charge_mEq_L"] == pytest.approx(2.181, abs=0.001)
    assert result["side_mEq_L"] == pytest.approx(37.372, abs=0.001)
    assert result["sig_mEq_L"] == pytest.approx(5.128, abs=0.001)


def test_charge_and_lactate_sensitivity():
    normal = calculate_metrics(**NORMAL)
    lower_cl = calculate_metrics(**{**NORMAL, "chloride": 100})
    higher_lactate = calculate_metrics(**{**NORMAL, "lactate": 5.5})
    higher_calcium = calculate_metrics(**{**NORMAL, "ionized_calcium": 2.2})
    assert lower_cl["sida_mEq_L"] - normal["sida_mEq_L"] == pytest.approx(4)
    assert higher_lactate["sida_mEq_L"] - normal["sida_mEq_L"] == pytest.approx(-4)
    assert higher_calcium["sida_mEq_L"] - normal["sida_mEq_L"] == pytest.approx(2)


@pytest.mark.parametrize("change", [
    {"sodium": ""}, {"sodium": "x"}, {"sodium": float("nan")},
    {"chloride": float("inf")}, {"ph": 5.0}, {"ph": 9},
    {"pco2": 0}, {"albumin": -1}, {"ionized_magnesium": -0.2},
])
def test_invalid_input_rejected(change):
    with pytest.raises(ValueError):
        calculate_metrics(**{**NORMAL, **change})


def test_missing_inputs_are_not_silently_substituted():
    with pytest.raises(TypeError):
        calculate_metrics(sodium=140)


def test_batch_header_validation(tmp_path):
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    src.write_text("sodium,chloride\n140,104\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required"):
        process_batch(src, dst)
    assert not dst.exists()


def test_batch_fail_before_output(tmp_path):
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    with src.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=INPUT_FIELDS)
        writer.writeheader()
        writer.writerow(NORMAL)
        writer.writerow({**NORMAL, "pco2": "NaN"})
    with pytest.raises(ValueError, match="row 3"):
        process_batch(src, dst)
    assert not dst.exists()


def test_batch_and_csv_formula_safety(tmp_path):
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    with src.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["case_id", *INPUT_FIELDS])
        writer.writeheader()
        writer.writerow({"case_id": "=2+2", **NORMAL})
    assert process_batch(src, dst) == 1
    with dst.open(newline="") as stream:
        row = next(csv.DictReader(stream))
    assert row["case_id"] == "'=2+2"
    assert float(row["sig_mEq_L"]) == pytest.approx(5.128, abs=0.001)


def test_cli_calculation(capsys):
    arguments = ["single"]
    for field, value in NORMAL.items():
        arguments += ["--" + field.replace("_", "-"), str(value)]
    assert main(arguments) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["sida_mEq_L"] == 42.5


def test_cli_invalid_input_exits():
    with pytest.raises(SystemExit):
        main(["single", "--sodium", "140"])
