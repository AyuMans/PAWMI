import platform
import os


def get_system_info():
    return {
        "operating_system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_cores": os.cpu_count()
    }