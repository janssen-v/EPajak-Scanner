<img src="logo.png" width="128"/>

# EPajak-Scanner
An open source scanner for E-Pajak forms. Format compatible with the e-faktur pajak application (v3.2).
### Important Notice
This is a very early testing release, only tested with incoming tax invoices (faktur masukan). There is preliminary support for outgoing tax invoices, however it is yet to be tested.

## Build Instructions
1. Clone the repo
2. Build the provided spec file with PyInstaller
```
pyinstaller EPJS.spec
```

## Documentation
### Package dependencies
- Opencv-Python
- pyzbar
- urllib3
- numpy
- PySimpleGUI
### Licensing
EPajak-Scanner is available under MIT license.
