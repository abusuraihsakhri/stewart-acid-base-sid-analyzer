"""Headless browser-interaction regression using Node.js and a minimal DOM stub."""
import json
import re
import shutil
import subprocess
from pathlib import Path
import pytest


def test_browser_calculation_and_stale_result_reset():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js unavailable")
    html = (Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.DOTALL)
    assert len(scripts) == 1
    harness = r"""
const assert = require("node:assert/strict");
const ids = ["calculator","error","download","status","detail","reset",
             "sida","side","sig","bicarbonate","albumin_charge","phosphate_charge",
             "sodium","potassium","ionized_calcium","ionized_magnesium",
             "chloride","lactate","ph","pco2","albumin","phosphate"];
const defaults = {
  sodium:"140", potassium:"4", ionized_calcium:"1.2", ionized_magnesium:"0.8",
  chloride:"104", lactate:"1.5", ph:"7.4", pco2:"40", albumin:"40", phosphate:"1.2"
};
const elements = {};
for (const id of ids) {
  elements[id] = {
    value: defaults[id] ?? "",
    textContent: "", hidden: true, disabled: true, handlers: {},
    addEventListener: function (event, cb) { this.handlers[event] = cb; },
    reportValidity: () => true,
    reset: () => {}
  };
}
global.document = { getElementById: id => elements[id] };
"""
    verify = r"""
elements.calculator.handlers.submit({preventDefault() {}});
assert.equal(elements.sida.textContent, "42.500");
assert.equal(elements.side.textContent, "37.372");
assert.equal(elements.sig.textContent, "5.128");
assert.equal(elements.download.disabled, false);
elements.lactate.value = "5.5";
elements.calculator.handlers.input();
assert.equal(elements.download.disabled, true);
assert.equal(elements.sig.textContent, "—");
elements.calculator.handlers.submit({preventDefault() {}});
assert.equal(elements.sig.textContent, "1.128");
elements.pco2.value = "0";
elements.calculator.handlers.submit({preventDefault() {}});
assert.equal(elements.download.disabled, true);
assert.match(elements.error.textContent, /PaCO/);
"""
    code = harness + "\n" + scripts[0] + "\n" + verify
    run = subprocess.run([node, "-"], input=code, capture_output=True,
                         text=True, timeout=20, check=False)
    assert run.returncode == 0, run.stderr
