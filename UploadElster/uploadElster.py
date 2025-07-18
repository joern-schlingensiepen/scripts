import os
import pyperclip

def find_pdf_file (line):    
    line = line.strip("\"")  # Remove quotes
    if not line.lower().endswith('.pdf'): return None
    if os.path.isfile(line): return line
    if line.startswith('file://'):
        line = line[7:]  # Remove 'file://' prefix
        line = line.replace('/', os.path.sep)  # Replace forward slashes with OS-specific path separator 
    if os.path.isfile(line): return line
    line = "\\\\" + line
    print(line)
    if os.path.isfile(line): return line    
    return None

# Read lines from clipboard
lines = pyperclip.paste().splitlines()
paths = []
for line in lines:
    path = find_pdf_file(line)
    if path is not None:
        paths.append(path)

if len(paths) == 0:
  print ("No PDFs found, you should copy them by <Copy as path>...")
  exit()

print ("Found " + str(len(paths)) + " PDF files")
print (paths)

from selenium import webdriver
from selenium.webdriver.common.by import By
import pyperclip
import time
from selenium.webdriver.support.ui import Select

pyperclip.copy(r"\\fileserver\orga\data\jsp-pers_elster_24.11.2022_12.38.pfx")
# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

driver.get('https://www.elster.de/eportal/login/softpse')

dlg = input ("Logged in to Elster? (y/n):")
if ("n" in dlg.lower()) : 
    driver.quit()
    exit()

res = []

for path in paths:
    driver.get('https://www.elster.de/eportal/formulare-leistungen/alleformulare/belegnachreichung')
    driver.implicitly_wait(3)

    # Find the element with the text "Alle Formulare"
    element = driver.find_element(By.CSS_SELECTOR, "[aria-label='Weiter. Weiter ins Formular'")
    # Click on the element
    element.click()
    driver.implicitly_wait(3)
    time.sleep(.5)

    for dialog in driver.find_elements(By.XPATH, "//span[text()='Steuernummer']"):
        print ("TTT")
        dialog.click()
    time.sleep(.5)

    select_element = driver.find_element(By.ID, 'dialogeruBelegnachreichungOrdnungsbegriffSteuernummer-country')
    select = Select(select_element)
    select.select_by_visible_text('Hessen')

    time.sleep(.5)

    input = driver.find_element(By.ID, 'dialogeruBelegnachreichungOrdnungsbegriffSteuernummer-tax-number-tax-office')
    # input.send_keys('01886530882')
    #input.send_keys('01847803196') # Jago Schlingensiepen
    input.send_keys('01847803362') # Lea Schlingensiepen

    time.sleep(.5)

    button = driver.find_element(By.ID, 'NextPage')
    button.click()

    selects = driver.find_elements(By.TAG_NAME, 'select')
    for select_element in selects:
        select = Select(select_element)
        select.select_by_visible_text('natürliche Person')

    # values = [None, '63501147828', 'Jörn Schlingensiepen', 'Prof. Dr.-Ing.', 'Jörn', 'Schlingensiepen', 'Jörn Schlingensiepen','', '14.10.1976', None, None]
    # values = [None, '92603381571', 'Jago Schlingensiepen', '', 'Jago', 'Schlingensiepen', 'Jago Schlingensiepen','', '19.07.2002', None, None]
    values = [None, '94603378525', 'Lea Schlingensiepen', '', 'Lea', 'Schlingensiepen', 'Lea Schlingensiepen','', '11.05.1999', None, None]
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    inputs = [input for input in inputs if input.get_attribute('type') != 'hidden']

    for input in inputs:
        print (input.get_attribute('name'))

    for value, input in zip (values, inputs):
        if value is None:
            continue
        input.clear()
        input.send_keys(value)
        time.sleep(.5)

    button = driver.find_element(By.ID, 'NextPage')
    button.click()
    time.sleep(1)

    button = driver.find_element(By.ID, 'NextPage')
    button.click()
    time.sleep(1)

    button = driver.find_element(By.ID, 'NextPage')
    button.click()
    time.sleep(1)

    selects = driver.find_elements(By.TAG_NAME, 'select')
    select = Select(selects[0])
    select.select_by_visible_text('2023')

    select = Select(selects[1])
    select.select_by_visible_text('Einkommensteuererklärung')

    button = driver.find_element(By.ID, 'NextPage')
    button.click()
    time.sleep(1)

    dropzone = driver.find_element(By.CLASS_NAME, 'objectField__field')

    # Path to the file you want to drop
    file_path = path
    # "C:\Users\joern\Downloads\38C3-XVQGLD7HGL-1-pdf_scan.pdf""

    inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
    for input in inputs:
        input.clear()
        display_name = os.path.basename(file_path)
        display_name = os.path.splitext(display_name)[0]
        display_name = display_name.replace('-', ' ')
        display_name = display_name.replace('_', ' ')
        input.send_keys(display_name)
    time.sleep(1)

    elements = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
    for element in elements:
        element.send_keys(file_path)
    time.sleep(3)

    button = driver.find_element(By.ID, 'SwitchModus')
    button.click()
    time.sleep(15)

    button = driver.find_element(By.ID, 'defaultbutton')
    button.click()
    time.sleep(4)

    button = driver.find_element(By.ID, 'defaultbutton')
    button.click()
    time.sleep(4)

    transferticket = driver.find_element(By.ID, 'transferticket')

    transferticket = transferticket.text
    res.append ([transferticket, display_name, file_path])
    print (res)

print (res)

for r in res:
    print ("Transferticket " + r[0] + "\t" + r[1])

driver.quit()
