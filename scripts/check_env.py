import sys, os, platform
print("version   =", sys.version)
print("executable=", sys.executable)
print("venv      =", sys.prefix != sys.base_prefix)
print("docker    =", os.path.exists("/.dockerenv"))
print("wsl       =", "microsoft" in platform.release().lower())
