# utils.py
import datetime
from dateutil.parser import parse as dateutil_parse
# from dateutil.relativedelta import relativedelta # Not used in the provided helper functions
import re

def get_current_day_for_teds():
    py_weekday = datetime.date.today().weekday() # Monday is 0 and Sunday is 6
    # Convert to a system where Sunday=0, Monday=1, ..., Saturday=6 if that was the original JS logic.
    # The provided Python logic seems to directly map Python's weekday():
    # Tuesday (1 in Python) -> 2 in some logic. Friday (4 in Python) -> 5 in some logic.
    # Let's assume the direct use of Python's weekday or a known mapping is intended.
    # Based on original code: if js_equivalent_day == 2 (Tuesday), if js_equivalent_day == 5 (Friday)
    # Python's weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    # So, Tuesday is py_weekday == 1. Friday is py_weekday == 4.
    if py_weekday == 1: return 2 # Tuesday mapping
    if py_weekday == 4: return 5 # Friday mapping
    # Fallback:
    # The original JS conversion was: js_equivalent_day = (py_weekday + 1) % 7
    # Mon (0) -> (0+1)%7 = 1
    # Tue (1) -> (1+1)%7 = 2
    # Fri (4) -> (4+1)%7 = 5
    # Sun (6) -> (6+1)%7 = 0
    # This mapping is consistent with the checks for 2 and 5.
    return (py_weekday + 1) % 7


def get_nth_day_of_week(year, month, week_num, day_of_week_py): # Mon=0..Sun=6
    first_day_of_month = datetime.date(year, month, 1)
    days_to_add = (day_of_week_py - first_day_of_month.weekday() + 7) % 7
    nth_day = first_day_of_month + datetime.timedelta(days=days_to_add + (week_num - 1) * 7)
    if nth_day.month == month:
        return nth_day
    return None

def get_last_day_of_week(year, month, day_of_week_py): # Mon=0..Sun=6
    if month == 12:
        last_day_of_month = datetime.date(year, month, 31)
    else:
        last_day_of_month = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    days_to_subtract = (last_day_of_month.weekday() - day_of_week_py + 7) % 7
    return last_day_of_month - datetime.timedelta(days=days_to_subtract)

def get_holiday_context(start_date_str, end_date_str):
    if not start_date_str or not end_date_str: return ""
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError: return ""

    holidays = [
        {'name': "New Year's Day", 'type': 'fixed', 'month': 1, 'day': 1},
        {'name': "Martin Luther King Jr. Day", 'type': 'nthDayOfWeek', 'month': 1, 'week': 3, 'dayOfWeek': 0}, # Monday
        {'name': "Valentine's Day", 'type': 'fixed', 'month': 2, 'day': 14},
        {'name': "Presidents' Day", 'type': 'nthDayOfWeek', 'month': 2, 'week': 3, 'dayOfWeek': 0}, # Monday
        {'name': "St. Patrick's Day", 'type': 'fixed', 'month': 3, 'day': 17},
        # Simplified Easter to a month range, as exact calculation is complex and region-dependent.
        {'name': "Easter Season", 'type': 'monthRange', 'startMonth': 3, 'endMonth': 4},
        {'name': "Memorial Day", 'type': 'lastDayOfWeek', 'month': 5, 'dayOfWeek': 0}, # Last Monday
        {'name': "Juneteenth", 'type': 'fixed', 'month': 6, 'day': 19},
        {'name': "Independence Day (4th of July)", 'type': 'fixed', 'month': 7, 'day': 4},
        {'name': "Labor Day", 'type': 'nthDayOfWeek', 'month': 9, 'week': 1, 'dayOfWeek': 0}, # First Monday
        {'name': "Indigenous Peoples' Day/Columbus Day", 'type': 'nthDayOfWeek', 'month': 10, 'week': 2, 'dayOfWeek': 0}, # Second Monday
        {'name': "Halloween", 'type': 'fixed', 'month': 10, 'day': 31},
        {'name': "Veterans Day", 'type': 'fixed', 'month': 11, 'day': 11},
        {'name': "Thanksgiving Day", 'type': 'nthDayOfWeek', 'month': 11, 'week': 4, 'dayOfWeek': 3}, # 4th Thursday
        {'name': "Christmas Day", 'type': 'fixed', 'month': 12, 'day': 25}
    ]
    current_d = start_date
    while current_d <= end_date:
        cY, cM, cDOM = current_d.year, current_d.month, current_d.day
        for h in holidays:
            if h['type'] == 'fixed' and h['month'] == cM and h['day'] == cDOM: return h['name']
            elif h['type'] == 'nthDayOfWeek':
                hd = get_nth_day_of_week(cY, h['month'], h['week'], h['dayOfWeek'])
                if hd and hd == current_d: return h['name']
            elif h['type'] == 'lastDayOfWeek':
                hd = get_last_day_of_week(cY, h['month'], h['dayOfWeek'])
                if hd and hd == current_d: return h['name']
            elif h['type'] == 'monthRange' and h['startMonth'] <= cM <= h['endMonth']:
                return h['name']
        current_d += datetime.timedelta(days=1)
    return ""

def format_date_string_for_caption_display(date_obj, lang="english", is_hasta_format=False, include_year=False):
    # Parameters 'lang' and 'is_hasta_format' are kept for interface compatibility 
    # but 'lang' is no longer used to determine M/D or D/M order for the primary date string.
    # 'is_hasta_format' is still implicitly used by the calling function 'format_dates_for_caption_context'
    # to decide if it's formatting a single end date or a range.
    if not date_obj: return ''
    
    day_str = f"{date_obj.day:02d}"
    month_str = f"{date_obj.month:02d}"
    year_suffix = ""

    if include_year:
        year_suffix = f"/{date_obj.year % 100:02d}"

    # Always return MM/DD format for the day-month part as per user request for consistency.
    return f"{month_str}/{day_str}{year_suffix}"


