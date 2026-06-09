import requests

# ১. যেসব সোর্স থেকে চ্যানেল নিতে চান (এখানে ডেমো হিসেবে কিছু দেওয়া হলো)
sources = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/bd.m3u", # বাংলাদেশ
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/in.m3u"  # ইন্ডিয়া
]

valid_channels = []

print("চ্যানেল স্ক্র্যাপিং এবং চেকিং শুরু হচ্ছে...")

for source in sources:
    try:
        response = requests.get(source, timeout=10)
        if response.status_code == 200:
            lines = response.text.split('\n')
            current_info = ""
            
            for line in lines:
                if line.startswith("#EXTINF"):
                    current_info = line
                elif line.startswith("http"):
                    url = line.strip()
                    # ২. লিঙ্কটি সচল কিনা চেক করা (Link Validation)
                    try:
                        # শুধু হেডার চেক করা হচ্ছে যাতে দ্রুত কাজ হয়
                        check_res = requests.head(url, timeout=3, allow_redirects=True)
                        if check_res.status_code == 200:
                            valid_channels.append(f"{current_info}\n{url}")
                    except:
                        pass # ডেড লিঙ্ক হলে বাদ যাবে
    except Exception as e:
        print(f"Error loading source {source}: {e}")

# ৩. ফ্রেশ M3U প্লেলিস্ট ফাইল তৈরি করা
with open("live_tv.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for channel in valid_channels:
        f.write(channel + "\n")

print(f"কাজ শেষ! মোট {len(valid_channels)}টি সচল চ্যানেল পাওয়া গেছে।")
