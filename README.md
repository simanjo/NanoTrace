# NanoTrace

Tool to display squiggle plots of Oxforrd Nanopore bulk files plus some additional information about the distribution of the raw signal in a channel. Nanotrace was developed as part of research to detect and quantify small molecules using nanopores (Quint, I. et al. Ready-to-use nanopore platform for ethanolamine quantification using an aptamer-based strand displacement assay. 2023.02.27.530168 Preprint at https://doi.org/10.1101/2023.02.27.530168 (2023))

# Installation

The easiest way is to use the respective binaries ([Windows v1.0.0](https://github.com/simanjo/NanoTrace/releases/download/v1.0.0/nanotrace.exe), Linux  (tbd)).

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
# use pyinstaller to build a binary
pyinstaller --windowed --onefile nanotrace.py
```

# Usage instructions

NanoTrace consists of 3 components; an overview window, showing general information about the currently loaded file, a plot window, showing squiggle plots of selected channels or kernel density estimations for the whole run (to visualize the distribution of the raw signal) and a settings window. For more details also see the [supplementary files](https://www.biorxiv.org/content/10.1101/2023.02.27.530168v1.supplementary-material) accompanying the preprint.
