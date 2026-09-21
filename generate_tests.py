from prompts import build_basic_prompt
from llm_client import call_llm

from pathlib import Path
import os
import subprocess
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import sys

def run_pytest():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "generated_tests",
            "--junitxml=results/pytest.xml"
        ],
        capture_output=True,
        text=True
    )

    return result

def run_coverage():
    subprocess.run([sys.executable, "-m", "coverage", "erase"])

    subprocess.run(
        [sys.executable, "-m", "coverage", "run", "-m", "pytest", "generated_tests"],
        capture_output=True,
        text=True
    )

    subprocess.run(
        [sys.executable, "-m", "coverage", "json", "-o", "results/coverage.json"],
        capture_output=True,
        text=True
    )

def run_mutation_testing():
    result = subprocess.run(
        [sys.executable, "-m", "mutmut", "run"],
        capture_output=True,
        text=True
    )
    return result

def read_pytest_stats():
    root = ET.parse("results/pytest.xml").getroot()

    if root.tag == "testsuite":
        testsuite = root
    else:
        testsuite = root.find("testsuite")

    tests = int(testsuite.attrib["tests"])
    failures = int(testsuite.attrib["failures"])
    errors = int(testsuite.attrib["errors"])
    skipped = int(testsuite.attrib["skipped"])
    time = float(testsuite.attrib["time"])

    passed = tests - failures - errors - skipped

    return {
        "tests": tests,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "time": time
    }

def read_coverage_stats():
    with open("results/coverage.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    totals = data["totals"]

    return {
        "line_percent": totals["percent_covered"],
        "covered_lines": totals["covered_lines"],
        "missing_lines": totals["missing_lines"],
        "num_statements": totals["num_statements"],
        "covered_branches": totals["covered_branches"],
        "missing_branches": totals["missing_branches"],
        "num_branches": totals["num_branches"]
    }

def read_mutation_results():
    result = subprocess.run(
        [sys.executable, "-m", "mutmut", "results"],
        capture_output=True,
        text=True
    )

    return result.stdout

def save_summary(pytest_stats, coverage_stats):
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pytest": pytest_stats,
        "coverage": coverage_stats
    }

    with open("results/summary.json", "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

def read_source_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        source_code = file.read()
    return source_code

def save_generated_tests(test_code, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(test_code)

def clean_llm_response(text):
    cleaned_text = text.strip()
    if cleaned_text.startswith("```python") and cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[9:-3].strip()
    return cleaned_text

def path_to_module_name(path):
    path = Path(path)

    without_suffix = path.with_suffix("")
    module_name = str(without_suffix).replace(os.sep, '.')
    return module_name

def main():
    source_path = "src/tasks.py"

    source_code = read_source_code(source_path)

    prompt = build_basic_prompt(source_code, module_name=path_to_module_name(source_path))

    generated_tests = call_llm(prompt)

    generated_tests = clean_llm_response(generated_tests)

    print(generated_tests)

    output_path = "generated_tests/test_generated.py"
    os.makedirs("generated_tests", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    save_generated_tests(generated_tests, output_path)

    pytest_result = run_pytest()
    print(pytest_result.stdout)
    print(pytest_result.stderr)

    pytest_stats = read_pytest_stats()

    if pytest_result.returncode != 0:
        save_summary(pytest_stats, {})
        print("Pytest failed")
        print(pytest_result.stdout)
        print(pytest_result.stderr)
        return
    
    run_coverage()
    coverage_stats = read_coverage_stats()

    # run_mutation_testing()
    
    # mutation_stats = read_mutation_results()
    
    save_summary(pytest_stats, coverage_stats)

if __name__ == "__main__":
    main()
