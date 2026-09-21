# Local LLM Test Generator

This is a small but complete Python project that generates unit tests with a locally running language model. It reads source code, creates a focused prompt, saves the generated pytest tests, runs them automatically, measures branch coverage, and exports the results as machine-readable files.

The project is intentionally simple. My goal was to understand the full workflow behind AI-assisted test generation instead of hiding it behind a framework.

## What It Does

1. Reads a Python source file.
2. Converts its file path into a valid Python module name.
3. Sends the source code and test instructions to a local Gemma model through the LM Studio API.
4. Cleans the model response and writes executable pytest code.
5. Runs the generated tests automatically.
6. Measures statement and branch coverage.
7. Saves pytest, coverage, and summary reports in the `results` directory.
8. Supports mutation testing with mutmut inside Docker.

## Why I Built It

I built this project to learn how local LLM integration, prompt construction, automated testing, subprocess execution, report parsing, coverage analysis, and containerization work together in one pipeline.

It is an MVP, but it covers the complete process from source code to measurable test results. It also keeps the model local, so the source code does not need to be sent to a cloud API.

## Project Structure

```text
test_generator/
|-- src/
|   |-- __init__.py
|   `-- tasks.py
|-- generated_tests/
|   `-- test_generated.py
|-- results/
|   |-- coverage.json
|   |-- pytest.xml
|   `-- summary.json
|-- generate_tests.py
|-- llm_client.py
|-- prompts.py
|-- pytest.ini
|-- .coveragerc
|-- setup.cfg
|-- requirements.txt
`-- Dockerfile
```

## Technologies

- Python
- pytest
- coverage.py
- mutmut
- LM Studio
- Gemma 3 4B
- Docker

## Run Locally

Start LM Studio, load the `google/gemma-3-4b` model, and enable the local API server on port `1234`.

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the complete pipeline from the project directory:

```powershell
python generate_tests.py
```

The generated test file is written to `generated_tests/test_generated.py`. The reports are written to the `results` directory.

The default model and API endpoint can be changed without editing the code:

```powershell
$env:LLM_MODEL = "another-model-id"
$env:LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
python generate_tests.py
```

## Run With Docker

LM Studio must be running on the host machine before the container starts.

Build the image:

```powershell
docker build -t local-llm-test-generator .
```

Run the pipeline and keep the generated files on the host machine:

```powershell
docker run --rm `
  -v "${PWD}/generated_tests:/app/generated_tests" `
  -v "${PWD}/results:/app/results" `
  local-llm-test-generator
```

Docker Desktop resolves `host.docker.internal` to the Windows host. The container uses this address to reach LM Studio.

To use another loaded model:

```powershell
docker run --rm `
  -e LLM_MODEL=another-model-id `
  -v "${PWD}/generated_tests:/app/generated_tests" `
  -v "${PWD}/results:/app/results" `
  local-llm-test-generator
```

To test your own code, place a file named `my_tasks.py` in the current directory and mount it over the example source file:

```powershell
docker run --rm `
  -v "${PWD}/my_tasks.py:/app/src/tasks.py:ro" `
  -v "${PWD}/generated_tests:/app/generated_tests" `
  -v "${PWD}/results:/app/results" `
  local-llm-test-generator
```

The `:ro` option makes the source file read-only inside the container. The generated tests and reports are still saved on the host machine.

### Use the Published Image

The image is also available on Docker Hub, so the project can be used without building it locally:

```powershell
docker pull leventekk1/local-llm-test-generator:latest
```

Run the downloaded image and keep the generated files on the host machine:

```powershell
docker run --rm `
  -v "${PWD}/my_tasks.py:/input/tasks.py:ro" `
  -v "${PWD}/generated_tests:/app/generated_tests" `
  -v "${PWD}/results:/app/results" `
  leventekk1/local-llm-test-generator:latest
```

## Mutation Testing

mutmut does not support native Windows execution. The Docker image uses Linux, so mutation testing can run without WSL.

Mutation testing is intentionally separate from the main generation pipeline. The generated tests and coverage report run automatically because they provide fast feedback after every generation. Mutation testing is slower, and surviving mutants can return a non-zero exit code even when the analysis completed correctly.

For this MVP, keeping it as an optional step makes the normal workflow faster and easier to understand:

1. `generate_tests.py` generates the tests, runs pytest, measures coverage, and saves the summary.
2. `mutmut run` performs the deeper mutation analysis when it is needed.
3. `mutmut results` displays the mutants that survived and shows where the test suite can be improved.

The mutation helper functions remain in the code as a starting point for a later version. A future version can run mutation testing automatically and export structured results, but it should remain optional instead of slowing down every test generation run.

First generate the tests, then run:

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  local-llm-test-generator python -m mutmut run
```

Display the mutation results:

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  local-llm-test-generator python -m mutmut results
```

To run only mutation testing with the published image, place `my_tasks.py` and the existing `generated_tests/test_generated.py` file in the current directory:

```powershell
docker run --rm `
  -v "${PWD}/my_tasks.py:/input/tasks.py:ro" `
  -v "${PWD}/generated_tests:/app/generated_tests:ro" `
  leventekk1/local-llm-test-generator:latest `
  sh -c "cp /input/tasks.py /app/src/tasks.py && python -m mutmut run --CI && python -m mutmut results"
```

This command uses the existing generated tests and does not call LM Studio. It does not replace the container's `/app` directory, so the mutation configuration included in the image remains available. The `--CI` option allows the command to continue when mutants survive, while fatal mutation testing errors still stop the process.

## Output

- `generated_tests/test_generated.py`: test code produced by the model
- `results/pytest.xml`: detailed pytest execution report
- `results/coverage.json`: statement and branch coverage data
- `results/summary.json`: compact summary for later processing or visualization
- `.mutmut-cache`: mutation testing results created by the optional Docker command

## Current Scope

The current version processes one Python source file and uses one local model. The next logical steps are multi-file support, automatic repair of failed generated tests, structured mutation statistics, and comparison between different models and prompts.
