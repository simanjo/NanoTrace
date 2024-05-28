# NanoTrace

Tool to display squiggle plots of Oxforrd Nanopore bulk files plus some additional information about the distribution of the raw signal in a channel. Nanotrace was developed as part of research to detect and quantify small molecules using nanopores [Quint, I. et al. Ready-to-use nanopore platform for label-free small molecule quantification: Ethanolamine as first example](https://doi.org/10.1016/j.nano.2023.102724)

# Installation

The easiest way is to use the respective binaries ([Windows v1.0.1](https://github.com/simanjo/NanoTrace/releases/download/v1.0.1/nanotrace.exe), Linux  (tbd)).
Due to the end of support for Windows 8.1 only Windows 10 and later are supported (and the binary will most likely not run on older windows versions (due to the need to include the [universal crt](https://devblogs.microsoft.com/cppblog/introducing-the-universal-crt/)).

For manual usage from source follow these steps which require a working python 3 installation (3.8, 3.9 and 3.10 are supported):
```
# clone the repository
# for git version older than git 2.13 you might need to use --recursive instead of --recurse-submodules
git clone --recurse-submodules https://github.com/simanjo/NanoTrace.git
cd NanoTrace
# use pip to install the requirements (in a seperate virtual environment)
python3 -m venv env
pip3 install -r requirements.txt
# run the app
python3 nanotrace.py
```
To build your own binaries from source follow these steps (for details on the arguments see the [pyinstaller documentation](https://pyinstaller.org/en/stable/usage.html#options)):
```
# clone the repository
git clone --recurse-submodules https://github.com/simanjo/NanoTrace.git
cd NanoTrace
# use pip to install the requirements (in a seperate virtual environment)
python3 -m venv env
pip3 install -r dev_requirements.txt
# use pyinstaller to build a binary (assuming the virtual environment is placed in .\env)
pyinstaller --windowed --onefile  --add-data ".\env\Lib\site-packages\vbz_h5py_plugin\lib\vbz_hdf_plugin.dll:vbz_h5py_plugin\lib\" nanotrace.py
```

# Usage instructions

NanoTrace consists of 3 components; an overview window, showing general information about the currently loaded file, a plot window, showing squiggle plots of selected channels or kernel density estimations for the whole run (to visualize the distribution of the raw signal) and a settings window. For more details also see the [supplementary files](https://ars.els-cdn.com/content/image/1-s2.0-S1549963423000758-mmc1.docx) accompanying the publication.
