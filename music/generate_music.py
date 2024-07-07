import requests 
import time
import os

endpoint = "https://api.sunoaiapi.com/api/v1/"
headers = {
    "api-key": os.getenv("SUNO_API_KEY"),
    "content-type": "application/json",
}

def create_music_task(title, tags, prompt, model) :
    if isinstance(tags, list):
        print( "Converting tags to list")
        tags = ",".join(tags)
    data = {
        "title": title,
        "tags": tags,
        "prompt": prompt,
        "mv": model,
    }

    print (f"Data: {data}")
    try:
        result = requests.post(
        endpoint + "/gateway/generate/music", headers=headers, json=data
        )
        return result.json()
    except Exception as e:
        return {"error": str(e)}
    
def query_result (ids_array) :
    ids = ",".join(ids_array)
    try:
        result = requests.get(f"{endpoint}/gateway/query/?ids={ids}", headers=headers)
        return result.json()
    except Exception as e:
        return {"error": str(e)}
    
def generate_music(title, tags, prompt, model="chirp-v3-5"):
    tasks_details = create_music_task(title, tags, prompt, model)
    task_ids = []
    
    print (f"Task details: {tasks_details}")

    for task in tasks_details ["data"]:
        print (task)
        task_ids. append (task["song_id"])

    all_resolved = False

    while not all_resolved:
        results = query_result(task_ids)
        all_resolved = all(
            json_obj["status"] in ["complete", "error"] for json_obj in results
        )
        if all_resolved:
            audio_urls = [json_obj["audio_url"] for json_obj in results]
        else:
            time.sleep (1)
    return audio_urls