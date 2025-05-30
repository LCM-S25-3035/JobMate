import importlib.util
import os
import sys

def call_function_from_file(filename: str, function_name: str, *args, **kwargs):
    """
    Dynamically find and import a Python file and call a function from it.

    Args:
        filename (str): The filename to search for (e.g., 'option1_1.py').
        function_name (str): The function name to invoke.
        *args, **kwargs: Parameters to pass into the function.

    Returns:
        Output of the invoked function.
    """
    # Search for file anywhere inside current project folder
    project_root = r"C:\Users\xnoor\OneDrive - Lambton College\Documents\GitHub\JobMate\src"

    found_path = None

    for root, _, files in os.walk(project_root):
        if filename in files:
            found_path = os.path.join(root, filename)
            break

    if not found_path:
        raise FileNotFoundError(f"{filename} not found anywhere in {project_root}")

    # Load and execute function from the found file
    module_name = os.path.splitext(os.path.basename(found_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, found_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, function_name):
        raise AttributeError(f"Function '{function_name}' not found in '{filename}'")

    func = getattr(module, function_name)
    return func(*args, **kwargs)

# Reference: 
# OpenAI 4o, 1st prompt: 
# why can't we just do like.. input is whatever file we want to call like option1_1.py, which will be the argument and then there's this argument for function that we want to call.. then we will retrun the function? Or is it unnecessary? coz we can call so many functions and so many py files

# OpenAI 4o, last prompt: 
# Getting error "ERROR] Resume parsing failed: C:\Users\xnoor\OneDrive - Lambton College\Documents\GitHub\JobMate\onboarding\option1_1.py not found"