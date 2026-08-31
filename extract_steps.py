# Reads UiPath .xaml files and writes all the automation steps into an output.txt file, extracting display names, text, URLs, and workflow references
import re
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def extract_steps(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open("output.txt", "a", encoding="utf-8") as out:
        out.write(f"\n=== {os.path.basename(filepath)} ===\n")
        
        tags = re.findall(r'<[a-zA-Z0-9:]+[^>]*>', content)
        for tag in tags:
            if any(x in tag for x in ['NTypeInto', 'NClick', 'NGoToUrl', 'NOpenBrowser', 'InvokeWorkflowFile', 'NGetValue', 'NKeyboardShortcut', 'ui:TypeInto', 'ui:Click', 'ui:OpenBrowser', 'ui:NavigateTo']):
                if tag.startswith('</'): continue
                
                name = re.search(r'DisplayName="([^"]+)"', tag)
                name_str = name.group(1) if name else ""
                
                text = re.search(r'Text="([^"]+)"', tag)
                text_str = f" [Text: {text.group(1)}]" if text else ""
                
                url = re.search(r'Url="([^"]+)"', tag)
                url_str = f" [Url: {url.group(1)}]" if url else ""
                
                wf = re.search(r'WorkflowFileName="([^"]+)"', tag)
                wf_str = f" [Workflow: {wf.group(1)}]" if wf else ""
                
                tag_name = tag.split()[0].replace('<', '')
                
                if name_str or wf_str or url_str:
                    out.write(f"{tag_name}: {name_str}{text_str}{url_str}{wf_str}\n")


if os.path.exists("output.txt"):
    os.remove("output.txt")

folder = os.getenv("XAML_FOLDER", "")
if not folder:
    raise SystemExit(
        "Set XAML_FOLDER in .env to the folder holding the UiPath .xaml files "
        "(the path is machine-specific, so it is not committed)."
    )
files = ["Main.xaml", "Main_Modified.xaml", "Main_Created.xaml", "ACS.xaml", "DownloadJsonSeason.xaml"]
for f in files:
    path = os.path.join(folder, f)
    if os.path.exists(path):
        extract_steps(path)
