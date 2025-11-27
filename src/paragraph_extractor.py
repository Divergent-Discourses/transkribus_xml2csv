"""
To use this code:

* Place the directory containing your pageXML files into the ./data/to_process_xml directory
* Navigate to the ./transkribus_utils directory using the 'cd' command then run:

    python ./src/paragraph_extractor.py

* After running, find the .csv file outputs in the ./data/processed_csv directory.

"""
import os
from xml.etree import ElementTree as ET
import fnmatch
import pandas as pd
import re

class XMLParagraphExtractor:

    def __init__(self, namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}, xml_dir="./data/to_process_xml",
                 csv_dir="./data/processed_csv"):
        """
        Initialises the XMLParagraphExtractor with specified directories.
        """
        self.namespaces = namespaces
        self.xml_dir = xml_dir
        self.csv_dir = csv_dir


    def parse_filename(self, fstring):
        """
        Parses metadata from the filename. Assumes metadata is stored in filename, formatted: 0001_QTN_1952_07_05_001_SB_Zsn128163MR.jpg
        (0001 = transkribus-assigned ID, QTN = newspaper name/code, 1952 = year, 07 = month, 05 = date, 001 = page, remaining info = irrelevant
        and shouldn't affect parsing). Elements should be underscore-separated. Order matters.
        fstring (str): filepath or filename
        """
        filename = os.path.basename(fstring)  # Extract only the filename

        f_attributes = filename.split('_')

        if len(f_attributes) < 6:
            raise ValueError(f"Unexpected filename format: {filename}")

        newspaper = f_attributes[1]
        year = f_attributes[2]
        month = f_attributes[3]
        date = f_attributes[4]
        page_num = f_attributes[5]

        return {'newspaper': newspaper, 'year': year, 'month': month, 'date': date, 'page_num': page_num}


    def extract_xml(self, fname):
        """
        Extracts text paragraphs from a PAGE XML file and returns a DataFrame.
        """
        with open(fname, 'r', encoding='utf-8') as f:
            data = f.read()

        root = ET.fromstring(data)
        content_keys = ['paragraph', 'paragraph_idx', 'readingorder_idx', 'region_type', 'filename', 'newspaper', 'year', 'month', 'date', 'page_num']
        contents = {k: [] for k in content_keys}

        # Extract the imageFilename attribute
        page_elem = root.find('.//ns:Page', self.namespaces)

        if page_elem is not None:
            image_filename = page_elem.get('imageFilename')
        else:
            image_filename = None

        # Parse metadata from the IMAGE filename (not the XML filename)
        if image_filename:
            file_metadata = self.parse_filename(image_filename)
        else:
            raise ValueError(f"No imageFilename found in XML file: {fname}")

        for text_region in root.findall('.//ns:TextRegion', self.namespaces):

            # Extract paragraph_idx
            region_idx = text_region.get('id')

            # Extract region_type by parsing 'custom' attribute
            custom_attribute = text_region.get('custom')
            match = re.search(r'type:([^;}]+)', custom_attribute)
            region_type = match.group(1) if match else None  # Extracted type or None if not found

            # Extract readingorder_num by parsing 'custom' attribute
            match = re.search(r'readingOrder\s*\{index:(\d+);', custom_attribute)
            readingorder_num = int(match.group(1)) if match else None  # Extracted index as an integer or None if not found

            # Extract region_text by concatenating text lines
            region_text = ''

            for text_equiv in text_region.findall('.//ns:TextEquiv/ns:Unicode', self.namespaces):
                content = text_equiv.text

                if content:
                    region_text = region_text + content
                    region_text = region_text.replace('\n', '')
                    region_text = region_text.replace('\t', ' ')

            contents['paragraph'].append(region_text)
            contents['paragraph_idx'].append(region_idx)
            contents['readingorder_idx'].append(readingorder_num)
            contents['region_type'].append(region_type)
            contents['filename'].append(image_filename)

            # Collect metadata in the correct order: newspaper, year, month, date, page_num
            contents['newspaper'].append(file_metadata['newspaper'])
            contents['year'].append(file_metadata['year'])
            contents['month'].append(file_metadata['month'])
            contents['date'].append(file_metadata['date'])
            contents['page_num'].append(file_metadata['page_num'])

        return pd.DataFrame(contents)


    def parse_transkribus(self):

        xml_files = []
        excluded_files = ['mets.xml', 'metadata.xml']

        for root, _, files in os.walk(self.xml_dir):
            for file in files:
                if file.endswith('.xml') and file not in excluded_files:
                    xml_files.append(os.path.join(root, file))

        if not xml_files:
            print("No XML files found in to_process_xml/")
            return

        # Ensure output directory exists
        if not os.path.exists(self.csv_dir):
            os.makedirs(self.csv_dir)

        for fname in xml_files:
            try:
                data = self.extract_xml(fname)

                # Save CSV in the processed_csv directory
                csv_filename = os.path.join(self.csv_dir, os.path.basename(fname).replace('.xml', '.csv'))
                data.to_csv(csv_filename, index=False, encoding='utf-8-sig')

                print(f'Processed and saved: {csv_filename}')

            except Exception as e:
                print(f'Error processing {fname}: {e}')


# Run the processing
if __name__ == "__main__":
    extractor = XMLParagraphExtractor()
    extractor.parse_transkribus()
