import subprocess


# Applications PAWMI is allowed to launch
ALLOWED_APPS = {
    "firefox": ["firefox"],
    "terminal": ["qterminal"],
    "calculator": ["galculator"],
}


def open_application(application):
    application = application.lower().strip()

    if application not in ALLOWED_APPS:
        return {
            "success": False,
            "message": f"I am not allowed to open '{application}'."
        }
        
    try:
        subprocess.Popen(
            ALLOWED_APPS[application],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )
        return {
            "success": True,
            "message": f"Opened {application}"
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"{application} is not installed or cannot be found."
        }
    except Exception as error:
        return {
            "success": False,
            "message": f"Could not open {application}: {error}"
        }
        