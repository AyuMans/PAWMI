import subprocess


# Applications PAWMI is allowed to launch
ALLOWED_APPS = {
    "firefox": ["firefox"],
    "terminal": ["qterminal"],
    "calculator": ["mate-calc"],
}

APP_ALIASES = {
    "browser": "firefox",
    "web browser": "firefox",
    "internet browser": "firefox",

    "command line": "terminal",
    "command prompt": "terminal",
    "shell": "terminal",

    "calc": "calculator",
}

def open_application(application):
    application = application.lower().strip()
    application = APP_ALIASES.get(application, application)
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
        