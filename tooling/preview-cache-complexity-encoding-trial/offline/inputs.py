"""Process-free native-byte classification; independent of the C++ detector."""
import hashlib
import json
from pathlib import Path

FORMATS = {4, 5, 6, 16, 17, 18}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def classify(data, width, height, image_format, byte_order):
    require(type(width) is int and type(height) is int and width > 0 and height > 0, 'native dimensions')
    require(type(image_format) is int and byte_order in ('little', 'big'), 'native format/order')
    require(len(data) == width*height*4, 'packed native length')
    if image_format not in FORMATS or min(width, height) < 2:
        return dict(sample_count=0, complex_count=0, writer='default')
    xs = [1+(2*i+1)*(width-1)//(2*min(32,width-1)) for i in range(min(32,width-1))]
    ys = [1+(2*j+1)*(height-1)//(2*min(32,height-1)) for j in range(min(32,height-1))]
    def pixel(x,y):
        offset = (y*width+x)*4
        return data[offset:offset+4]
    count = sum(pixel(x,y) != pixel(x-1,y) and pixel(x,y) != pixel(x,y-1) for y in ys for x in xs)
    samples = len(xs)*len(ys)
    return dict(sample_count=samples, complex_count=count, writer='compression11' if 4*count >= samples else 'default')


def validate(directory):
    manifest = directory/'inputs.json'
    records = json.loads(manifest.read_text())
    expected = [f'{name}-{tier}' for name in ('textured','flat','alpha','oriented','two-color','gradient','panel') for tier in (128,256,512,1024)]
    require([r['id'] for r in records] == expected, 'materialized corpus membership')
    files = {'inputs.json': hashlib.sha256(manifest.read_bytes()).hexdigest()}
    for record in records:
        for suffix, key in (('rgba','pixels'),('native','native'),('icc','icc')):
            name = record['id']+'-input.'+suffix
            data = (directory/name).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            require(digest == record[key], 'materialized file identity')
            files[name] = digest
            if suffix == 'native':
                require(record['format'] in FORMATS, 'corpus format eligibility')
                calculated = classify(data, record['width'], record['height'], record['format'], record['byte_order'])
                require(type(record['sample_count']) is int and type(record['complex_count']) is int, 'classification count types')
                require(all(record[k] == v for k,v in calculated.items()), 'native classification mismatch')
            if suffix == 'rgba':
                require(len(data) == record['width']*record['height']*4, 'canonical RGBA length')
    return dict(files=files, manifest_sha256=files['inputs.json'], records=records)
