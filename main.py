import urllib2
import json
import os
import errno
import requests

# Where all metadata is stored in JSON format
metadata = "images/meta_data.txt"

# Starts at 0 image
image_no = 0
data = "1"

# Check for directory and file
if not os.path.exists(os.path.dirname(metadata)):
    try:
        os.makedirs(os.path.dirname(metadata))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

# Get the last downloaded image at the metadata file
with open(metadata, "r+") as file:
    if os.path.getsize(metadata) == 0:
        metadata_file = {}
    else:
        metadata_file = json.load(file)
        for i in metadata_file:
            image_no = image_no + 1

# While there is data, parse JSON
while len(data) > 0:
    # Define data url
    data = json.load(urllib2.urlopen("https://isic-archive.com/api/v1/image?limit=50&offset=" + str(image_no) + "&sort=name&sortdir=1&detail=true"))

    for image in data:
        print(image_no);
        try:
            # Get the data
            id = image["_id"]
            age = image["meta"]["clinical"]["age_approx"]
            benign_malignant = image["meta"]["clinical"]["benign_malignant"]
            sex = image["meta"]["clinical"]["sex"]
            img_type = image["meta"]["acquisition"]["image_type"]
            try:
                race = image["meta"]["unstructured"]["race"]
            except:
                race = "Uknown"

            img_url = "https://isic-archive.com/api/v1/image/" + str(id) + "/download?contentDisposition=inline"

            # Save image to file
            f = open("images/" + str(image_no) + ".jpg", "wb")
            try:
                f.write(requests.get(img_url).content)
            except:
                break
            f.close()

            # Prepare structure for concatenate metadata
            new_mdata = {str(image_no): {"id": id, "age": age, "benign_malignant": benign_malignant, "diagnosis":diagnosis, "sex":sex, "img_type":img_type, "race":race ,"filename": str(image_no) + ".jpg"}}
            metadata_file.update(new_mdata)

            # Save metadata to file
            with open(metadata, "w") as filesave:
                json.dump(metadata_file, filesave, indent=4, sort_keys=True)
        except:
            print("Failed: " + str(image_no) + ". Probably missing metadata.")

        # Move to next image
        image_no = image_no + 1;