import os

success_ips = []
failed_ips = []
folder_path = '/root/pi/nt_tool/united_award_tracking'

files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
latest_files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)), reverse=True)[:250]

#with open("/root/pi/nt_tool/united_award_tracking/2023-11-14 15:00:04.684904.log", 'r') as file:
#    lines = file.readlines()

ip_counts = {}

for file_name in latest_files:
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        line = lines[i].strip()

        if line.startswith("proxy ip:"):
            proxy_ip = line.split("http://")[1].split("'")[0]
            if lines[i + 1].startswith("search takes"):
                # Increment the success count for the IP
                ip_counts[proxy_ip] = ip_counts.get(proxy_ip, [0, 0])
                ip_counts[proxy_ip][0] += 1
            elif lines[i + 1].startswith("calendar_search"):
                pass
            else:
                # Increment the failed count for the IP
                ip_counts[proxy_ip] = ip_counts.get(proxy_ip, [0, 0])
                ip_counts[proxy_ip][1] += 1

for k, v in ip_counts.items():
    if v[0] + v[1] > 8 and v[0]/(v[0]+v[1]) * 100 > 85:
        #print(k)
        print(f"{k}: {v[0]}, {v[1]}, {v[0]/(v[0]+v[1]) * 100:.2f}%")

