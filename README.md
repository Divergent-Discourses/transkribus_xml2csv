# Description

This repository holds utilities for parsing and extracting useful data from [Transkribus](https://www.transkribus.org/) PageXML outputs, such as a utility for identifying text regions (Paragraph Extractor), and a utility to reconcile Transkribus output metadata with the equivalent data in relevant library catalogues (coming shortly).

**Paragraph Extractor** is a utility that accepts Transkribus PageXML as input and then interprets the text regions on each page/image (such as headers, titles, blocks of text, etc.), which we term "paragraphs". It then returns the raw text of each text region (paragraph) along with its metadata. Note that it **reads PageXML, not AltoXML**.


## Paragraph Extractor

`paragraph_extractor.py` takes a directory containing pageXML files. For each pageXML file, it generates a CSV containing the page's relevant metadata including its text regions (one per row). The method assumes the Transkribus "text region" is an acceptably accurate 1:1 proxy for a paragraph.

CSV columns include:

* Paragraph (str): The text recognised by Transkribus HTR
* Paragraph ID (str): E.g.	tr_1718110017
* Region type (str): E.g. caption, heading, paragraph, other
* Filename (str): E.g. 0001_QTN_1959_10_03_001_SB_Zsn128163MR.jpg. The original image filename, extracted from the pageXML. Filenames must be underscore-separated with elements ordered as follows for the code to work as intended - 4-digit code assigned by Transkribus (0001), newspaper name/code (QTN), year (1959), month (10), date (03), page (001). Remaining information in filename is not extracted
* Newspaper (str): E.g. QTN - parsed from the original image filename
* Year (int): Parsed from the original image filename
* Month (int): Parsed from the original image filename  
* Date (int): Parsed from the original image filename  

The program recursively searches input directories for .xml files, so clean file structures are important!

### Installation

Using the command line, navigate to the location in which you wish to download the code. Then, download the code.

```bash
git clone https://github.com/Divergent-Discourses/transkribus_xml2csv.git
```

Create a virtual environment.

```bash
conda create -n xml2csv python=3.12.2
```

Activate the environment.

```bash
conda activate xml2csv
```

Using the command line, navigate to the location of this repository. Then, install required packages.

```bash
cd transkribus_xml2csv
pip install -r requirements.txt
```

### Using the Paragraph Extractor

Move the directories containing your pageXML files (.xml) into the `./data/to_process_xml` directory.

Navigate via the command line into this **transkribus_xml2csv** directory.

To **parse the pageXML** files and output a series of .csv files, call:

```bash
python ./src/paragraph_extractor.py 
```

.csv files will be outputted to `./data/processed_csv`.


To **merge .csv files** into a single .csv file, call:

```bash
python merge_csv.py
```

The master .csv file will be outputted to `./data/merged_csv`


Remember to deactivate the virtual environment once you're done.

```bash
conda deactivate xml2csv
```


## Copyright

**Paragraph Extractor** was developed by James Engels and modified by Christina Sabbagh, both of SOAS University of London, for the Divergent Discourses project. The project is a joint study involving SOAS University of London and Leipzig University, funded by the AHRC in the UK and the DFG in Germany. Please acknowledge the project in any use of these materials. Copyright for the project resides with the two universities. 
