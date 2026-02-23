"""
api_tools.py — All external API tools for Sahaba Islamic Assistant.

Each function is a LangChain @tool that logs its call and response to terminal.

Covers:
  - Quran (api.alquran.cloud)
  - Prayer times (api.aladhan.com)
  - Islamic calendar (api.aladhan.com)
  - Qibla direction (api.aladhan.com)
  - Geocoding (nominatim.openstreetmap.org)
"""

import json
import requests
from langchain_core.tools import tool
from config import (
    QURAN_API_BASE,
    ALADHAN_API_BASE,
    GEOCODING_API_BASE,
    GEOCODING_USER_AGENT,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _log_api(name: str, url: str, response_summary: str) -> None:
    print(f"\n[API CALL] {name}")
    print(f"  URL: {url}")
    print(f"  Response: {response_summary[:300]}")


def _get(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ══════════════════════════════════════════════════════════════════════════════
# QURAN TOOLS
# ══════════════════════════════════════════════════════════════════════════════

@tool
def get_ayah_english(surah: int, ayah: int) -> str:
    """Get the English translation (Asad) of a specific Quran verse (ayah).
    
    Args:
        surah: Surah number (1–114)
        ayah: Ayah number within the surah
    """
    url = f"{QURAN_API_BASE}/ayah/{surah}:{ayah}/en.asad"
    data = _get(url)
    _log_api("get_ayah_english", url, json.dumps(data.get("data", {})))
    d = data.get("data", {})
    return (
        f"Surah {d.get('surah', {}).get('englishName', '')} ({surah}:{ayah})\n"
        f"Translation: {d.get('text', 'N/A')}"
    )


@tool
def get_surah_english(surah: int) -> str:
    """Get the English translation (Asad) of an entire Quran surah.
    
    Args:
        surah: Surah number (1–114)
    """
    url = f"{QURAN_API_BASE}/surah/{surah}/en.asad"
    data = _get(url)
    _log_api("get_surah_english", url, json.dumps(data.get("data", {}).get("name", "")))
    d = data.get("data", {})
    ayahs = d.get("ayahs", [])
    lines = [f"Surah {d.get('englishName', '')} ({d.get('name', '')})\n"]
    for a in ayahs:
        lines.append(f"[{a['numberInSurah']}] {a['text']}")
    return "\n".join(lines)


@tool
def get_ayah_arabic(surah: int, ayah: int) -> str:
    """Get the Arabic text (Uthmani script) of a specific Quran verse (ayah).
    
    Args:
        surah: Surah number (1–114)
        ayah: Ayah number within the surah
    """
    url = f"{QURAN_API_BASE}/ayah/{surah}:{ayah}/quran-uthmani"
    data = _get(url)
    _log_api("get_ayah_arabic", url, json.dumps(data.get("data", {})))
    d = data.get("data", {})
    return (
        f"Surah {d.get('surah', {}).get('englishName', '')} ({surah}:{ayah}) — Arabic:\n"
        f"**{d.get('text', 'N/A')}**"
    )


@tool
def get_surah_arabic(surah: int) -> str:
    """Get the Arabic text (Uthmani script) of an entire Quran surah.
    
    Args:
        surah: Surah number (1–114)
    """
    url = f"{QURAN_API_BASE}/surah/{surah}/quran-uthmani"
    data = _get(url)
    _log_api("get_surah_arabic", url, json.dumps(data.get("data", {}).get("name", "")))
    d = data.get("data", {})
    ayahs = d.get("ayahs", [])
    lines = [f"Surah {d.get('englishName', '')} ({d.get('name', '')}) — Arabic:\n"]
    for a in ayahs:
        lines.append(f"**[{a['numberInSurah']}] {a['text']}**")
    return "\n".join(lines)


@tool
def search_quran(query: str) -> str:
    """Search the Quran (English translation) for a keyword or phrase.
    
    Args:
        query: The search term or phrase to look up
    """
    url = f"{QURAN_API_BASE}/search/{query}/all/en.asad"
    data = _get(url)
    _log_api("search_quran", url, f"count={data.get('data', {}).get('count', 0)}")
    matches = data.get("data", {}).get("matches", [])
    if not matches:
        return f"No Quran results found for: '{query}'"
    out = [f"Quran search results for '{query}' ({len(matches)} found):\n"]
    for m in matches[:10]:  # cap at 10 results
        surah_name = m.get("surah", {}).get("englishName", "")
        num = m.get("surah", {}).get("number", "")
        ain = m.get("numberInSurah", "")
        out.append(f"• ({num}:{ain}) {surah_name}: {m.get('text', '')}")
    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════════
# PRAYER TIMES TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def _format_timings(timings: dict) -> str:
    keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Sunset", "Maghrib", "Isha", "Midnight"]
    rows = ["| Prayer | Time |", "|--------|------|"]
    for k in keys:
        if k in timings:
            rows.append(f"| {k} | {timings[k]} |")
    return "\n".join(rows)


@tool
def get_prayer_times(date: str, latitude: float, longitude: float) -> str:
    """Get Islamic prayer times for a specific date and location.
    
    Args:
        date: Date in DD-MM-YYYY format (e.g. '19-02-2026')
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{ALADHAN_API_BASE}/timings/{date}"
    params = {"latitude": latitude, "longitude": longitude}
    data = _get(url, params=params)
    _log_api("get_prayer_times", url, json.dumps(params))
    d = data.get("data", {})
    timings = d.get("timings", {})
    date_info = d.get("date", {}).get("readable", date)
    hijri = d.get("date", {}).get("hijri", {})
    hijri_str = f"{hijri.get('day')} {hijri.get('month', {}).get('en', '')} {hijri.get('year')} AH"
    return (
        f"Prayer Times for {date_info} ({hijri_str})\n"
        f"Location: ({latitude}, {longitude})\n\n"
        + _format_timings(timings)
    )


@tool
def get_next_prayer(date: str, latitude: float, longitude: float) -> str:
    """Get the next upcoming prayer for a given date and location.
    
    Args:
        date: Date in DD-MM-YYYY format (e.g. '19-02-2026')
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{ALADHAN_API_BASE}/nextPrayer/{date}"
    params = {"latitude": latitude, "longitude": longitude}
    data = _get(url, params=params)
    _log_api("get_next_prayer", url, json.dumps(params))
    d = data.get("data", {})
    timings = d.get("timings", {})
    return (
        f"Next Prayer at ({latitude}, {longitude}) on {date}:\n"
        + _format_timings(timings)
    )


@tool
def get_prayer_times_hijri_month(
    hijri_year: int, hijri_month: int, latitude: float, longitude: float
) -> str:
    """Get prayer times for an entire Hijri calendar month.
    
    Args:
        hijri_year: Hijri year (e.g. 1447)
        hijri_month: Hijri month number (1–12)
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{ALADHAN_API_BASE}/hijriCalendar/{hijri_year}/{hijri_month}"
    params = {"latitude": latitude, "longitude": longitude}
    data = _get(url, params=params)
    _log_api("get_prayer_times_hijri_month", url, json.dumps(params))
    days = data.get("data", [])
    lines = [f"Prayer times for Hijri {hijri_month}/{hijri_year} at ({latitude}, {longitude}):\n"]
    for day in days[:5]:  # show first 5 days as sample
        date_str = day.get("date", {}).get("readable", "")
        fajr = day.get("timings", {}).get("Fajr", "")
        maghrib = day.get("timings", {}).get("Maghrib", "")
        lines.append(f"• {date_str}: Fajr {fajr}, Maghrib {maghrib}")
    if len(days) > 5:
        lines.append(f"... and {len(days) - 5} more days.")
    return "\n".join(lines)


@tool
def get_prayer_times_gregorian_month(
    year: int, month: int, latitude: float, longitude: float
) -> str:
    """Get prayer times for an entire Gregorian calendar month.
    
    Args:
        year: Gregorian year (e.g. 2026)
        month: Gregorian month number (1–12)
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{ALADHAN_API_BASE}/calendar/{year}/{month}"
    params = {"latitude": latitude, "longitude": longitude}
    data = _get(url, params=params)
    _log_api("get_prayer_times_gregorian_month", url, json.dumps(params))
    days = data.get("data", [])
    lines = [f"Prayer times for {month}/{year} at ({latitude}, {longitude}):\n"]
    for day in days[:5]:  # show first 5 days as sample
        date_str = day.get("date", {}).get("readable", "")
        fajr = day.get("timings", {}).get("Fajr", "")
        maghrib = day.get("timings", {}).get("Maghrib", "")
        lines.append(f"• {date_str}: Fajr {fajr}, Maghrib {maghrib}")
    if len(days) > 5:
        lines.append(f"... and {len(days) - 5} more days.")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# ISLAMIC CALENDAR TOOLS
# ══════════════════════════════════════════════════════════════════════════════

@tool
def gregorian_to_hijri(date: str) -> str:
    """Convert a Gregorian date to its Hijri (Islamic) equivalent.
    
    Args:
        date: Gregorian date in DD-MM-YYYY format (e.g. '19-02-2026')
    """
    url = f"{ALADHAN_API_BASE}/gToH/{date}"
    data = _get(url)
    _log_api("gregorian_to_hijri", url, json.dumps(data.get("data", {})))
    d = data.get("data", {}).get("hijri", {})
    return (
        f"Gregorian {date} → Hijri:\n"
        f"{d.get('day')} {d.get('month', {}).get('en', '')} {d.get('year')} AH\n"
        f"({d.get('month', {}).get('ar', '')})"
    )


@tool
def hijri_to_gregorian(date: str) -> str:
    """Convert a Hijri (Islamic) date to its Gregorian equivalent.
    
    Args:
        date: Hijri date in DD-MM-YYYY format (e.g. '19-08-1447')
    """
    url = f"{ALADHAN_API_BASE}/hToG/{date}"
    data = _get(url)
    _log_api("hijri_to_gregorian", url, json.dumps(data.get("data", {})))
    d = data.get("data", {}).get("gregorian", {})
    return (
        f"Hijri {date} → Gregorian:\n"
        f"{d.get('day')} {d.get('month', {}).get('en', '')} {d.get('year')}"
    )


@tool
def hijri_calendar_for_gregorian_month(month: int, year: int) -> str:
    """Get the Hijri calendar dates for an entire Gregorian month.
    
    Args:
        month: Gregorian month number (1–12)
        year: Gregorian year (e.g. 2026)
    """
    url = f"{ALADHAN_API_BASE}/gToHCalendar/{month}/{year}"
    data = _get(url)
    _log_api("hijri_calendar_for_gregorian_month", url, f"month={month}, year={year}")
    days = data.get("data", [])
    lines = [f"Hijri dates for Gregorian {month}/{year}:\n"]
    for day in days[:10]:
        greg = day.get("gregorian", {})
        hijri = day.get("hijri", {})
        lines.append(
            f"• {greg.get('day')} {greg.get('month', {}).get('en', '')} {greg.get('year')} "
            f"= {hijri.get('day')} {hijri.get('month', {}).get('en', '')} {hijri.get('year')} AH"
        )
    if len(days) > 10:
        lines.append(f"... and {len(days) - 10} more days.")
    return "\n".join(lines)


@tool
def gregorian_calendar_for_hijri_month(hijri_month: int, hijri_year: int) -> str:
    """Get the Gregorian calendar dates for an entire Hijri month.
    
    Args:
        hijri_month: Hijri month number (1–12)
        hijri_year: Hijri year (e.g. 1447)
    """
    url = f"{ALADHAN_API_BASE}/hToGCalendar/{hijri_month}/{hijri_year}"
    data = _get(url)
    _log_api("gregorian_calendar_for_hijri_month", url, f"hijri_month={hijri_month}, hijri_year={hijri_year}")
    days = data.get("data", [])
    lines = [f"Gregorian dates for Hijri {hijri_month}/{hijri_year}:\n"]
    for day in days[:10]:
        greg = day.get("gregorian", {})
        hijri = day.get("hijri", {})
        lines.append(
            f"• {hijri.get('day')} {hijri.get('month', {}).get('en', '')} {hijri.get('year')} AH "
            f"= {greg.get('day')} {greg.get('month', {}).get('en', '')} {greg.get('year')}"
        )
    if len(days) > 10:
        lines.append(f"... and {len(days) - 10} more days.")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# QIBLA TOOLS
# ══════════════════════════════════════════════════════════════════════════════

@tool
def get_qibla_direction(latitude: float, longitude: float) -> str:
    """Get the Qibla direction (compass bearing in degrees) from a location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{ALADHAN_API_BASE}/qibla/{latitude}/{longitude}"
    data = _get(url)
    _log_api("get_qibla_direction", url, json.dumps(data.get("data", {})))
    d = data.get("data", {})
    direction = d.get("direction", "N/A")
    return (
        f"Qibla Direction from ({latitude}, {longitude}):\n"
        f"Bearing: {direction:.2f}°\n"
        f"(0° = North, 90° = East, 180° = South, 270° = West)"
    )


@tool
def get_qibla_compass_image_url(latitude: float, longitude: float) -> str:
    """Get the URL of a Qibla compass image for a given location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{ALADHAN_API_BASE}/qibla/{latitude}/{longitude}/compass"
    _log_api("get_qibla_compass_image_url", url, f"lat={latitude}, lon={longitude}")
    return f"QIBLA_COMPASS_IMAGE:{url}"


# ══════════════════════════════════════════════════════════════════════════════
# GEOCODING TOOL
# ══════════════════════════════════════════════════════════════════════════════

@tool
def geocode_address(address: str) -> str:
    """Convert a location name or address to latitude and longitude coordinates.
    
    Args:
        address: Location name or address (e.g. 'Cambridge, UK' or 'London, England')
    """
    params = {"q": address, "format": "jsonv2", "limit": 1}
    headers = {"User-Agent": GEOCODING_USER_AGENT}
    data = _get(GEOCODING_API_BASE, params=params, headers=headers)
    _log_api("geocode_address", GEOCODING_API_BASE, f"address={address}")
    if not data:
        return f"Could not geocode address: '{address}'"
    result = data[0]
    lat = float(result.get("lat", 0))
    lon = float(result.get("lon", 0))
    display = result.get("display_name", address)
    return f"Location: {display}\nLatitude: {lat}\nLongitude: {lon}"


# ─── Tool Registry ────────────────────────────────────────────────────────────

ALL_TOOLS = [
    get_ayah_english,
    get_surah_english,
    get_ayah_arabic,
    get_surah_arabic,
    search_quran,
    get_prayer_times,
    get_next_prayer,
    get_prayer_times_hijri_month,
    get_prayer_times_gregorian_month,
    gregorian_to_hijri,
    hijri_to_gregorian,
    hijri_calendar_for_gregorian_month,
    gregorian_calendar_for_hijri_month,
    get_qibla_direction,
    get_qibla_compass_image_url,
    geocode_address,
]
