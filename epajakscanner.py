from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import urllib3
import traceback
import xml.etree.ElementTree as et
import csv

# E-Pajak Parse


def getXml(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    try:
        xml = response.data
        return xml
    except:
        print('Failed to parse xml from response (%s)' %
              traceback.format_exc())
    return


def parseXml(xml):

    form = {}  # create new form
    root = et.fromstring(xml)
    for child in root[:-1]:
        form[child.tag] = child.text

    tanggalFaktur = form.get('tanggalFaktur')
    masaPajak = tanggalFaktur[3:-5]  # MM
    tahunPajak = tanggalFaktur[-4:]  # YYYY

    # converts MM to M if MM < 10
    if masaPajak[0] == '0':
        masaPajak = masaPajak[1:]

    form['masaPajak'] = masaPajak
    form['tahunPajak'] = tahunPajak

    return form


def exportCSV(outputFile, formList):
    header = ['FM', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK',
              'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'IS_CREDITABLE']

    with open(outputFile, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        # write header
        writer.writerow(header)
        # write rows
        for form in formList:
            dataLine = ['FM',
                        form.get('kdJenisTransaksi'),
                        form.get('fgPengganti'),
                        form.get('nomorFaktur'),
                        form.get('masaPajak'),
                        form.get('tahunPajak'),
                        form.get('tanggalFaktur'),
                        form.get('npwpPenjual'),
                        form.get('namaPenjual'),
                        form.get('alamatPenjual'),
                        form.get('jumlahDpp'),
                        form.get('jumlahPpn'),
                        form.get('jumlahPpnBm'),
                        '1']
            writer.writerow(dataLine)


def parseUrls(urls, outputFile):
    formList = []  # list of forms
    for url in urls:
        xml = getXml(url)
        form = parseXml(xml)
        formList.append(form)
    exportCSV(outputFile, formList)


# Capture Init
cap = cv2.VideoCapture(0)

cap.set(1, 720)
cap.set(2, 640)
cap.set(3, 480)

font = cv2.FONT_HERSHEY_SIMPLEX
urllist = []


def decode(im):
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    return decodedObjects


# E-Pajak Scan
while(cap.isOpened()):

    # Capture frame-by-frame
    ret, frame = cap.read()
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # OpenCV stores image data in BGR
    decodedObjects = decode(im)
    # Draw amount of captured URLs
    cv2.putText(frame, 'Forms scanned: ' + str(len(urllist)),
                (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # Draw commands
    cv2.putText(frame, 'Press S to (S)ave, Q to (Q)uit',
                (10, 60), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    for decodedObject in decodedObjects:
        points = decodedObject.polygon

        # If points do not form a quad, find convex hull
        if len(points) > 4:
            hull = cv2.convexHull(
                np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points

        # Number of points in the convex hull
        n = len(hull)
        x = decodedObject.rect.left
        y = decodedObject.rect.top

        raw = str(decodedObject.data)
        url = raw[2:-1]  # b'link' removal

        if url not in urllist:
            # Draw the convex hull
            for j in range(0, n):
                cv2.line(frame, hull[j], hull[(j+1) % n], (51, 153, 255), 3)
            # Draw text on image frame
            cv2.putText(frame, 'SCANNING', (x, y), font,
                        1, (51, 153, 255), 2, cv2.LINE_AA)
            # webbrowser.open(url)
            urllist.append(url)
        else:
            # Draw the convex hull
            for j in range(0, n):
                cv2.line(frame, hull[j], hull[(j+1) % n], (0, 204, 0), 3)
            # Draw text on image frame
            cv2.putText(frame, 'SCAN OK', (x, y), font,
                        1, (0, 204, 0), 2, cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow('E-Pajak QR Code Scanner v0.1a', frame)

    key = cv2.waitKey(1)
    # On button press (Q)uit
    if key & 0xFF == ord('q'):
        break

    # On button press (S)can
    elif key & 0xFF == ord('s'):
        # Handoff to E-Pajak Parse
        parseUrls(urllist, 'export.csv')
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
