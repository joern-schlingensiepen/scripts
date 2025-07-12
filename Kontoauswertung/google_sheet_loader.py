import pygsheets
import pandas as pd
import re
import os
from collections import Counter
from datetime import datetime

class GoogleSheetLoader:
    def __init__(self, url, client_secret_path=None):
        if client_secret_path is None:
            client_secret_path = os.path.expanduser('~/Documents/google_client_secret.json')
        print(f"Lade Google Sheet von {url} mit Client Secret {client_secret_path}")
        self.gc = pygsheets.authorize(service_file=client_secret_path)
        self.sh = self.gc.open_by_url(url)
        self.locale = self.sh.locale
        if self.locale.startswith('de'):
            self.decimal_sep = ','
            self.thousand_sep = '.'
            self.date_formats = ['%d.%m.%Y', '%d.%m.%y']
        else:
            self.decimal_sep = '.'
            self.thousand_sep = ','
            self.date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']

    def get_tab_names(self):
        return [wks.title for wks in self.sh.worksheets()]

    def get_tab_as_df(self, tab_name):
        wks = self.sh.worksheet_by_title(tab_name)
        df = wks.get_as_df(has_header=True)
        return self._parse_dataframe(df)

    def _extract_number_and_unit(self, value):
        if not isinstance(value, str):
            return value, None
        value = value.strip()
        # Erkenne Werte wie .5$, 0.5$, 1.234,55 €, 1,234.55 EUR, 1.234,44 qm, 5,00%
        # Optional führende Null vor dem Komma/Punkt
        match = re.match(r'^([+-]?\d*[\.,]?\d+)\s*([\w€%$]*)$', value)
        if match:
            num, unit = match.groups()
            num = num.replace(self.thousand_sep, '')
            num = num.replace(self.decimal_sep, '.')
            try:
                return float(num), unit if unit else None
            except ValueError:
                return value, None
        # Wenn der Wert nicht mit einer Zahl beginnt, ist es keine Zahl mit Einheit
        return value, None

    def _parse_date(self, value):
        for fmt in self.date_formats:
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        return value

    def _parse_dataframe(self, df):
        for col in df.columns:
            units = []
            numbers = []
            is_date = []
            for val in df[col]:
                if val is None or (isinstance(val, str) and val.strip() == ""):
                    continue
                # Versuche Datums-Parsing
                if isinstance(val, str):
                    date_val = self._parse_date(val)
                    if isinstance(date_val, datetime):
                        is_date.append(True)
                        numbers.append(date_val)
                        units.append(None)
                        continue
                # Versuche Zahl + Einheit
                num, unit = self._extract_number_and_unit(str(val))
                numbers.append(num)
                # Nur Einheit merken, wenn num wirklich float oder int ist
                if isinstance(num, (float, int)):
                    units.append(unit)
                else:
                    units.append(None)
                is_date.append(False)
            # Warnung bei gemischten Einheiten (auch None als eigene Einheit zählen)
            unit_counts = Counter([unit if unit is not None else '∅' for unit in units])
            if len(unit_counts) > 1:
                print(f"WARNUNG: Gemischte Einheiten in Spalte '{col}': {dict(unit_counts)} (∅ = keine Einheit)")
            # Typisierung: Datum
            if len(is_date) > 0:
                if sum(is_date) / len(is_date) > 0.8:
                    df[col] = [n if isinstance(n, datetime) else None for n in numbers]
                    continue
            # Typisierung: Float/Int
            num_values = [n for n in numbers if isinstance(n, (float, int))]
            not_empty_values = [n for n in numbers if n is not None and n != '']
            print(f"Spalte '{col}': {len(num_values)} numerische Werte von nicht leeren {len(not_empty_values)} Gesamtwerten ({len(num_values) / len(not_empty_values):.2%})")
            if len(not_empty_values) == 0:
                # Wenn keine nicht-leeren Werte, belasse als String
                df[col] = [str(n) if n is not None else None for n in numbers]
                continue
            if len(num_values) / len(not_empty_values) > 0.8:
                # Prüfe, ob alle floats/ints auch ints sind
                if all(isinstance(n, int) or (isinstance(n, float) and float(n).is_integer()) for n in num_values):
                    df[col] = [int(n) if isinstance(n, (float, int)) and float(n) == int(n) else None for n in numbers]
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                else:
                    df[col] = [float(n) if isinstance(n, (float, int)) else None for n in numbers]
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            # Sonst: belasse als String
        return df
