# core/registry.py
import os
import sys
import glob
import importlib.util
import inspect
from typing import Callable, Any, Dict, List, Optional

# Definicja typu dla metody prognozowania
# Musi przyjmować pd.Series i zwracać pd.Series
ForecastFunc = Callable[[Any, int], Any]


class ForecastMethod:
    def __init__(self, key: str, name: str, category: str, func: ForecastFunc, description: str = ""):
        self.key = key
        self.name = name
        self.category = category
        self.func = func
        self.description = description


class MethodRegistry:
    def __init__(self, methods_dir: str):
        self._methods: Dict[str, ForecastMethod] = {}
        self.methods_dir = methods_dir

    def register(self, method: ForecastMethod):
        self._methods[method.key] = method

    def get_by_key(self, key: str) -> Optional[ForecastMethod]:
        return self._methods.get(key)

    def all_methods(self) -> List[ForecastMethod]:
        return list(self._methods.values())

    def load_methods(self):
        """Dynamicznie ładuje pliki .py z folderu methods/"""
        self._methods.clear()

        # Zabezpieczenie: sprawdź czy folder istnieje
        if not os.path.exists(self.methods_dir):
            os.makedirs(self.methods_dir)
            print(f"[Core] Utworzono folder metod: {self.methods_dir}")

        search_path = os.path.join(self.methods_dir, "*.py")
        files = glob.glob(search_path)

        print(f"[Core] Znaleziono plików metod: {len(files)}")

        for path in sorted(files):
            fname = os.path.basename(path)
            if fname.startswith("_"):
                continue

            # Unikalna nazwa modułu
            mod_name = f"methods.{os.path.splitext(fname)[0]}"

            try:
                # Dynamiczny import
                spec = importlib.util.spec_from_file_location(mod_name, path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)

                    if hasattr(module, "get_forecast_method"):
                        spec_dict = module.get_forecast_method()
                        # Walidacja i rejestracja
                        method = ForecastMethod(
                            key=str(spec_dict["key"]),
                            name=str(spec_dict["name"]),
                            category=str(spec_dict["category"]),
                            func=spec_dict["forecast"],
                            description=spec_dict.get("description", "")
                        )
                        self.register(method)
                        print(f"[Core] Załadowano metodę: {method.name}")
            except Exception as e:
                print(f"[Core] Błąd ładowania {fname}: {e}")