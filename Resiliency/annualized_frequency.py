import pandas as pd 
import json
import pdb

hazard_file = "Resiliency/NRI_Table_Counties/NRI_Table_Counties.csv"
graphic_file = "ECA/graphic.csv"

hazard_df = pd.read_csv(hazard_file)
graphic_df = pd.read_csv(graphic_file)

# find all the valid county codes inside the graphic csv and track index 
county_codes = list(graphic_df['GEO_ID'])
county_codes = [code[-5:] for code in county_codes]
# county_codes = set(county_codes)


AF_list = []
for index, row in hazard_df.iterrows():
    if row["NRI_ID"][1:] not in county_codes:
        continue

    graphic_index = county_codes.index(row["NRI_ID"][1:])

    # codes:
    # coastal flooding - CFLD_AFREQ
    # earthquake - ERQK_AFREQ
    # hail - HAIL_AFREQ
    # hurricane - HRCN_AFREQ
    # ice storm - ISTM_AFREQ
    # lightning - LTNG_AFREQ
    # strong wind - SWND_AFREQ
    # tornado - TRND_AFREQ
    # pdb.set_trace()
    coastal_flooding = row["CFLD_AFREQ"] if str(row["CFLD_AFREQ"]) != 'nan' else 0
    
    frequency_dict = {
        "graphic_index": graphic_index, 
        "county": row["COUNTY"],
        "county_type": row["COUNTYTYPE"] if str(row["COUNTYTYPE"]) != 'nan' else 'None',
        "coastal_flooding": row["CFLD_AFREQ"] if str(row["CFLD_AFREQ"]) != 'nan' else 0,
        "earthquake": row["ERQK_AFREQ"] if str(row["ERQK_AFREQ"]) != 'nan' else 0,
        "hail": row["HAIL_AFREQ"] if str(row["HAIL_AFREQ"]) != 'nan' else 0,
        "hurricane": row["HRCN_AFREQ"] if str(row["HRCN_AFREQ"]) != 'nan' else 0, 
        "ice_storm": row["ISTM_AFREQ"] if str(row["ISTM_AFREQ"]) != 'nan' else 0, 
        "lightning": row["LTNG_AFREQ"] if str(row["LTNG_AFREQ"]) != 'nan' else 0, 
        "strong_wind": row["SWND_AFREQ"] if str(row["SWND_AFREQ"]) != 'nan' else 0,
        "tornado": row["TRND_AFREQ"] if str(row["TRND_AFREQ"]) != 'nan' else 0,
    }
    AF_list.append(frequency_dict)

sorted_AF_list = sorted(AF_list, key=lambda x : x["graphic_index"])

print(len(AF_list))
# Write data to the JSON file
file_path = "Resiliency/annual_frequencies.json"
with open(file_path, 'w') as json_file:
    json.dump(sorted_AF_list, json_file, indent=4)
