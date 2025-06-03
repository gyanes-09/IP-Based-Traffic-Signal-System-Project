import string
import easyocr
import csv

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}



def write_csv(results, output_path, criminal_db_path):
    """
    Write the results to a CSV file and check against a criminal database.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
        criminal_db_path (str): Path to the criminal plates CSV file.
    """
    # Load criminal plates
    criminal_plates = set()
    with open(criminal_db_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            criminal_plates.add(row[0].strip())

    with open(output_path, 'w') as f:
        f.write('frame_nmr,car_id,car_bbox,license_plate_bbox,license_plate_bbox_score,license_number,license_number_score,criminal_match\n')
        
        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                if 'car' in results[frame_nmr][car_id] and 'license_plate' in results[frame_nmr][car_id]:
                    license_number = results[frame_nmr][car_id]['license_plate']['text']
                    is_criminal = "YES" if license_number in criminal_plates else "NO"
                    
                    f.write(f"{frame_nmr},{car_id},[{results[frame_nmr][car_id]['car']['bbox']}],"
                            f"[{results[frame_nmr][car_id]['license_plate']['bbox']}],"
                            f"{results[frame_nmr][car_id]['license_plate']['bbox_score']},"
                            f"{license_number},{results[frame_nmr][car_id]['license_plate']['text_score']},"
                            f"{is_criminal}\n")

def is_valid_indian_plate(text):
    """
    Validate if the license plate matches the Indian format (XY13 CQ2345).

    Args:
        text (str): License plate text.

    Returns:
        bool: True if valid, False otherwise.
    """
    if len(text) != 10:
        return False
    
    return (text[:2].isalpha() and text[2:4].isdigit() and text[4] == ' ' and
            text[5:7].isalpha() and text[7:].isdigit())

def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Formatted license plate text and confidence score.
    """
    detections = reader.readtext(license_plate_crop)
    
    for detection in detections:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')
        
        if len(text) >= 10:
            text = text[:4] + ' ' + text[4:]
            if is_valid_indian_plate(text):
                return text, score
    
    return None, None

def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate
    for xcar1, ycar1, xcar2, ycar2, car_id in vehicle_track_ids:
        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            return xcar1, ycar1, xcar2, ycar2, car_id
    
    return -1, -1, -1, -1, -1
