
SP_POIs = ["North Pad & Ferrari",
           "The Wall",
           "Zeus Station",
           "Lightning Rod",
           "Storm Catcher",

           "Ceto Station",
           "Command Center",
           "Cascade Falls",
           "Checkpoint",
           "Downed Beast",

           "The Mill",
           "CON Pylon | Cave & Bean",
           "Cenote Cave",
           "Barometer",
           "Coastal Camp",

           "Echo HQ",
           "Devastated Coast",
           "Launch Pad",
           "CON Pylon | Cave & Bean",
           "Jurassic & Mountain Lift"]

SP_POIs_SHORT = {
    "North Pad & Ferrari": "North Pad",
    "The Wall": "Wall",
    "Zeus Station": "Zeus Station",
    "Lightning Rod": "Lightning Rod",
    "Storm Catcher": "Storm Catcher",
    "Ceto Station": "Ceto Station",
    "Command Center": "Command",
    "Cascade Falls": "Cascades",
    "Checkpoint": "Checkpoint",
    "Downed Beast": "Downed Beast",
    "The Mill": "Mill",
    "CON Pylon | Cave & Bean": "CON Pylon | Bean",
    "Cenote Cave": "Cenote Cave",
    "Barometer": "Barometer",
    "Coastal Camp": "Coastal Camp",
    "Echo HQ": "Echo HQ",
    "Devastated Coast": "Devastated Coast",
    "Launch Pad": "Launch Pad",
    "Jurassic & Mountain Lift": "Jurassic/Lift"
}

WE_POIs = ["Skyhook West & Trials",
            "Skyhook East & Tunnel",
            "Survey Camp & Epicenter",
            "Climatizer",
            "Overlook",

            "CON Siphon | Fragment",
            "Monument",
            "Countdown",
            "Lava Fissure & Mirage",
            "Staging",

            "Landslide",
            "Thermal Station",
            "The Tree",
            "Harvester",
            "CON Siphon | Fragment",

            "Launch Site",
            "The Dome",
            "Stacks",
            "Big Maude",
            "The Geyser"]

WE_POIs_SHORT = {
    "Skyhook West & Trials": "Skyhook West",
    "Skyhook East & Tunnel": "Skyhook East",
    "Survey Camp & Epicenter": "Survey/Epicenter",
    "Climatizer": "Climatizer",
    "Overlook": "Overlook",
    "CON Siphon | Fragment": "CON Siphon | Frag",
    "Monument": "Monument",
    "Countdown": "Countdown", 
    "Lava Fissure & Mirage": "Fissure/Mirage",
    "Staging": "Staging",
    "Landslide": "Landslide",
    "Thermal Station": "Thermal",
    "The Tree": "The Tree",
    "Harvester": "Harvester",
    "Launch Site": "Launch Site",
    "The Dome": "Dome",
    "Stacks": "Stacks",
    "Big Maude": "Maude",
    "The Geyser": "Geyser"
}

ED_POIs = [
    "Resort",
    "CON The Lotus | Riverside",
    "Electro Dam",
    "Heights",
    "Galleria",

    "City Hall",
    "Boardwalk",
    "Blossom Drive",
    "CON Neon Square | Angels Atrium", 
    "CON Energy Bank | Slums", # Heights-Energy | BusStop

    "Stadium",
    "Humbert Labs",
    "Old Town",
    "Draft Point",
    "Shipyard Arcade",
    
    "Viaduct",
    "Street Market",
    "CON The Lotus | Riverside", # Lotus-Energy | Canal
    "CON Neon Square | Angels Atrium", 
    "CON Energy Bank | Slums" # Heights-Energy | BusStop
]

ED_POIs_SHORT = {
    "Resort": "Resort",
    "CON The Lotus | Riverside": "CON Lotus | Riverside",
    "Electro Dam": "Electro Dam",
    "Heights": "Heights",
    "Galleria": "Galleria",
    "City Hall": "City Hall",
    "Boardwalk": "Boardwalk",
    "Blossom Drive": "Blossom Drive",
    "CON Neon Square | Angels Atrium": "CON Neon | Angels Atrium",
    "CON Energy Bank | Slums": "CON Energy | Slums",

    "Stadium": "Stadium",
    "Humbert Labs": "Humbert Labs",
    "Old Town": "Old Town",
    "Draft Point": "Draft Point",
    "Shipyard Arcade": "Shipyard Arcade",
    "Viaduct": "Viaduct",
    "Street Market": "Street Market"
}


KC_POIs = ["Crash Site",
            "Artillery",
            "Spotted Lake & Lake House",
            "Runoff & Gold House",
            "Containment & Cascades",

            "Basin",
            "The Rig & Cable Susp.",
            "Capacitor",
            "Labs",
            "Swamps",

            "Cage & Forest",
            "Hydro",
            "Repulsor",
            "Map Room",
            "Caustic Treatment",

            "Market",
            "Relic",
            "Gauntlet",
            "Airbase",
            "Bunker & High Desert"]

