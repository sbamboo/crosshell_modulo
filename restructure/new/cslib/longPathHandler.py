'''
CSlib: Windows long path handler
'''

from cslib.externalLibs.conUtils import IsWindows

# Non windows default function
def lph_isAllowed(pathstr=str) -> bool:
    return True

if IsWindows() == True:
    def _legacy_longPathEnabled() -> bool:
        import sys
        import ctypes
        # Get the full path to the Python executable
        python_exe = sys.executable
        # Call the GetLongPathName function to get the long path version of the executable
        long_path = ctypes.create_unicode_buffer(512)
        result = ctypes.windll.kernel32.GetLongPathNameW(python_exe, long_path, len(long_path))
        if result == 0:
            # Error: GetLongPathName failed
            return False
        # Check if the long path is longer than the original path
        if len(long_path.value) > len(python_exe):
            # Long path support is enabled
            return True
        else:
            # Long path support is not enabled
            return False
    def _longPathEnabled() -> bool:
        import winreg
        try:
            # Check if the 'LongPathsEnabled' key exists in the Registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\FileSystem') as key:
                try:
                    value, _ = winreg.QueryValueEx(key, 'LongPathsEnabled')
                    return value == 1  # Long path support is enabled
                except FileNotFoundError:
                    return False  # Long path support key not found, so it's not enabled
                except Exception:
                    return False  # Handle other errors by returning False
        except Exception:
            return False  # Handle any other exceptions by returning False
    
    def lph_isAllowed(pathstr=str,legacy=False) -> bool:
        # Check enabled
        enabled = False
        if legacy == True:
            enabled = _legacy_longPathEnabled()
        else:
            enabled = _longPathEnabled()
        # Check allowence
        if enabled == True:
            return len(pathstr) <= 32767 # Maximum allowed path length
        else:
            return len(pathstr) <= 260 # Maximum allowed path length in Windows