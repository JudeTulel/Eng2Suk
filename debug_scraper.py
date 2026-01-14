import requests
from bs4 import BeautifulSoup

url = "https://www.bible.com/bible/2884/GEN.1.PKO?parallel=68"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        script = soup.find('script', id='__NEXT_DATA__')
        if script:
            print("Found __NEXT_DATA__ script!")
            import json
            data = json.loads(script.string)
            def find_path(obj, target, path=None):
                if path is None:
                    path = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        new_path = path + [k]
                        if isinstance(v, (dict, list)):
                            res = find_path(v, target, new_path)
                            if res: return res
                        elif isinstance(v, str) and target in v:
                            return new_path
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        new_path = path + [str(i)]
                        if isinstance(v, (dict, list)):
                            res = find_path(v, target, new_path)
                            if res: return res
                        elif isinstance(v, str) and target in v:
                            return new_path
                return None

            with open("debug_output.txt", "w", encoding="utf-8") as f:
                page_props = data.get('props', {}).get('pageProps', {})
                f.write(f"PageProps keys: {list(page_props.keys())}\n")
                
                cid = page_props.get('chapterInfoData')
                if cid:
                    f.write(f"chapterInfoData keys: {list(cid.keys())}\n")
                    f.write(f"chapterInfoData content present: {'content' in cid}\n")
                    if 'content' in cid:
                        f.write(f"English Content start: {cid['content'][:100]}\n")
                else:
                    f.write("chapterInfoData NOT found.\n")

                pcid = page_props.get('parallelChapterInfoData')
                if pcid:
                     f.write(f"parallelChapterInfoData content present: {'content' in pcid}\n")
                else:
                     f.write("parallelChapterInfoData NOT found.\n")
            print("Debug output written to debug_output.txt")
        else:
            print("__NEXT_DATA__ not found.")

except Exception as e:
    print(f"Error: {e}")
