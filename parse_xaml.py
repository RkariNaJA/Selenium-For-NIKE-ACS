# Reads UiPath .xaml automation files and prints out all the automation actions
import xml.etree.ElementTree as ET
import sys
import glob
import os
from dotenv import load_dotenv

load_dotenv()

def strip_ns(tag):
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def parse_element(el, level=0, max_depth=20):
    if level > max_depth: return
    tag = strip_ns(el.tag)
    
    display_name = el.get("DisplayName", "")
    text = el.get("Text", "")
    url = el.get("Url", "")
    
    info = []
    if display_name: info.append(f"Name='{display_name}'")
    if text: info.append(f"Text='{text}'")
    if url: info.append(f"Url='{url}'")
    
    # Try to find target attributes for UI Automation activities
    target_selector = ""
    for child in el:
        child_tag = strip_ns(child.tag)
        if child_tag == "Target":
            target_selector = child.get("Selector", "")
            if target_selector:
                info.append(f"Selector='{target_selector}'")
    
    if tag in ["InvokeWorkflowFile", "TypeInto", "Click", "OpenBrowser", "NavigateTo", "GetValue", "SelectItem", "SendHotkey"]:
        print("  " * level + f"-> {tag}: {', '.join(info)}")
        for attr, val in el.attrib.items():
            if attr in ["Text", "Url"] or "WorkflowFileName" in attr:
                print("  " * (level+1) + f"{attr}: {val}")

    for child in el:
        parse_element(child, level + 1, max_depth)

def parse_file(filepath):
    print(f"\n--- Parsing {os.path.basename(filepath)} ---")
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        parse_element(root)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")

folder = os.getenv("XAML_FOLDER", "")
if not folder:
    raise SystemExit(
        "Set XAML_FOLDER in .env to the folder holding the UiPath .xaml files "
        "(the path is machine-specific, so it is not committed)."
    )
files = ["Main.xaml", "ACS.xaml", "DownloadJsonSeason.xaml", "Main_Created.xaml", "Main_Modified.xaml"]

for f in files:
    full_path = os.path.join(folder, f)
    if os.path.exists(full_path):
        parse_file(full_path)
