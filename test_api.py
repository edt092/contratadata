import requests, json

resp = requests.get(
    "https://www.datos.gov.co/resource/jbjy-vk9h.json",
    headers={"X-App-Token": "2YVTAs1AD7saHXHaCkf0esEYU", "Accept": "application/json"},
    params={
        "$select": "count(*)",
        "$where": "fecha_de_firma >= '2025-01-01'",
    },
    timeout=30,
)
print("Status:", resp.status_code)
print("Respuesta:", resp.json())
