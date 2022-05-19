from cgitb import enable, text
import PySimpleGUI as sg
import cv2
import traceback
import urllib3
import numpy as np
import pyzbar.pyzbar as pyzbar
import xml.etree.ElementTree as ElementTree
import csv
import os
import sys

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


def export_csv(output_file, form_list, mode):
    """
    Writes list of forms into a CSV file ('output_file.csv') compliant with e-faktur pajak release 3.2.0.0.
    Currently, supports FAKTUR MASUKAN only.

    Args:
        output_file (string): File name of CSV export
        form_list (list(dict)): List of tax forms in dict format
    """
    
    # MODE Selector
    F_MK = 'FK' if mode else 'FM'
    
    header = [F_MK, 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK',
              'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM',
              'IS_CREDITABLE']

    with open(output_file, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        # write header
        writer.writerow(header)
        # write rows
        for form in form_list:
            data_line = [F_MK,
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
            
            
def parse_url(url):
    xml = get_xml(url)
    form = parse_xml(xml)
    return form


def decode(im):
    # Find barcodes and QR codes
    decoded_objects = pyzbar.decode(im)
    return decoded_objects


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# App Event Loop

# Globals
MODE = True

# Window Layout
output_path = ''
form_list = []
left_col = [[sg.Text('Faktur Tersimpan', font='ArialBold 12', pad=(15,0))],
            [sg.Listbox(values= form_list, enable_events=True, size=(35,28), key = '-FORM LIST-')],
            [sg.Button('Export CSV', key='-EXPORT-'), sg.Button('Faktur Keluar', key='-MODE-'), sg.Button('Start Scan', key='-SCAN-')]]

            

viewport_col = [[sg.Image(filename='', key='-FRAME-')]]
# Full Layout
layout = [[sg.Column(left_col), sg.VSeparator(), sg.Column(viewport_col)]]

# Make Window
icons = resource_path('epjs.ico')
window = sg.Window('E-Pajak QR Scanner', layout, grab_anywhere=True, icon=icons)

# Run Event Loop
url_list = [] # url list persistence since scan may be started and stopped
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    # Start Scanner
    if event == '-SCAN-':
        sg.popup_quick_message('Initializing Scanner', auto_close_duration=0.5, background_color='red', text_color='white', font='Any 16')
        window['-SCAN-'].update('Stop Scan', button_color=('white', 'red'))
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = decode(im)
            
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
                    cv2.putText(frame, 'SCANNING', (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (51, 153, 255), 2, cv2.LINE_AA)
                    url_list.append(url)
                    single_form = parse_url(url) 
                    form_list.append(single_form)
                    window['-FORM LIST-'].update(values= [form['nomorFaktur'] for form in form_list])
                else:
                    # Draw the convex hull
                    for j in range(0, n):
                        cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 204, 0), 3)
                    # Draw text on image frame
                    cv2.putText(frame, 'SCAN OK', (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 204, 0), 2, cv2.LINE_AA)
                
                
            # Show frame in viewport
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window['-FRAME-'].update(data=imgbytes)
            event, values = window.read(timeout=0)
            if event in (None, '-SCAN-', 'Exit'):
                window['-SCAN-'].update('Start Scan', button_color=sg.theme_button_color())
                window['-FRAME-'].update('')
                cap.release()
                break
            
    # Update Mode Indicator
    if event == '-MODE-':
        # Mode true = FK, false = FM
        MODE = not MODE
        if MODE:
            window['-MODE-'].update('Faktur Keluar')
        else:
            window['-MODE-'].update('Faktur Masuk')
    
    # Handle Export Button
    if event == '-EXPORT-':
        try:
            output_path = sg.popup_get_file('Export Forms as CSV', save_as=True, file_types=(('Comma Separated Value', '*.csv'),),icon=icons)
            export_csv(output_path, form_list, MODE)
        except:
            continue
    
            