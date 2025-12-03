import os
import importlib.util

THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir))  # plugin root
SCRIPT_PATH = os.path.abspath(os.path.join(REPO_ROOT, '..', 'scripts', 'ILS_LLZ_single_frequency.py'))


def run_ils_llz_single_frequency():
    """
    Carga dinámicamente el script original del repositorio y ejecuta su entrypoint si existe.
    Devuelve un conteo/indicador simple para confirmar ejecución.
    """
    if not os.path.exists(SCRIPT_PATH):
        raise FileNotFoundError(f'No se encontró el script: {SCRIPT_PATH}')

    spec = importlib.util.spec_from_file_location('ils_llz_single', SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    count = 0
    for candidate in ('main', 'run', 'execute'):
        fn = getattr(mod, candidate, None)
        if callable(fn):
            fn()
            count += 1
            break
    return count
