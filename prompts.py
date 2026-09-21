def build_basic_prompt(source_code, module_name="src.tasks"):
    prompt = f"""
    You are a python test generator. 
    Write unit tests using pytest for the following python source code.
    Test normal cases, edge cases, and error cases, if they exist.
    Don't include any explanations, only return executable python test code.
    Import from this module the functions and use them in the tests.:
    {module_name}
    SOURCE CODE:
    {source_code}
    """
    return prompt