OL_POIs = ["Docks",
           "Power Grid",
           "Rift",
           "Fight Night",
           "Carrier",
           
           "Oasis",
           "Turbine",
           "Hammond Labs",
           "Estates & Power Station",
           "Hydro & Elysium",

           "Phase Driver",
           "Terminal",
           "Bonsai",
           "Solar Array",
           "Icarus",

           "Orbital Cannon",
           "Grow Towers",
           "Clinic & Outskirts",
           "Gardens",
           "Energy Depot"]


class Overstat:
    # Overstat POIs

    SP_POIs = {'North Pad': ['North Pad', 'Ferrari'],
          'The Wall': ['Wall'],
          'Zeus Station': ['Zeus Station'],
          'Lightning Rod': ['Lightning Rod', 'Thunder'],
          'Storm Catcher': ['Storm Catcher', 'Cliffside'],
          'Ceto Station': ['Ceto Station'],
          'Command Center': ['Command'],
          'Cascade Falls': ['Cascade Falls'],
          'Checkpoint': ['Checkpoint'],
          'Downed Beast': ['Downed Beast'],
          'The Mill': ['Mills'],
          'God Cave & Bean': ['God Cave', 'Bean'],
          'Cenote Cave': ['Cenote'],
          'Barometer': ['Barometer'],
          'Coastal Camp': ['Coastal Camp'],
          'Echo HQ': ['Echo MD'],
          'Devastated Coast': ['Devastated Coast'],
          'Launch Pad': ['Launch Pad'],
          'The Pylon': ['The Pylon'],
          'Jurassic': ['Jurassic', 'Mountain Lift']}

    WE_POIs = {'Skyhook West & Trials': ['Trials', 'Sky West'],
               'Skyhook East & Tunnel': ['Sky East', 'Tunnel'],
               'Survey Camp & Epicenter': ['EpiCenter', 'Survey'],
               'Climatizer': ['Climatizer'],
               'Overlook': ['Overlook'],
               'Fragment & Noname': ['Fragment', 'No Name'],
               'Monument': ['Monument'],
               'Countdown': ['Countdown'],
               'Lava Fissure': ['Fissure'],
               'Staging': ['Staging'],
               'Mirage & Landslide': ['Mirage', 'Landslide'],
               'Thermal Station': ['Thermal'],
               'The Tree': ['Tree'],
               'Harvester': ['Harvester'],
               'Lava Siphon': ['Siphon'],
               'Launch Site': ['Launch Site'],
               'The Dome': ['Dome'],
               'Stacks': ['Stacks'],
               'Big Maude': ['Maude'],
               'The Geyser': ['Geyser']}



# KC_POIs = [["Crash Site"],
#            ["Artillery"],
#            ["Spotted Lake", "Lake House"],
#            ["Runoff", "Gold House"], # "The Pit"
#            ["Containment", "N. 82", "Cascades"],
#            ["Basin"],
#            ["The Rig", "Cable Susp."],
#            ["Capacitor"],
#            ["Labs"],
#            ["Swamps"],
#            ["Cage", "Forest", "Fallen Bridge"],
#            ["Hyrdo"],
#            ["Repulsor"],
#            ["Map Room"],
#            ["Caustic Treatment", "F", "E"],
#            ["Market", "B", "C"],
#            ["Relic"],
#            ["Gauntlet", "A"], # Replace with ["Hillside", "Two Splines"]
#            ["Airbase"], # Add ["Gauntlet", "A"]
#            ["Bunker", "High Desert", "River"]]

# OL_POIs = [["Docks"],
#            ["Power Grid"],
#            ["Rift"],
#            ["Fight Night"],
#            ["Carrier"],
#            ["Oasis"],
#            ["Turbine"],
#            ["Hammond Labs"],
#            ["Estates", "Power Station"],
#            ["Hydro", "Elysium"],
#            ["Phase Driver"],
#            ["Terminal"],
#            ["Bonsai"],
#            ["Solar Array"],
#            ["Icarus"],
#            ["Orbital Cannon"],
#            ["Grow Towers"],
#            ["Clinic", "Outskirts"],
#            ["Gardens"],
#            ["Energy Depot"]]

# BM_POIs = [["Breaker Wharf"],
#            ["Breaker Wharf"],
#            ["Dry Gulch"],
#            ["Production Yard"],
#            ["The Foundry"],
#            ["The Foundry"],
#            ["Cultivation"],
#            ["S. Promenade"],
#            ["Core"],
#            ["Core"],
#            ["N. Promenade"],
#            ["Stasis Array"],
#            ["Alpha Base"],
#            ["Backup Atmo"],
#            ["Eternal Gardens"],
#            ["The Divide"],
#            ["Bionomics"],
#            ["Atmostation"],
#            ["Terraformer"],
#            ["Terraformer"]]