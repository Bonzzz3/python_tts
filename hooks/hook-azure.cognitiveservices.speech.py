from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# Include all dynamic libraries (DLLs, .so, .dylib)
binaries = collect_dynamic_libs("azure.cognitiveservices.speech")
datas = collect_data_files("azure.cognitiveservices.speech")
hiddenimports = []