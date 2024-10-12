import requests
import os
import datetime
import json
import time

## --------- VARIABLES --------------------------

ROOT_DIR = os.getcwd()
PLAYLIST_META_DIR = os.path.join(ROOT_DIR, "001_metadata", "001_playlists")
TRACKS_META_DIR = os.path.join(ROOT_DIR, "001_metadata", "002_tracks")


## --------- FUNCTIONS --------------------------

# get playlist link from user
def get_playlist_link():
    playlist_link = input('\nProvide a SPOTIFY playlist link:\n\n\t>>\t')
    return playlist_link

# parse playlist link from the user
def parse_link(link:str, preffix:str="https://open.spotify.com/playlist/"):
    step_one = link.removeprefix(preffix)
    step_two = step_one.split("?")[0]
    return step_two

# validate the playlist link from user
def validate_link(link:str):
    link_preffix = "https://open.spotify.com/playlist/"
    if link.startswith(link_preffix):
        link = parse_link(link=link)
        return link
    else:
        return print("INVALID LINK")
        
# get the playlist metadata
def get_playlist_metadata(playlist_id:str):

    url = f"https://api.spotifydown.com/metadata/playlist/{playlist_id}"

    header_url = "https://spotifydown.com"
    
    payload = {}
    headers = {'Origin': header_url,
               'Referer': header_url}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()

# generate current time as string HHMMSSDDMMYYYY
def get_current_time():
    return datetime.datetime.now().strftime("%H%M%S%d%m%Y")

# save log metadata playlist searched
def log_metadata(json_file, file_title, metadata_path):
    save_time = get_current_time()
    file_name = f"{save_time} - {file_title}.json"
    file_path = os.path.join(metadata_path, file_name)
    with open(file_path, 'x') as file:
        json.dump(json_file, file, indent=4)
        file.close()
    
# get the playlist songs
def get_playlist_tracks(playlist_id:str, offset=0):

    url = f"https://api.spotifydown.com/trackList/playlist/{playlist_id}?offset={offset}"
    header_url = "https://spotifydown.com"

    payload = {}
    headers = {'Origin': header_url,'Referer': header_url}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    return response.json()

# iterate playlist pages using offset and stop at nextOffset=None
def iterate_playlist_pages(playlist_data:str, playlist_id:str):

    offset_count = int(playlist_data["nextOffset"])
    track_list = playlist_data["trackList"]

    while offset_count != None:

        # request playlist tracks based on next offset
        response = get_playlist_tracks(playlist_id=playlist_id, offset=offset_count)

        # extend the existing list with the new page tracks
        extension_tracks = response["trackList"]
        track_list.extend(extension_tracks)

        # set the offset count to the current offset available try to set to int, if not because is none
        try:
            offset_count = int(response["nextOffset"])
        except:
            offset_count = response["nextOffset"]


    return track_list

# get the track download link -- ADD CHANGE TO NUMBER OF TRIALS
def get_track_download_link(track_id:str):
    url = f"https://api.spotifydown.com/download/{track_id}"
    header_url = "https://spotifydown.com"

    payload = {}
    headers = {'Origin': header_url,'Referer': header_url}

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    status_code = response["statusCode"]
    
    connections_tried = 1

    if status_code == 200:
        # print(connections_tried)
        return response


    while status_code != 200 or connections_tried == 10:
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        status_code = response["statusCode"]
        connections_tried += 1
        time.sleep(0.300)


    # print(connections_tried)
    return response

# from the given response extract the link of the song
def extract_track_link(track_response):
    return track_response["link"]

## --------- EXECUTION --------------------------


# step_one = get_playlist_link()
playlist_id = validate_link(link="https://open.spotify.com/playlist/37i9dQZF1CyMfoowXy73oF?si=7k7GZfsuS7qbNigr1aI92Q")

# get the metadata for the playlist
playlist_metadata = get_playlist_metadata(playlist_id)

# save the metadata to the log file
log_metadata(playlist_metadata, playlist_metadata["title"], PLAYLIST_META_DIR)

# get the playlist tracks
playlist_tracks = get_playlist_tracks(playlist_id)

# iterate to get all the tracks
track_list = iterate_playlist_pages(playlist_id=playlist_id, playlist_data=playlist_tracks)

# save the metadata of the tracks
log_metadata(track_list, playlist_metadata["title"], TRACKS_META_DIR)

# filter only the ids for testing
track_id_list = [item['id'] for item in track_list]

track_links = list()

# create a loop for the tracks
for link in track_id_list:

    # request single track download - TEST
    track_info = get_track_download_link(link)

    # extrack link
    track_link = extract_track_link(track_info)

    # append link to track links
    track_links.append(track_link)

with open('test_links.txt', 'a') as file:
    [file.write(f"{line}\n") for line in track_links]
    file.close()