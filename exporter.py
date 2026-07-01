import csv

def export_to_kml(coordinates_list, filename="mission_route.kml"):
    kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://opengis.net">
  <Document>
    <name>Agro-Telemetry Flight Path</name>
    <Style id="blueLine">
      <LineStyle>
        <color>ffff0000</color>
        <width>4</width>
      </LineStyle>
    </Style>
    <Placemark>
      <name>Survey Grid</name>
      <styleUrl>#blueLine</styleUrl>
      <LineString>
        <altitudeMode>relativeToGround</altitudeMode>
        <coordinates>
"""
    kml_footer = """        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""

    coordinate_strings = []
    for pt in coordinates_list:
        lon = pt.get('lon') or pt.get('longitude') or pt.get('Longitude')
        lat = pt.get('lat') or pt.get('latitude') or pt.get('Latitude')
        alt = pt.get('altitude') or pt.get('Altitude_M', 60)
        coordinate_strings.append(f"          {lon},{lat},{alt}")

    full_kml_content = kml_header + "\n".join(coordinate_strings) + kml_footer
    with open(filename, "w") as f:
        f.write(full_kml_content)
    return full_kml_content

def export_to_csv(coordinates_list, filename="mission_route.csv"):
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Latitude', 'Longitude', 'Altitude_M'])
        for pt in coordinates_list:
            lat = pt.get('lat') or pt.get('latitude') or pt.get('Latitude')
            lon = pt.get('lon') or pt.get('longitude') or pt.get('Longitude')
            alt = pt.get('altitude') or pt.get('Altitude_M', 60)
            writer.writerow([lat, lon, alt])
