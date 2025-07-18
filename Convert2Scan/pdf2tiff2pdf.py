import pyperclip
import os
import ghostscript
from PIL import Image
from PIL import ImageSequence
import ftputil
import random
import qrcode
import string

# file://fileserver/work/Farming/Homberg/Mieter/2024-12-18_Mietvertrag_2-L-Abdi-1.pdf
# file://fileserver/work/Farming/Homberg/Mieter/2024-12-18_Mietvertrag_2-L-Abdi-2.pdf

def find_pdf_file (line):    
    line = line.strip("\"")  # Remove quotes
    # if not line.lower().endswith('.pdf'): return None
    if os.path.isfile(line): return line
    if line.startswith('file://'):
        line = line[7:]  # Remove 'file://' prefix
        line = line.replace('/', os.path.sep)  # Replace forward slashes with OS-specific path separator 
    if os.path.isfile(line): return line
    line = "\\\\" + line
    print(line)
    if os.path.isfile(line): return line    
    return None

def tiff_pdf (path):
    tiff_filename = os.path.basename(path[0:-4]) + '_scan.tiff'
    print(tiff_filename)
    pdf_filename = path[0:-4] + '_scan.pdf'

    args = ["pdf2tiff", "-dNOPAUSE", "-r600", "-sDEVICE=tiff24nc", "-dBATCH", "-sOutputFile=" + tiff_filename,  path]
    ghostscript.Ghostscript(*args)

    new_filename = tiff_filename.replace('.tiff', '.pdf')
    # Load multipage TIFF
    tiff_image = Image.open(tiff_filename)

    # Convert TIFF to PDF with A4 format
    pdf_filename = path[0:-4] + '_scan.pdf'
    ## , append_images=enumerate(ImageSequence.Iterator(tiff_image))
    print(pdf_filename)
    tiff_image.save(pdf_filename, format='PDF', resolution=600, save_all=True)
    tiff_image.close()
    # Delete TIFF file
    os.remove(tiff_filename)
    return pdf_filename

def upload_file (path, random_dir):
    # establish a connection to a ftps server accepting all certificates
    with ftputil.FTPHost('home697972399.1and1-data.host', 'u90468258', 'Hallo1finchen!') as host:
        print("Connected to FTP server" + host.getcwd())        
        host.chdir('/u90468258/seb.news/download')
        print("Current Folder on FTP server" + host.getcwd())
        if not host.path.exists(random_dir):
            host.mkdir(random_dir)
        # change to the new directory
        host.chdir(random_dir)
        print("Current Folder on FTP server" + host.getcwd())
        # upload the file
        remote_path = os.path.basename(path)
        # replace all characters that are not a-z, A-Z, 0-9, or a dot with an underscore
        remote_path = ''.join([c if c.isalnum() or c == '.' or c == '-' else '_' for c in remote_path])
        print("Start uploading " + path + " to " + remote_path)
        host.upload(path, remote_path, print)
        print("Uploaded " + path + " to " + remote_path)
        url = f'https://seb.news/download/{random_dir}/{remote_path}'
        return url, remote_path
    
def publish_file (paths):
    print ("Publishing files")
    # create a subdirectory named a random name containing 0-9 and a-z with a length of 32 characters
    random_dir = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    print("Random directory: " + random_dir)
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        print("Uploading " + path)
        url, remote_path = upload_file(path, random_dir)
        # generate a QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=55,
            border=4,
        )
        qr.add_data(url)        
        qr.add_data('Scan the QR code to download the file')
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_code_name = 'qr-'+ os.path.basename(path)+'.png'
        img.save(qr_code_name)
        # shell command to open the QR code
        os.startfile(qr_code_name)
        # shell command to open the URL
        os.startfile(url)
        yield url, remote_path

def publish_pack (urls, remote_paths):
    # open text file in write mode
    with open("index.html", "w") as file:
        file.write('<html>\n<body>\n')
        for url, remote_path in zip(urls, remote_paths):
            file.write(f'<a target="_blank" href="{url}">{remote_path.replace("_", " ")}</a><br>\n')
        file.write('</body>\n</html>')
    for url, remote_path in publish_file("index.html"):
        print(f'Published pack at {url}')        

# Read lines from clipboard
lines = pyperclip.paste().splitlines()
paths = []
# Check if each line is a valid path to a PDF file
for i, line in enumerate(lines):
    print(line)
    path = find_pdf_file(line)
    if path:
        print(f'Valid path: {path}')
        paths.append(path)
    else:
        print(f'Invalid path: {line}')

print ("t - vertiffen")
print ("u - upload")
print ("p - pack upload")
print ("x - exit")

dlg = input ("Process steps:")

if ("x" in dlg.lower()) : exit()

if ("t" in dlg.lower()) :
    new_filenames = []
    for path in paths:
        if path.lower().endswith('.pdf'):
            new_filenames.append(tiff_pdf(path))
        else:
            new_filenames.append(path)
    paths = new_filenames

urls = []
remote_paths = []
if ("u" in dlg.lower() or "p" in dlg.lower()):
    for path in paths :
        for url, remote_path in publish_file(path):
            urls.append(url)
            remote_paths.append(remote_path)
        
if ("p" in dlg.lower()):
    publish_pack(urls, remote_paths)

for url in urls:
    print(url)

print ("Done")
