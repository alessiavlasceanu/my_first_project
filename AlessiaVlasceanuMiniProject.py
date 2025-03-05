import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime

STATIONS = [
    {"label": "London", "stationReference": "246424TP"},
    {"label": "Hull", "stationReference": "041917"},
    {"label": "Newcastle", "stationReference": "017651"},
    {"label": "Plymouth", "stationReference": "47155"},
    {"label": "Liverpool", "stationReference": "550148"}
]
API_URL = "https://environment.data.gov.uk/flood-monitoring/id/stations/{stationReference}/readings"
EA_REGIONS = {
    "246424TP": "Thames",
    "041917": "North East",
    "017651": "North East",
    "47155": "South West",
    "550148": "North West"
}

def fetch_station_data(station_reference):
    response = requests.get(API_URL.format(stationReference=station_reference))
    if response.status_code == 200:
        return response.json()["items"]
    return None

def update_station_data(event):
    station = station_selection.get()
    station_reference = next(s["stationReference"] for s in STATIONS if s["label"] == station)
    ea_region_name = EA_REGIONS.get(station_reference, "Unknown Region")
    
    data = fetch_station_data(station_reference)
    if data:
        latest_reading = data[0]
        latest_reading_text.set(f"Latest Reading: {latest_reading['value']}mm at {latest_reading['dateTime']}")
        
        station_info_text.set(f"Station Reference: {station_reference}\nEA Region: {ea_region_name}")
        
        readings_text.delete(1.0, tk.END)
        readings = [(r["value"], r["dateTime"]) for r in data[:10]]
        max_reading = max(readings, key=lambda x: x[0])
        min_reading = min((r for r in readings if r[0] > 0.0), key=lambda x: x[0])
        
        for value, time in readings:
            time_str = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M")
            if value == max_reading[0]:
                readings_text.insert(tk.END, f"Max: {value}mm at {time_str}\n", "max")
            elif value == min_reading[0]:
                readings_text.insert(tk.END, f"Min: {value}mm at {time_str}\n", "min")
            else:
                readings_text.insert(tk.END, f"{value}mm at {time_str}\n")
    else:
        latest_reading_text.set("Failed to retrieve data.")
        station_info_text.set("")
        readings_text.delete(1.0, tk.END)
        readings_text.insert(tk.END, "Failed to retrieve data.")

root = tk.Tk()
root.title("Informed Solutions")

station_selection = ttk.Combobox(root, values=[s["label"] for s in STATIONS])
station_selection.grid(row=0, column=0, padx=10, pady=10)
station_selection.bind("<<ComboboxSelected>>", update_station_data)

station_info_text = tk.StringVar()
station_info_label = tk.Label(root, textvariable=station_info_text)
station_info_label.grid(row=1, column=0, padx=10, pady=10)

latest_reading_text = tk.StringVar()
latest_reading_label = tk.Label(root, textvariable=latest_reading_text, font=("Times New Roman", 16, "bold"))
latest_reading_label.grid(row=2, column=0, padx=10, pady=10)

readings_text = tk.Text(root, height=10, width=40)
readings_text.grid(row=3, column=0, padx=10, pady=10)
readings_text.tag_configure("max", foreground="red")
readings_text.tag_configure("min", foreground="green")

root.mainloop()