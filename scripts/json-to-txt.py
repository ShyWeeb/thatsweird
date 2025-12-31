import os
import json

def convert(path_type):
    if path_type == 1:
        json_path = os.path.join(os.getcwd(), "db.json")
        txt_path = os.path.join(os.path.dirname(os.getcwd()), "db.txt")
        
    elif path_type == 0:
        json_path = os.path.join(os.path.join(os.getcwd(), "scripts", "db.json"))
        txt_path = os.path.join(os.getcwd(), "db.txt")

    if os.path.isfile(json_path):
        print(json_path)
        print(txt_path)

        video_ids = []

        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                if 'videoID' in item:
                    video_ids.append(item['videoID'])

        # Write to .txt file, one ID per line
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write("\n".join(video_ids))
    else:
        print("JSON FILE IS NOT DETECTED...")

def path_check():
    if os.getcwd().endswith('scripts'):
        return 1 # PARENT FOLDER
    elif os.path.isfile(os.path.join(os.getcwd(), 'index.html')):
        return 0 # SCRIPTS FOLDER
    else:
        return False

def main():
    if path_check() == 1:
        convert(1)
        #convert(os.path.dirname(os.getcwd()))
    elif path_check() == 0:
        convert(0)
        #convert(os.path.join(os.getcwd(), "scripts"))
    elif path_check() == False:
        pass

if __name__ == "__main__":
    main()