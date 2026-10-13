#!/usr/bin/env python3
"""Stewart–Figge acid–base calculations.

All strong ion concentrations are supplied in mmol/L, including ionized
Ca2+ and Mg2+ (converted to mEq/L by multiplying by their charge).
Albumin is in g/L, phosphate in mmol/L, PaCO2 in mmHg.
This is an educational/research calculator, not a treatment algorithm.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

INPUT_FIELDS = (
    "sodium", "potassium", "ionized_calcium", "ionized_magnesium",
    "chloride", "lactate", "ph", "pco2", "albumin", "phosphate",
)
OUTPUT_FIELDS = (
    "sida_mEq_L", "side_mEq_L", "sig_mEq_L",
    "bicarbonate_mmol_L", "albumin_charge_mEq_L", "phosphate_charge_mEq_L",
)


def calculate_metrics(*, sodium, potassium, ionized_calcium, ionized_magnesium,
                      chloride, lactate, ph, pco2, albumin, phosphate):
    """Compute SIDa, SIDe and SIG using the Stewart–Figge approximation.

    SIDa = Na + K + 2*iCa + 2*iMg - Cl - lactate
    HCO3 = 0.0301 * PaCO2 * 10**(pH - 6.1)
    SIDe = HCO3 + albumin*(0.123*pH - 0.631)
                 + phosphate*(0.309*pH - 0.469)
    SIG = SIDa - SIDe.

    Albumin g/L, phosphate and ions mmol/L, PaCO2 mmHg.
    Values are calculation results, not diagnostic thresholds.
    """
    raw = dict(sodium=sodium, potassium=potassium, ionized_calcium=ionized_calcium,
               ionized_magnesium=ionized_magnesium, chloride=chloride, lactate=lactate,
               ph=ph, pco2=pco2, albumin=albumin, phosphate=phosphate)
    vals = {}
    for name, value in raw.items():
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{name} must be a finite number") from exc
        if not math.isfinite(number):
            raise ValueError(f"{name} must be a finite number")
        vals[name] = number
    if not 6.0 <= vals["ph"] <= 8.5:
        raise ValueError("ph must be between 6.0 and 8.5")
    if vals["pco2"] <= 0:
        raise ValueError("pco2 must be positive (mmHg)")
    for name in INPUT_FIELDS:
        if name not in ("ph", "pco2") and vals[name] < 0:
            raise ValueError(f"{name} must be non-negative")

    sida = (vals["sodium"] + vals["potassium"]
            + 2 * vals["ionized_calcium"] + 2 * vals["ionized_magnesium"]
            - vals["chloride"] - vals["lactate"])
    bicarbonate = 0.0301 * vals["pco2"] * 10 ** (vals["ph"] - 6.1)
    alb_charge = vals["albumin"] * (0.123 * vals["ph"] - 0.631)
    pi_charge = vals["phosphate"] * (0.309 * vals["ph"] - 0.469)
    side = bicarbonate + alb_charge + pi_charge
    sig = sida - side
    return {
        "sida_mEq_L": round(sida, 3),
        "side_mEq_L": round(side, 3),
        "sig_mEq_L": round(sig, 3),
        "bicarbonate_mmol_L": round(bicarbonate, 3),
        "albumin_charge_mEq_L": round(alb_charge, 3),
        "phosphate_charge_mEq_L": round(pi_charge, 3),
        "method": "Stewart-Figge (Henderson-Hasselbalch bicarbonate estimate)",
        "note": "SIG reflects unmeasured net strong-ion charge within this approximation; interpret with clinical context.",
    }


def process_batch(input_csv, output_csv):
    """Process complete, header-matched CSV records; reject incomplete rows."""
    source = Path(input_csv)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    target = Path(output_csv)
    if not target.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        if not headers:
            raise ValueError("Input CSV has no headers")
        if len(headers) != len(set(headers)):
            raise ValueError("Input CSV has duplicate headers")
        if any(not h or h.lstrip().startswith(("=", "+", "-", "@")) for h in headers):
            raise ValueError("Input CSV has unsafe or empty headers")
        missing = [field for field in INPUT_FIELDS if field not in headers]
        if missing:
            raise ValueError("Missing required CSV columns: " + ", ".join(missing))
        if any(field in headers for field in OUTPUT_FIELDS):
            raise ValueError("Input CSV contains reserved result column names")
        result_rows = []
        for row_num, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"Extra columns in CSV row {row_num}")
            try:
                computed = calculate_metrics(**{k: row[k] for k in INPUT_FIELDS})
            except ValueError as exc:
                raise ValueError(f"Invalid input in CSV row {row_num}: {exc}") from exc
            result_rows.append({**row, **{k: computed[k] for k in OUTPUT_FIELDS}})

    # Neutralize CSV formula injection in text supplied by external datasets.
    def safe_cell(v):
        return "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else v

    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[*headers, *OUTPUT_FIELDS])
        writer.writeheader()
        for row in result_rows:
            writer.writerow({k: safe_cell(v) for k, v in row.items()})
    return len(result_rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Stewart–Figge SIDa, SIDe and SIG calculator")
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser("single", help="Calculate one complete specimen")
    for name in INPUT_FIELDS:
        single.add_argument("--" + name.replace("_", "-"), type=float, required=True)
    batch = commands.add_parser("batch", help="Read specimens from CSV")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    try:
        if args.command == "single":
            inputs = {k: getattr(args, k) for k in INPUT_FIELDS}
            print(json.dumps(calculate_metrics(**inputs), indent=2))
        else:
            count = process_batch(args.input, args.output)
            print(f"Processed {count} records -> {args.output}")
    except (ValueError, FileNotFoundError, PermissionError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