def format_dates_for_caption_context(start_str, end_str, date_format_pattern, lang):
    # 'lang' is passed to format_date_string_for_caption_display but won't alter MM/DD ordering there.
    # 'date_format_pattern' is used here to determine if it's a "Hasta" format, 
    # if the year should be included, and the separator for ranges.
    if not start_str or not end_str: return "DATES_MISSING"
    try:
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError: return "INVALID_DATES"

    is_hasta = date_format_pattern.lower().startswith("hasta")
    include_year = "yy" in date_format_pattern.lower() or "yyyy" in date_format_pattern.lower()

    if is_hasta:
        # For "Hasta" formats, only the end date is typically shown.
        # The format_date_string_for_caption_display will now always use MM/DD.
        return format_date_string_for_caption_display(end_date, lang, is_hasta_format=True, include_year=include_year)

    # For ranges like MM/DD-MM/DD or MM/DD - MM/DD
    # The format_date_string_for_caption_display will now always use MM/DD.
    start_formatted = format_date_string_for_caption_display(start_date, lang, is_hasta_format=False, include_year=include_year)
    end_formatted = format_date_string_for_caption_display(end_date, lang, is_hasta_format=False, include_year=include_year)
    
    separator = " - " if ' - ' in date_format_pattern else "-"
    return f"{start_formatted}{separator}{end_formatted}"


def get_final_price_string(price_format, price_value, custom_val):
    if price_format == "CUSTOM": return custom_val if custom_val else "[Custom Price]"
    if price_format == "X for $Y": return price_value if price_value else "[X for $Y Price]"
    if not price_value: return f"[Price Value] {price_format.split(' ',1)[1] if ' ' in price_format else ''}"
    
    price_value_str = str(price_value)

    if price_format == "¢ / lb.": return f"{price_value_str}¢ / lb."
    if price_format == "$ / lb.": return f"${price_value_str} / lb."
    if price_format == "$ each": return f"${price_value_str} each"
    if price_format == "¢ each": return f"{price_value_str}¢ each"
    return price_value_str 

def find_store_key_by_name(name_from_image, base_captions_data):
    if not name_from_image: return None
    norm_name = re.sub(r'[^A-Z0-9]', '', name_from_image.upper())
    for key, variants in base_captions_data.items():
        first_variant_key = list(variants.keys())[0]
        store_name_raw = variants[first_variant_key]['name'].split('(')[0].strip()
        norm_store_name = re.sub(r'[^A-Z0-9]', '', store_name_raw.upper())
        if norm_store_name in norm_name or norm_name in norm_store_name:
            if norm_store_name:
                return key
    return None

def try_parse_date_from_image_text(text_from_image):
    if not text_from_image or not isinstance(text_from_image, str): return None
    text_from_image = text_from_image.strip()
    current_year = datetime.date.today().year
    
    cleaned_text = text_from_image.replace('.', '/') 
    cleaned_text = re.sub(r'(?i)\b(ends|until|from|sale|starts|on|due|valido|expira|thru|through)\b\s*', '', cleaned_text).strip()
    cleaned_text = cleaned_text.replace(' ', '') 

    try:
        dt_obj = dateutil_parse(cleaned_text, dayfirst=False, default=datetime.datetime(current_year, 1, 1))
        
        original_had_year = re.search(r'\b(19\d{2}|20\d{2})\b', text_from_image)
        original_had_short_year = re.search(r'\b(\d{1,2}/\d{1,2}/)(\d{2})\b', text_from_image)

        if not original_had_year and not original_had_short_year and dt_obj.year != current_year:
            dt_obj = dt_obj.replace(year=current_year)
        elif original_had_year and (abs(dt_obj.year - current_year) > 5 or dt_obj.year == 1):
            try:
                dt_obj_fuzzy = dateutil_parse(cleaned_text, dayfirst=False, fuzzy=True, default=datetime.datetime(current_year, 1, 1))
                if abs(dt_obj_fuzzy.year - current_year) <= 5 : 
                    dt_obj = dt_obj_fuzzy
                else: 
                    return None
            except: 
                 return None 
        
        if dt_obj.year == 1 and not original_had_year and not original_had_short_year:
             dt_obj = dt_obj.replace(year=current_year)

        if not (current_year - 2 <= dt_obj.year <= current_year + 5): 
            if not original_had_year and not original_had_short_year:
                dt_obj = dt_obj.replace(year=current_year)
            elif original_had_year and not (current_year - 2 <= dt_obj.year <= current_year + 5) :
                 return None

        return dt_obj.strftime("%Y-%m-%d")
        
    except (ValueError, TypeError, OverflowError):
        patterns = [
            r"(\d{1,2})/(\d{1,2})/(\d{4})", 
            r"(\d{1,2})/(\d{1,2})/(\d{2})",  
            r"(\d{1,2})/(\d{1,2})"           
        ]
        for pattern in patterns:
            match = re.match(pattern, cleaned_text) 
            if match:
                parts = [int(p) for p in match.groups()]
                try:
                    if len(parts) == 3:
                        m, d, y_part = parts[0], parts[1], parts[2]
                        y = y_part if y_part > 1000 else (2000 + y_part if y_part < 70 else 1900 + y_part) 
                        if not (1 <= m <= 12 and 1 <= d <= 31): continue
                        return datetime.date(y, m, d).strftime("%Y-%m-%d")
                    elif len(parts) == 2:
                        m, d = parts[0], parts[1]
                        if not (1 <= m <= 12 and 1 <= d <= 31): continue
                        return datetime.date(current_year, m, d).strftime("%Y-%m-%d")
                except ValueError: continue 
    return None
