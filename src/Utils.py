import subprocess
import winreg


def find_installed_apps_from_registry(reg_hive, reg_path):
    install_locations = {}
    try:
        with winreg.OpenKey(reg_hive, reg_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    with winreg.OpenKey(key, winreg.EnumKey(key, i)) as subkey:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        install_location, _ = winreg.QueryValueEx(
                            subkey, "InstallLocation"
                        )

                        if display_name and install_location:
                            install_locations.update(
                                {display_name.strip(): install_location}
                            )

                except FileNotFoundError:
                    continue
                except OSError:
                    continue
    except FileNotFoundError:
        pass

    return install_locations


def find_installed_exes_from_registry(reg_hive, reg_path, install_locations):
    apps = {}
    try:
        with winreg.OpenKey(reg_hive, reg_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    with winreg.OpenKey(key, winreg.EnumKey(key, i)) as subkey:
                        path_exe, _ = winreg.QueryValueEx(subkey, None)
                        path, _ = winreg.QueryValueEx(subkey, "Path")

                        for diplay_name, install_location in install_locations.items():
                            if path == install_location:
                                apps.update({diplay_name.strip(): path_exe})
                except FileNotFoundError:
                    continue
                except OSError:
                    continue
    except FileNotFoundError:
        pass

    return apps


def find_exes_from_installed_apps(install_locations):
    entries_to_remove = []
    for display_name, location in install_locations.items():
        if not location.endswith("\\"):
            location += "\\"

        command = f'dir "{location}*.exe" /b'

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True,
        )
        output, error = process.communicate()

        if output:
            exe_path = output.splitlines()[0]
            install_locations[display_name] = f"{location}{exe_path}"
        else:
            entries_to_remove.append(display_name)

    for entry in entries_to_remove:
        install_locations.pop(entry, None)


def get_full_list_installed_apps():
    apps = {}

    registry_paths = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            # r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        ),  # 32-bit (global)
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            # r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
        ),  # 64-bit (global)
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            # r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        ),  # 32-bit (usuario)
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            # r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
        ),  # 64-bit (usuario)
    ]

    apps = {}
    for hive, path in registry_paths:
        apps.update((find_installed_apps_from_registry(hive, path)))

    find_exes_from_installed_apps(apps)

    return apps


if __name__ == "__main__":
    installed_apps = get_full_list_installed_apps()
    input("\nPresiona Enter para salir...")
