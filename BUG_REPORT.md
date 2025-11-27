# Bug Report and Fix Summary for transkribus_xml2csv

## Issues Found

### 1. **CRITICAL BUG: Wrong Filename Being Parsed (Line 57)**
**Problem:** The code was calling `parse_filename(fname)` where `fname` is the XML file path, not the image filename.

**Original Code:**
```python
file_metadata = self.parse_filename(fname)  # Line 57
```

**Issue:** This meant the script was parsing the XML filename structure instead of the image filename structure embedded in the XML. Since XML filenames don't follow the expected format (0001_QTN_1952_07_05_001_...), the parsing would either fail or extract completely wrong values.

**Fix:** Parse the `image_filename` extracted from the XML instead:
```python
# Extract the imageFilename attribute first
page_elem = root.find('.//ns:Page', self.namespaces)
if page_elem is not None:
    image_filename = page_elem.get('imageFilename')
else:
    image_filename = None

# Then parse metadata from the IMAGE filename
if image_filename:
    file_metadata = self.parse_filename(image_filename)
else:
    raise ValueError(f"No imageFilename found in XML file: {fname}")
```

### 2. **Dictionary Key Order Issue (Lines 106-107)**
**Problem:** The code used `for k in file_metadata.keys():` to append values, which relies on dictionary ordering.

**Original Code:**
```python
for k in file_metadata.keys():
    contents[k].append(file_metadata[k])
```

**Issue:** While Python 3.7+ maintains insertion order, this approach is error-prone and makes the code less readable. The order might not match the order in `content_keys`.

**Fix:** Explicitly append each value in the correct order:
```python
contents['newspaper'].append(file_metadata['newspaper'])
contents['year'].append(file_metadata['year'])
contents['month'].append(file_metadata['month'])
contents['date'].append(file_metadata['date'])
contents['page_num'].append(file_metadata['page_num'])
```

### 3. **Duplicate Processing Loop (Lines 126-152)**
**Problem:** The script processes each XML file twice in identical loops.

**Original Code:**
```python
for fname in xml_files:
    try:
        data = self.extract_xml(fname)
        # ... save CSV ...
    except Exception as e:
        print(f'Error processing {fname}: {e}')

for fname in xml_files:  # DUPLICATE!
    try:
        data = self.extract_xml(fname)
        # ... save CSV again ...
    except Exception as e:
        print(f'Error processing {fname}: {e}')
```

**Issue:** This wastes processing time and overwrites files unnecessarily. The first loop doesn't even specify encoding, while the second uses utf-8-sig.

**Fix:** Remove the duplicate loop, keep only one with proper encoding:
```python
for fname in xml_files:
    try:
        data = self.extract_xml(fname)
        csv_filename = os.path.join(self.csv_dir, os.path.basename(fname).replace('.xml', '.csv'))
        data.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f'Processed and saved: {csv_filename}')
    except Exception as e:
        print(f'Error processing {fname}: {e}')
```

### 4. **Missing Output Directory Check**
**Problem:** The code doesn't verify that the output directory exists before trying to save files.

**Fix:** Added directory creation:
```python
# Ensure output directory exists
if not os.path.exists(self.csv_dir):
    os.makedirs(self.csv_dir)
```

### 5. **Potential None Value Issue (Line 71)**
**Problem:** `image_filename` might be None if the Page element exists but doesn't have an imageFilename attribute, leading to issues later.

**Fix:** Added proper None handling and error raising if imageFilename is missing.

## Root Cause of Your Specific Problem

The newspaper, year, month, date columns were being filled with wrong values because:

1. The script was parsing the XML filename instead of the image filename embedded in the XML
2. The XML filename doesn't follow the expected underscore-separated format
3. When splitting by underscore, it was getting completely different values at positions [1], [2], [3], [4], [5]
4. This caused a "shift" where year values appeared in the newspaper column, month in year, etc.

## Additional Notes

- The `merge_csv.py` script appears to be working correctly and doesn't need changes
- The fixed script maintains backward compatibility with the expected filename format
- All CSV outputs now use consistent utf-8-sig encoding for better compatibility with Excel

## Testing Recommendations

1. Test with a sample XML file to verify the image filename is correctly extracted
2. Verify that newspaper codes (TIM, TID, NIB, etc.) now appear in the correct column
3. Check that dates and years are properly aligned
4. Confirm that the merged CSV has all columns in the expected order
