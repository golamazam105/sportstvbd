import requests
import json
import re

sources = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/bd.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/in.m3u"
]

valid_channels = []

print("চ্যানেল স্ক্র্যাপিং শুরু হচ্ছে...")

for source in sources:
    try:
        response = requests.get(source, timeout=10)
        if response.status_code == 200:
            lines = response.text.split('\n')
            current_name = "Unknown Channel"
            
            for line in lines:
                if line.startswith("#EXTINF"):
                    # নাম খুঁজে বের করার চেষ্টা
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        current_name = name_match.group(1).strip()
                elif line.startswith("http"):
                    url = line.strip()
                    try:
                        check_res = requests.head(url, timeout=3, allow_redirects=True)
                        if check_res.status_code == 200:
                            # নাম এবং ইউআরএল ডিকশনারি আকারে রাখা
                            valid_channels.append({
                                "name": current_name,
                                "url": url
                            })
                    except:
                        pass
    except Exception as e:
        print(f"Error: {e}")

# ১. আগের মতো M3U ফাইলও তৈরি হবে (VLC এর জন্য)
with open("live_tv.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in valid_channels:
        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['url']}\n")

# ২. কোডুলারের জন্য স্পেশাল JSON ফাইল তৈরি হবে
with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(valid_channels, f, ensure_ascii=False, indent=4)

print("সব ফাইল আপডেট কমপ্লিট!")
