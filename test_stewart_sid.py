import pytest
from stewart_sid import calculate_metrics, process_batch, main


def test_stewart_sid_single():
    res = calculate_metrics(v1=12.0, v2=4.0)
    assert "score" in res
    assert "classification" in res
    assert res["score"] > 0


def test_stewart_sid_batch(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Patient,v1,v2\nPat_001,15.0,3.0\nPat_002,5.0,1.0\n", encoding="utf-8")

    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "Pat_001" in content
    assert "score" in content


def test_calculate_metrics_empty():
    res = calculate_metrics()
    assert res["score"] == 1.0
    assert res["classification"] == "Low / Standard"


def test_calculate_metrics_single_value():
    res = calculate_metrics(v1=30.0)
    assert res["score"] == 30.0
    assert res["classification"] == "High / Severe"


def test_calculate_metrics_moderate():
    res = calculate_metrics(v1=15.0, v2=5.0)
    assert res["classification"] == "Moderate / Intermediate"


def test_calculate_metrics_ignores_none():
    res = calculate_metrics(v1=10.0, v2=None)
    assert res["inputs_evaluated"] == 1


def test_process_batch_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_batch(str(tmp_path / "nonexistent.csv"), str(tmp_path / "out.csv"))


def test_process_batch_no_headers(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no headers"):
        process_batch(str(csv_in), str(csv_out))


def test_main_single_cli():
    exit_code = main(["single", "--v1", "15.0"])
    # main() returns None (no explicit return) on success; exit code is via sys.exit
    # Since we don't call sys.exit on success, it returns None


def test_main_batch_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["batch", "-i", str(tmp_path / "nope.csv")])
    assert exc_info.value.code == 1
