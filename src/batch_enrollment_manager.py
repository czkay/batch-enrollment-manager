import config
import csv
import itertools
import PySimpleGUI as sg
import logging
import os
import shutil

def initialise_logger():
    logging.basicConfig(filename='logs.txt', filemode='w', 
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO)

def join_paths():
    unenrolled_details_path = os.path.join(config.BASE_UNENROLLED_DETAILS_PATH, 'enrollment.txt')
    photos_path = config.BASE_PHOTOS_PATH
    full_details_path = os.path.join(config.BASE_FULL_DETAILS_PATH, 'persons.txt')
    return (unenrolled_details_path, photos_path, full_details_path)

def get_unenrolled_data(details_path, base_photos_path):
    with open(details_path, "r") as f:
        data = []
        reader = csv.DictReader(f)
        for row in reader:
            image_path = os.path.join(base_photos_path, row['photo_path']) # obtain the absolute path of the image
            timestamp = row['timestamp']
            id = row['id']
            data.append([image_path, timestamp, id])
    logging.info("Successfully read unenrolled data.")
    # data.sort(key=lambda ls: ls[2])
    data = dict((log[2], log) for log in data).values() # remove duplicate logs, leaving only the most recent ones
    return data # return as a list of lists, with each sublist containing a log of an unenrolled person

def clear_unenrolled_data(details_path):
    with open(details_path, "w") as f:
        f.write('photo_path,timestamp,id\n')
    logging.info("Cleared enrollment.txt.")

def initialise_window(log):
    print(log)
    sg.theme('Dark')  
    layout = [  [sg.Image(log[0], key='PHOTO')],
        [sg.Text('Timestamp ' + log[1], key='TIMESTAMP')],
        [sg.Text('Smartcard ID: ' + log[2], key='CARD_ID')],
        [sg.Text('Input employee\'s NRIC:'), sg.InputText(key='INPUT')],
        [sg.Button('Submit', bind_return_key=True), sg.Button('Discard')] ]
    window = sg.Window('Unenrolled employees', layout, finalize=True)
    window.TKroot.focus_force()
    window.Element('INPUT').SetFocus()
    return window

# loads the window to UI and waits for/processes input
def load_window(window, log, full_details_path):
    id = log[2]
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Discard':
        logging.info('Discarded log with smartcard ID %s; no NRIC submission', id)
    elif event == 'Submit':
        nric = values['INPUT']
        logging.info('Inserting NRIC (%s) and corresponding smartcard ID (%s) into persons.txt...', nric, id)
        update_full_details(nric, id, full_details_path)
    window.close()

def update_full_details(nric, id, path):
    # with open(path, 'r') as f:
    #     reader = csv.DictReader(f)
    #     data = [row for row in reader]

    # with open(path, 'w', newline='') as f:
    #     writer = csv.writer(f, delimiter=',')
    #     writer.writerow(['nric','id'])
    #     for row in data:
    #         if row['id'] == id: # found corresponding id
    #             if row['nric']: # nric is already associated
    #                 logging.warning('Employee with smartcard id of %s has already been enrolled. Overriding previous association (nric: %s) with latest association (nric: %s)',
    #                         id, row['nric'], nric)
    #             writer.writerow([nric, id])
    #         else:
    #             writer.writerow([row['nric'], row['id']])
    
    # append nric and id to persons.txt
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow([nric, id])
        logging.info("Success!")

def enroll(data_list, full_details_path):
    if data_list: # if there are unenrolled persons
        for log in data_list:
            window = initialise_window(log)
            load_window(window, log, full_details_path)
        logging.info("All unenrolled persons' details iterated.")
    else:
        logging.info("No unenrolled persons found.")

def main():
    initialise_logger()

    logging.info("Program running...")

    unenrolled_details_path, photos_path, full_details_path = join_paths()

    logging.debug('\nunenrolled_details_path: %s\nphotos_path: %s\nfull_details_path: %s', 
            unenrolled_details_path, photos_path, full_details_path)

    data_list = get_unenrolled_data(unenrolled_details_path, photos_path)

    enroll(data_list, full_details_path)

    clear_unenrolled_data(unenrolled_details_path)

    logging.info("Closing program...")

if __name__ == '__main__':
    main()








# updates the window to show details of next log
# def update_window(window):
#     window['PHOTO'].update(log[0])
#     window['TIMESTAMP'].update('Timestamp ' + log[1])
#     window['CARD_ID'].update('Smartcard ID: ' + log[2])
#     window['INPUT'].update('')

# data = requests.get('http://localhost:5000/enrollment/get') for future use if/when we need to switch to API calls

# if data_list: # if there are unenrolled persons
#     window = setup_window()
#     logging.debug('Set up window with first log')
#     for log in data_list[1:]:
#         if read_window(window):
#             update_window(window)
#         else:
#             break

#     if read_window(window):
#         update_window(window)

#     window.close()
#     logging.info("All unenrolled persons' details iterated. Closing program...")
#     print("All unenrolled persons' details iterated. Closing program...")
# else:
#     logging.info("No unenrolled persons, closing program...")
#     print("No unenrolled persons recorded. Closing program...")