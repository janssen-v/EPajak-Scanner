# EPajak-Scanner
An open source scanner for E-Pajak forms. Format compatible with the e-faktur pajak application (v3.2).
### Important Notice
This is a very early testing release, only capable of scanning incoming tax invoices (faktur masukan), outgoing tax invoice support will be added with further development.

## Usage Instructions
#### English
1. Run epajakscanner.py.
2. Scan QR code on tax form with webcam.
3. The counter on the top left of the frame shows how many forms are stored in memory.
4. Press S to save scanned the forms as a CSV file (export.csv), or Q to exit without saving.
#### Bahasa Indonesia
1. Jalankan epajakscanner.py.
2. Scan kode QR dalam faktur pajak dengan webcam.
3. Penghitung yang ada di bagian atas kiri frame memberitahu berapa form yang telah disimpan.
4. Tekan S untuk menyimpan faktur sebagai file CSV (export.csv), atau Q untuk keluar tanpa save.

## Documentation
### Package dependencies
- Opencv-Python
- pyzbar
- urllib3
- numpy
### Licensing
EPajak-Scanner is available under MIT license.
