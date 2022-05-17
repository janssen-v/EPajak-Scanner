from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import urllib3
import traceback
import xml.etree.ElementTree as ElementTree
import csv


# E-Pajak Parse

# noinspection PyBroadException
def get_xml(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    try:
        xml = response.data
        return xml
    except:
        print('Failed to parse xml from response (%s)' %
              traceback.format_exc())
    return


def parse_xml(xml):
    """
    Returns contents of e-faktur XML as a dict
    Args:
        xml (string): A continuous string of XML

    Returns:
        form (dict): Tax form data in dict format
    """
    form = {}  # create new form
    root = ElementTree.fromstring(xml)
    for child in root[:-1]:
        form[child.tag] = child.text

    tanggal_faktur = form.get('tanggalFaktur')
    masa_pajak = tanggal_faktur[3:-5]  # MM
    tahun_pajak = tanggal_faktur[-4:]  # YYYY

    # converts MM to M if MM < 10
    if masa_pajak[0] == '0':
        masa_pajak = masa_pajak[1:]

    form['masaPajak'] = masa_pajak
    form['tahunPajak'] = tahun_pajak

    return form


def export_csv(output_file, form_list):
    """
    Writes list of forms into a CSV file ('output_file.csv') compliant with e-faktur pajak release 3.2.0.0.
    Currently, supports FAKTUR MASUKAN only.

    Args:
        output_file (string): File name of CSV export
        form_list (list(dict)): List of tax forms in dict format
    """
    header = ['FM', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK',
              'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM',
              'IS_CREDITABLE']

    with open(output_file, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        # write header
        writer.writerow(header)
        # write rows
        for form in form_list:
            data_line = ['FM',
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
            writer.writerow(data_line)


def parse_urls(urls, output_file):
    form_list = []  # list of forms
    for url in urls:
        xml = get_xml(url)
        form = parse_xml(xml)
        form_list.append(form)
    export_csv(output_file, form_list)


# Capture Init
cap = cv2.VideoCapture(0)
cap.set(1, 720)
cap.set(2, 640)
cap.set(3, 480)


font = cv2.FONT_HERSHEY_SIMPLEX
url_list = []


def decode(im):
    # Find barcodes and QR codes
    decoded_objects = pyzbar.decode(im)
    return decoded_objects


# E-Pajak Scanner
def main():
    while cap.isOpened():

        # Capture frame-by-frame
        ret, frame = cap.read()
        # OpenCV stores image data in BGR
        im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(im)
        # Draw amount of captured URLs
        cv2.putText(frame, 'Forms scanned: ' + str(len(url_list)),
                    (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        # Draw commands
        cv2.putText(frame, 'Press S to (S)ave, Q to (Q)uit',
                    (10, 60), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        for decodedObject in decoded_objects:
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

            if url not in url_list:
                # Draw the convex hull
                for j in range(0, n):
                    cv2.line(frame, hull[j], hull[(j + 1) % n], (51, 153, 255), 3)
                # Draw text on image frame
                cv2.putText(frame, 'SCANNING', (x, y), font,
                            1, (51, 153, 255), 2, cv2.LINE_AA)
                url_list.append(url)
            else:
                # Draw the convex hull
                for j in range(0, n):
                    cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 204, 0), 3)
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
            parse_urls(url_list, 'export.csv')
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
