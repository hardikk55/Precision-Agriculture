import csv, hashlib, io, re, uuid, zipfile
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET
from .farm_map import BY_SENSOR

POT_TO_SENSOR = {f'pot {n}': sensor for n, sensor in enumerate(('S00','S01','S10','S11'), 1)}
ALIASES = {'timestamp': ('timestamp','datetime','date time'), 'pot': ('pot','sensor','sensor id'), 'raw_adc': ('soil raw adc 15 min measurement','raw adc','adc'), 'before': ('moisture level before action','moisture before','moisture'), 'raw_after': ('soil raw adc after watering','raw adc after watering'), 'after': ('moisture level after watering','moisture after watering'), 'watering': ('watering status','watering'), 'temperature': ('temperature c','temperature'), 'humidity': ('relative humidity','humidity'), 'rain': ('rain mm','rain')}
def norm(value): return re.sub(r'[^a-z0-9]+',' ',str(value).lower()).strip()
def num(value):
    if value is None or str(value).strip() in ('','Not watered','not watered','N/A','n/a'): return None
    try: return float(value)
    except ValueError: raise ValueError(f'Invalid numeric value: {value}')
def header_map(headers):
    normalized={norm(v): i for i,v in enumerate(headers)}; mapped={}
    for key, choices in ALIASES.items():
        for choice in choices:
            if choice in normalized: mapped[key]=normalized[choice]; break
    if 'pot' not in mapped: raise ValueError('Missing required pot/sensor identifier column.')
    if 'timestamp' not in mapped and not {'check date','check time'}.issubset(normalized): raise ValueError('Missing timestamp column (or Check date and Check time columns).')
    if 'before' not in mapped and 'after' not in mapped: raise ValueError('Missing moisture measurement column.')
    return mapped, normalized
def excel_rows(blob):
    ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}; z=zipfile.ZipFile(io.BytesIO(blob)); sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml')); out=[]
    for row in sh.findall('.//x:sheetData/x:row',ns):
        values={}
        for cell in row.findall('x:c',ns):
            letters=re.match(r'[A-Z]+',cell.get('r','A1')).group(); col=sum((ord(x)-64)*26**i for i,x in enumerate(reversed(letters)))-1
            inline=cell.find('x:is/x:t',ns); values[col]=inline.text if inline is not None else cell.findtext('x:v',default='',namespaces=ns)
        out.append([values.get(i,'') for i in range(max(values,default=-1)+1)])
    return out
def parse(blob, filename):
    rows=excel_rows(blob) if filename.lower().endswith('.xlsx') else list(csv.reader(io.StringIO(blob.decode('utf-8-sig'))))
    if len(rows)<2: raise ValueError('The file is empty or has no data rows.')
    mapping, normalized=header_map(rows[0]); records=[]; errors=[]
    for line,row in enumerate(rows[1:],2):
        try:
            get=lambda key: row[mapping[key]] if key in mapping and mapping[key]<len(row) else ''
            sensor=POT_TO_SENSOR.get(norm(get('pot')),get('pot').strip().upper())
            if sensor not in BY_SENSOR: raise ValueError(f'Unsupported pot/sensor {get("pot")!r}; expected Pot 1 through Pot 4.')
            timestamp=get('timestamp') if 'timestamp' in mapping else f"{row[normalized['check date']]} {row[normalized['check time']]}"; parsed=None
            for form in ('%d-%b-%Y %I:%M %p','%Y-%m-%dT%H:%M:%S','%Y-%m-%d %H:%M:%S'):
                try: parsed=datetime.strptime(timestamp,form).replace(tzinfo=timezone.utc); break
                except ValueError: pass
            if parsed is None and re.fullmatch(r'\d+(\.\d+)?',timestamp): parsed=datetime(1899,12,30,tzinfo=timezone.utc)+timedelta(days=float(timestamp))
            if parsed is None: raise ValueError(f'Invalid timestamp {timestamp!r}.')
            before=num(get('before')) if 'before' in mapping else None; after=num(get('after')) if 'after' in mapping else None; moisture=after if after is not None and norm(get('watering'))=='watered' else before
            if moisture is None or not 1 <= moisture <= 5: raise ValueError('Soil moisture score must be a number from 1 to 5.')
            records.append((parsed.isoformat(),sensor,BY_SENSOR[sensor].pot,num(get('raw_adc')) if 'raw_adc' in mapping else None,before,num(get('raw_after')) if 'raw_after' in mapping else None,after,get('watering') if 'watering' in mapping else None,num(get('temperature')) if 'temperature' in mapping else None,num(get('humidity')) if 'humidity' in mapping else None,num(get('rain')) if 'rain' in mapping else None))
        except ValueError as error: errors.append(f'Row {line}: {error}')
    if errors: raise ValueError(' '.join(errors[:8]))
    sensors={r[1] for r in records}
    if not sensors: raise ValueError('Dataset contains no supported Pot 1–Pot 4 sensor records.')
    if len({(r[0],r[1]) for r in records}) != len(records): raise ValueError('Duplicate timestamp/sensor records were found.')
    return records, {'columns':rows[0],'record_count':len(records),'start_timestamp':min(r[0] for r in records),'end_timestamp':max(r[0] for r in records),'sensors':sorted(sensors),'sample':records[:5]}
def import_dataset(connection, blob, filename, source_kind='uploaded', protected=False):
    records, preview=parse(blob,filename); digest=hashlib.sha256(blob).hexdigest()
    if connection.execute('SELECT 1 FROM datasets WHERE import_key=?',(digest,)).fetchone(): raise ValueError('This dataset has already been imported.')
    dataset_id=str(uuid.uuid4()); now=datetime.now(timezone.utc).isoformat(); connection.execute('BEGIN IMMEDIATE')
    try:
        connection.execute('INSERT INTO datasets(id,filename,source_kind,import_key,imported_at,record_count,start_timestamp,end_timestamp,sensor_count,active,protected) VALUES (?,?,?,?,?,?,?,?,?,?,?)',(dataset_id,filename,source_kind,digest,now,preview['record_count'],preview['start_timestamp'],preview['end_timestamp'],4,0,int(protected)))
        connection.executemany('INSERT INTO historical_readings(dataset_id,timestamp,sensor_id,pot,raw_adc,moisture_before,raw_adc_after,moisture_after,watering_status,temperature,humidity,rain_mm) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',[(dataset_id,*r) for r in records])
        if not connection.execute('SELECT 1 FROM datasets WHERE active=1').fetchone(): connection.execute('UPDATE datasets SET active=1 WHERE id=?',(dataset_id,))
        connection.execute('COMMIT')
    except Exception: connection.execute('ROLLBACK'); raise
    return dataset_id,preview
