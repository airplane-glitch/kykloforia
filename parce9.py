import os
import xml.etree.ElementTree as ET
from tkinter import Tk, filedialog

def parse_log_files(log_directory, output_txt, bad_data_txt):
    required_fields = ["Timestamp", "VIN or ID", "Latitude", "Longitude", "Altitude"]
    known_fields = [
        "Primary Partition", "Secondary Partition", "Timestamp", "VIN or ID", "Latitude", "Longitude", "Altitude",
        "Tail/Call Sign", "Aircraft Type"
    ]

    total_rows = 0
    ignored_rows = 0

    log_files = sorted([f for f in os.listdir(log_directory) if
                        f.startswith("messages.log") or f.endswith(('.log', '.log1', '.log2'))])

    if not log_files:
        print("No log files found in the specified directory.")
        return

    with open(output_txt, "w", encoding="utf-8") as txt_file, open(bad_data_txt, "w", encoding="utf-8") as bad_file:
        for log_file in log_files:
            log_path = os.path.join(log_directory, log_file)
            print(f"Processing file: {log_file}")
            with open(log_path, "r", encoding="utf-8") as file:
                for line in file:
                    try:
                        if line.strip():
                            root = ET.fromstring(line)
                            src = root.findtext("src", "")  # Primary Partition
                            for record in root.findall(".//record"):
                                track = record.find(".//track")
                                flight_plan = record.find(".//flightPlan")

                                entry = {
                                    "Primary Partition": src,
                                    "Secondary Partition": "",
                                    "Timestamp": track.findtext("mrtTime", "") if track is not None else "",
                                    "VIN or ID": track.findtext("trackNum", "") if track is not None else "",
                                    "Latitude": track.findtext("lat", "") if track is not None else "",
                                    "Longitude": track.findtext("lon", "") if track is not None else "",
                                    "Altitude": track.findtext("reportedAltitude", "") if track is not None else "",
                                    "Tail/Call Sign": flight_plan.findtext("acid", "") if flight_plan is not None else "",
                                    "Aircraft Type": flight_plan.findtext("acType", "") if flight_plan is not None else "",
                                }

                                total_rows += 1

                                row = ",".join(str(entry.get(field, "")) for field in known_fields)
                                if any(entry[field] == "" for field in required_fields):
                                    bad_file.write(row + "\n")
                                    ignored_rows += 1
                                else:
                                    txt_file.write(row + "\n")
                    except ET.ParseError:
                        print(f"Skipping invalid XML line in {log_file}.")

        # Write summary to bad data file
        bad_file.seek(0, 0)
        bad_file.write(f"Ignored Rows: {ignored_rows}\n")
        bad_file.write(f"Valid Rows: {total_rows - ignored_rows}\n\n")

    print(f"Valid data exported to {output_txt}")
    print(f"Bad data saved in {bad_data_txt}")

def main():
    root = Tk()
    root.withdraw()
    print("Select the directory where the log files are located:")
    log_directory = filedialog.askdirectory(title="Select Log Directory")
    if not log_directory:
        print("No directory selected. Exiting.")
        return

    print("Select destination for valid output TXT file:")
    output_txt = filedialog.asksaveasfilename(
        title="Select Destination for Valid Data",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not output_txt:
        print("No output file selected. Exiting.")
        return

    print("Select destination for bad data TXT file:")
    bad_data_txt = filedialog.asksaveasfilename(
        title="Select Destination for Bad Data",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not bad_data_txt:
        print("No bad data file selected. Exiting.")
        return

    parse_log_files(log_directory, output_txt, bad_data_txt)

if __name__ == "__main__":
    main()
