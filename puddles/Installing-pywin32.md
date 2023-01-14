# win32api Issues

The package has issues when access through a multiprocess thread. Within the main thread the library resolved successfully, however when executed within a process it didn't exist.

+ It was in the path
+ It was installed within the `env`
+ I had copied varias packages to the root of the app


https://stackoverflow.com/questions/58612306/how-to-fix-importerror-dll-load-failed-while-importing-win32api

The solution was to run the post install, **as admin** to ensure the packages installed in the `system32`

    .\env\Scripts\pywin32_postinstall.py -install



Bad:

    (env) C:\Users\jay\Documents\projects\multprocessing\puddles>py ..\env\Scripts\pywin32_postinstall.py -install
    Parsed arguments are: Namespace(destination='C:\\Users\\jay\\Documents\\projects\\multprocessing\\env\\Lib\\site-packages', install=True, quiet=False, remove=False, silent=False, wait=None)
    Copied pythoncom38.dll to C:\Users\jay\Documents\projects\multprocessing\env\pythoncom38.dll
    Copied pywintypes38.dll to C:\Users\jay\Documents\projects\multprocessing\env\pywintypes38.dll
    You do not have the permissions to install COM objects.
    The sample COM objects were not registered.
    -> Software\Python\PythonCore\3.8\Help[None]=None
    -> Software\Python\PythonCore\3.8\Help\Pythonwin Reference[None]='C:\\Users\\jay\\Documents\\projects\\multprocessing\\env\\Lib\\site-packages\\PyWin32.chm'
    Registered help file
    Pythonwin has been registered in context menu
    Shortcut for Pythonwin created
    Shortcut to documentation created
    The pywin32 extensions were successfully installed.


Good:


    (env) C:\Users\jay\Documents\projects\multprocessing>python .\env\Scripts\pywin32_postinstall.py -install
    Parsed arguments are: Namespace(destination='C:\\Users\\jay\\Documents\\projects\\multprocessing\\env\\Lib\\site-packages', install=True, quiet=False, remove=False, silent=False, wait=None)
    Copied pythoncom38.dll to C:\Windows\system32\pythoncom38.dll
    Copied pywintypes38.dll to C:\Windows\system32\pywintypes38.dll
    Registered: Python.Interpreter
    Registered: Python.Dictionary
    Registered: Python
    -> Software\Python\PythonCore\3.8\Help[None]=None
    -> Software\Python\PythonCore\3.8\Help\Pythonwin Reference[None]='C:\\Users\\jay\\Documents\\projects\\multprocessing\\env\\Lib\\site-packages\\PyWin32.chm'
    Registered help file
    Pythonwin has been registered in context menu
    Shortcut for Pythonwin created
    Shortcut to documentation created
    The pywin32 extensions were successfully installed.


seen in the second printout, the `pythoncom38` and `pywintypes38` are installed:

    Copied pythoncom38.dll to C:\Windows\system32\pythoncom38.dll
    Copied pywintypes38.dll to C:\Windows\system32\pywintypes38.dll


Future solution:

+ really deprecate python 3.8
