#!/usr/bin/python3.5

import re
import os
import sys
import json
import timeit
import hashlib
import datetime
import requests
import subprocess
from io import BytesIO
from shutil import copyfile
from threading import Thread
from time import gmtime, strftime
from warcio.warcwriter import WARCWriter
from warcio.archiveiterator import ArchiveIterator
from warcio.statusandheaders import StatusAndHeaders


def extrcated_headers_from_warc_record(record, record_status):
    response_headers = {}
    response_headers_values = ''
    response_headers_keys = ''
    if str(record_status)[0] == '2':
        h_v = record.http_headers.get_header('Content-Type')
        if h_v:
            response_headers['Content-Type'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$Content-Type'

        h_v = record.http_headers.get_header('Content-Length')
        if h_v:
            response_headers['Content-Length'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$Content-Length'

        h_v = record.http_headers.get_header('Content-Location')
        if h_v:
            response_headers['Content-Location'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$Content-Location'

        h_v = record.http_headers.get_header('X-Archive-Orig-content-md5')
        if h_v:
            response_headers['X-Archive-Orig-content-md5'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-content-md5'
        
        h_v = record.http_headers.get_header('X-Archive-Orig-x-fb-content-md5')
        if h_v:
            response_headers['X-Archive-Orig-x-fb-content-md5'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-x-fb-content-md5'
        
        h_v = record.http_headers.get_header('X-Archive-Orig-age')
        if h_v:
            response_headers['X-Archive-Orig-age'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-age'
        
        h_v = record.http_headers.get_header('X-Archive-Orig-status')
        if h_v:
            response_headers['X-Archive-Orig-status'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-status'
        
        h_v = record.http_headers.get_header('X-Archive-Orig-date')
        if h_v:
            response_headers['X-Archive-Orig-date'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-date' 

        h_v = record.http_headers.get_header('X-Archive-Orig-user-agent')
        if h_v:
            response_headers['X-Archive-Orig-user-agent'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-user-agent'
        
        h_v = record.http_headers.get_header('X-Archive-Orig-etag')
        if h_v:
            response_headers['X-Archive-Orig-etag'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-etag' 
        
        h_v = record.http_headers.get_header('X-Archive-Orig-link')
        if h_v:
            response_headers['X-Archive-Orig-link'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-link' 
        
        h_v = record.http_headers.get_header('X-Archive-Orig-last-modified')
        if h_v:
            response_headers['X-Archive-Orig-last-modified'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-last-modified'

    elif str(record_status)[0] in ['3','4','5']:
        h_v = record.http_headers.get_header('Location')
        if h_v:
            response_headers['Location'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$Location'

        h_v = record.http_headers.get_header('X-Archive-Orig-date')
        if h_v:
            response_headers['X-Archive-Orig-date'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-date' 

        h_v = record.http_headers.get_header('X-Archive-Orig-status')
        if h_v:
            response_headers['X-Archive-Orig-status'] = h_v
            response_headers_values = response_headers_values +' '+ h_v
            response_headers_keys = response_headers_keys +' '+ '$X-Archive-Orig-status'

    if len(response_headers_values) > 0:
        response_headers_values = response_headers_values[1:]
    if len(response_headers_keys) > 0:
        response_headers_keys = response_headers_keys[1:]       
    return response_headers, response_headers_values, response_headers_keys

def convert_to_original_link(uri):
    tmp = re.findall('\d+', uri)
    
    for t in tmp:
        if len(str(t)) == 14:
            before = uri.split(str(t),1)[0]
            after = uri.split(str(t),1)[1].split("/",1)[1]
            return before+str(t)+'id_/'+after,t, after
    return None, None, None 

def generate_atomic(urim):

    tic_all=timeit.default_timer()

    time_json = {
            'date': strftime("%Y%m%d%H%M%S", gmtime()),
            'time_in_seconds_to_download_memento':0,
            'time_in_seconds_to_generate_fixity':0
    }

    urimid_, mdatetime, urir = convert_to_original_link(urim)

    manif = {
        "@context": "http://manifest.ws-dl.cs.odu.edu/terms.json",
        "uri-r": urir,
        "uri-m": urim,
        "memento-datetime": datetime.datetime.strptime(mdatetime, '%Y%m%d%H%M%S').strftime('%a, %d %b %Y %H:%M:%S GMT')
    }

    urimh = hashlib.md5(urim.encode()).hexdigest()

    downloadtime = strftime("%Y%m%d%H%M%S", gmtime())

    manif["created"] = datetime.datetime.strptime(downloadtime, '%Y%m%d%H%M%S').strftime('%a, %d %b %Y %H:%M:%S GMT')

    # outMainDir =  '/data/Fixity/mementos/'+urimh+'/'+downloadtime

    outMainDir  = '/Users/maturban/Fixity/generate_manifest3/'+urimh+'/'+downloadtime
    warc_file = outMainDir + '/raw.warc'

    tic0=timeit.default_timer()

    if not os.path.exists(outMainDir):
        os.makedirs(outMainDir)

    with open(warc_file, 'wb') as poutput:
        writer = WARCWriter(poutput, gzip=False)

        headers = {
        'User-Agent': 'Web Science and Digital Libraries Group (@WebSciDL); Project/archives_fixity; Contact/Mohamed Aturban (maturban@odu.edu)',
        'Accept-Encoding': None
        }

        try:                            
            resp = requests.get(urimid_, headers=headers, timeout=180, allow_redirects=True, stream=True)
        except:
            pass;

        cont = resp.content
        headers_list = resp.headers.items()
        http_headers = StatusAndHeaders(str(resp.status_code), headers_list, protocol='HTTP/1.0')
        record = writer.create_warc_record(urimid_, 'response',
                                            payload=BytesIO(cont),
                                            http_headers=http_headers)
        try:
            writer.write_record(record)
        except Exception as e:
            print(str(e))

    toc0=timeit.default_timer()

    if os.path.exists(warc_file):
        with open(warc_file, 'rb') as stream:
            counter_raw = 0
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    uri = record.rec_headers.get_header('WARC-Target-URI')
                    if uri == urimid_:
                        status_code = record.http_headers.statusline.split()[0]
                        entity = record.content_stream().read() #.strip()
                        hdrs, hdrs_values, hdrs_keys =  extrcated_headers_from_warc_record(record, status_code)
                        hdrs["Preference-Applied"] = "original-links, original-content"
                        md5h = hashlib.md5(entity + hdrs_values.encode()).hexdigest()
                        sha256h = hashlib.sha256(entity + hdrs_values.encode()).hexdigest()
                        hash_v = "md5:{} sha256:{}".format(md5h, sha256h)
                        hash_constructor = "(curl -s '$uri-m' && echo -n '"+hdrs_keys+"') | tee >(sha256sum) >(md5sum) >/dev/null | cut -d ' ' -f 1 | paste -d':' <(echo -e 'md5\nsha256') - | paste -d' ' - -"

    manif["http-headers"] = hdrs
    manif["hash"] = hash_v
    manif["hash-constructor"] = hash_constructor
    manif["@id"] = "http://manifest.ws-dl.cs.odu.edu/manifest/"+downloadtime+'/ /'+urim

    manif_file = json.dumps(manif,indent=4)
    self_hash = hashlib.sha256(manif_file.encode()).hexdigest()

    manif["@id"] = manif["@id"].replace("/ /","/"+self_hash+"/")

    with open(outMainDir+'/'+self_hash+'.json', 'w') as outfile:
        json.dump(manif, outfile, indent=4)

    toc_all=timeit.default_timer()

    time_json['time_in_seconds_to_download_memento'] = toc0 - tic0
    time_json['time_in_seconds_to_generate_fixity'] = (toc_all - tic_all) - time_json['time_in_seconds_to_download_memento']

    with open(outMainDir+'/'+self_hash+'.json.time', 'w') as outfile:
        json.dump(time_json, outfile, indent=4)    

    return outMainDir+'/'+self_hash+'.json'

def generate_current(urim):

    tic_all=timeit.default_timer()

    time_json = {
            'date': strftime("%Y%m%d%H%M%S", gmtime()),
            'time_in_seconds_to_download_memento':0,
            'time_in_seconds_to_generate_fixity':0
    }

    urimid_, mdatetime, urir = convert_to_original_link(urim)

    manif = {
        "@context": "http://manifest.ws-dl.cs.odu.edu/terms.json",
        "uri-r": urir,
        "uri-m": urim,
        "memento-datetime": datetime.datetime.strptime(mdatetime, '%Y%m%d%H%M%S').strftime('%a, %d %b %Y %H:%M:%S GMT')
    }

    urimh = hashlib.md5(urim.encode()).hexdigest()

    downloadtime = strftime("%Y%m%d%H%M%S", gmtime())

    manif["created"] = datetime.datetime.strptime(downloadtime, '%Y%m%d%H%M%S').strftime('%a, %d %b %Y %H:%M:%S GMT')

    outMainDir =  '/data/Fixity/verification/'+urimh+'/'+downloadtime
    warc_file = outMainDir + '/raw.warc'

    tic0=timeit.default_timer()

    if not os.path.exists(outMainDir):
        os.makedirs(outMainDir)

    with open(warc_file, 'wb') as poutput:
        writer = WARCWriter(poutput, gzip=False)

        headers = {
        'User-Agent': 'Web Science and Digital Libraries Group (@WebSciDL); Project/archives_fixity; Contact/Mohamed Aturban (maturban@odu.edu)',
        'Accept-Encoding': None
        }

        try:                            
            resp = requests.get(urimid_, headers=headers, timeout=180, allow_redirects=True, stream=True)
        except:
            pass;

        cont = resp.content
        headers_list = resp.headers.items()
        http_headers = StatusAndHeaders(str(resp.status_code), headers_list, protocol='HTTP/1.0')
        record = writer.create_warc_record(urimid_, 'response',
                                            payload=BytesIO(cont),
                                            http_headers=http_headers)
        try:
            writer.write_record(record)
        except Exception as e:
            print(str(e))

    toc0=timeit.default_timer()

    if os.path.exists(warc_file):
        with open(warc_file, 'rb') as stream:
            counter_raw = 0
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    uri = record.rec_headers.get_header('WARC-Target-URI')
                    if uri == urimid_:
                        status_code = record.http_headers.statusline.split()[0]
                        entity = record.content_stream().read() #.strip()
                        hdrs, hdrs_values, hdrs_keys =  extrcated_headers_from_warc_record(record, status_code)
                        hdrs["Preference-Applied"] = "original-links, original-content"
                        md5h = hashlib.md5(entity + hdrs_values.encode()).hexdigest()
                        sha256h = hashlib.sha256(entity + hdrs_values.encode()).hexdigest()
                        hash_v = "md5:{} sha256:{}".format(md5h, sha256h)
                        hash_constructor = "(curl -s '$uri-m' && echo -n '"+hdrs_keys+"') | tee >(sha256sum) >(md5sum) >/dev/null | cut -d ' ' -f 1 | paste -d':' <(echo -e 'md5\nsha256') - | paste -d' ' - -"

    manif["http-headers"] = hdrs
    manif["hash"] = hash_v
    manif["hash-constructor"] = hash_constructor
    manif["@id"] = "http://manifest.ws-dl.cs.odu.edu/manifest/"+downloadtime+'/ /'+urim

    manif_file = json.dumps(manif,indent=4)
    self_hash = hashlib.sha256(manif_file.encode()).hexdigest()

    manif["@id"] = manif["@id"].replace("/ /","/"+self_hash+"/")

    with open(outMainDir+'/'+self_hash+'.json', 'w') as outfile:
        json.dump(manif, outfile, indent=4)

    toc_all=timeit.default_timer()

    time_json['time_in_seconds_to_download_memento'] = toc0 - tic0
    time_json['time_in_seconds_to_generate_fixity'] = (toc_all - tic_all) - time_json['time_in_seconds_to_download_memento']

    with open(outMainDir+'/'+self_hash+'.json.time', 'w') as outfile:
        json.dump(time_json, outfile, indent=4)    

    return outMainDir+'/'+self_hash+'.json'

def publish_atomic(manif):

    tic_0=timeit.default_timer()
    manifest_file = manif.rsplit("/",1)[1]
    urimh = manif.split("/data/Fixity/mementos/",1)[1].split("/",1)[0]
    manifest_datetime = manif.split(urimh+'/',1)[1].split("/",1)[0]

    try:
        os.mkdir('/data/Fixity/manifests/'+urimh)
    except:
        pass

    copyfile(manif, '/data/Fixity/manifests/'+urimh+'/'+manifest_datetime+'-'+manifest_file)

    with open(manif) as data_file:
            manifest_json = json.load(data_file)    

    toc_0=timeit.default_timer()

    time_json = {"time_in_seconds_to_publish_manifest" : toc_0 - tic_0, 'date': strftime("%Y%m%d%H%M%S", gmtime())}

    with open(manif+'.publish_time', 'w') as outfile:
        json.dump(time_json, outfile, indent=4)  

    return 'http://manifest.ws-dl.cs.odu.edu/manifest/'+manifest_json['uri-m'], manifest_json['@id']


def disseminate_block(uri_block,flags):

    res_list = []
    times = {}
    
    # archivenow 
    if 'wc' in flags:
        tic=timeit.default_timer()
        cmdo = "archivenow --wc '"+uri_block+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                print('block_urim:',v)
                print('Time-in-secs-to-push-into-wc:',toc-tic)
                print('Date:',strftime("%Y%m%d%H%M%S", gmtime()))
                print()
    
    if 'ia' in flags:
        tic=timeit.default_timer()
        cmdo = "archivenow --ia '"+uri_block+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                print('block_urim:',v)
                print('Time-in-secs-to-push-into-ia:',toc-tic)
                print('Date:',strftime("%Y%m%d%H%M%S", gmtime()))
                print()

    if 'is' in flags:
        tic=timeit.default_timer()
        cmdo = "archivenow --is '"+uri_block+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                print('block_urim:',v)
                print('Time-in-secs-to-push-into-is:',toc-tic)
                print('Date:',strftime("%Y%m%d%H%M%S", gmtime()))
                print()

    if 'cc' in flags:    
        tic=timeit.default_timer()
        cmdo = "archivenow --cc --cc_api_key=dba45acaac24682584eea381f3c36a2d4dbd54ee '"+uri_block+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                print('block_urim:',v)
                print('Time-in-secs-to-push-into-cc:',toc-tic)
                print('Date:',strftime("%Y%m%d%H%M%S", gmtime()))
                print()


def disseminate_atomic(uri_manif,flags):

    res_list = []
    times = {}
    
    # archivenow 
    if 'wc' in flags:
        tic=timeit.default_timer()
        cmdo = "archivenow --wc '"+uri_manif+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        print(out)
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                res_list.append(v)
                times[v] = {}
                times[v]['time_to_archivenow'] = toc-tic
                times[v]['date'] = strftime("%Y%m%d%H%M%S", gmtime())
    
    if 'ia' in flags:
        tic=timeit.default_timer()
        cmdo = "archivenow --ia '"+uri_manif+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                res_list.append(v)
                times[v] = {}
                times[v]['time_to_archivenow'] = toc-tic
                times[v]['date'] = strftime("%Y%m%d%H%M%S", gmtime())

    if 'is' in flags:
        tic=timeit.default_timer()
        cmdo = "archivenow --is '"+uri_manif+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        print(out)
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                res_list.append(v)
                times[v] = {}
                times[v]['time_to_archivenow'] = toc-tic
                times[v]['date'] = strftime("%Y%m%d%H%M%S", gmtime())
    if 'cc' in flags:    
        tic=timeit.default_timer()
        cmdo = "archivenow --cc --cc_api_key=dba45acaac24682584eea381f3c36a2d4dbd54ee '"+uri_manif+"'"
        p = subprocess.Popen(cmdo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        toc=timeit.default_timer()

        for v in out.decode().split("\n"):
            if (v != "") and (v.startswith("http")):
                res_list.append(v)                                    
                times[v] = {}
                times[v]['time_to_archivenow'] = toc-tic
                times[v]['date'] = strftime("%Y%m%d%H%M%S", gmtime())

    # the server keeps those manif_urims locally
    try:                            
        r = requests.get(uri_manif, timeout=180, allow_redirects=True)
    except:
        sys.exit(1)

    json_manif = r.json()

    urimh = hashlib.md5(json_manif['uri-m'].encode()).hexdigest()

    created_dt = datetime.datetime.strptime(json_manif["created"],'%a, %d %b %Y %H:%M:%S GMT').strftime('%Y%m%d%H%M%S')
    manifh = json_manif["@id"].split('.ws-dl.cs.odu.edu/manifest/',1)[1].split("/",1)[1].split("/",1)[0]
    manif_urim_file = '/data/Fixity/manifests/'+urimh+'/'+created_dt+'-'+manifh+'.urim-manif'

    try:
        with open(manif_urim_file) as myfile:
            list_manif_urims = myfile.read().split('\n')
        list_manif_urims = list(filter(lambda a: a != "", list_manif_urims))
    except:
        list_manif_urims = []
        pass;

    try:
        with open(manif_urim_file+'.time') as data_file:
            old_times = json.load(data_file)    
    except:
        old_times = {}
        pass;        

    with open(manif_urim_file, "w") as myfile:
        for v in res_list:
            if (v != "") and (v not in list_manif_urims) and (v.startswith("http")):
                list_manif_urims.append(v)
                old_times[v] = times[v]
        for v in list_manif_urims:
            myfile.write(v+'\n')

    with open(manif_urim_file+'.time', 'w') as outfile:
        json.dump(old_times, outfile, indent=4)  

    return res_list

res_manifests = []
json_manif = {}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def get_manif_ia(m):

    try:
        r = requests.get(m, headers=headers, allow_redirects=True,  timeout=120)
        r.raise_for_status()
        return r.json()
    except:
        return None

def get_manif_cc(m):

    try:
        r = requests.get(m, headers=headers, allow_redirects=True,  timeout=120)
        r.raise_for_status()
        n_urim = "http://perma-archives.org/warc/" +m.rsplit("/",1)[1]+'/'+r.text.split("perma-archives.org/warc/"+m.rsplit("/",1)[1],1)[1].split('"',1)[0]
        r = requests.get(n_urim, headers=headers, allow_redirects=True,  timeout=120)
        r.raise_for_status()
        return r.json()
    except:
        return None

def get_manif_is(m):

        try:
            r = requests.get(m, headers=headers, allow_redirects=True,  timeout=120)
            r.raise_for_status()
            return  json.loads(r.text.split('word;white-space:pre-wrap;">',1)[1].split("</pre></div>",1)[0])
        except:
            return None

def get_manif_wc(m):
    
    try:
        r_init  = requests.get(m, headers=headers, allow_redirects=True,  timeout=120)
        r = requests.get('http://www.webcitation.org/mainframe.php', timeout=180, cookies=r_init.cookies, allow_redirects=True)
        r.raise_for_status()
    except:
        return None

    return r.json()


res_manifests_time = {}

def get_manifests(m):
    
    global res_manifests
    global json_manif
    global res_manifests_time

    if m != "":
        s_name = m.split("//",1)[1].split("/",1)[0]

        if s_name == 'manifest.ws-dl.cs.odu.edu':
            res_manifests.append({m : json_manif})
            res_manifests_time[m] = 0.0

        elif s_name == 'web.archive.org':
            tic_get_manif_ia = timeit.default_timer()
            res_manifests.append({m : get_manif_ia(m)})
            toc_get_manif_ia = timeit.default_timer()
            res_manifests_time[m] = toc_get_manif_ia - tic_get_manif_ia

        elif s_name == 'perma.cc':
            tic_get_manif_cc = timeit.default_timer()
            res_manifests.append({m : get_manif_cc(m)})
            toc_get_manif_cc = timeit.default_timer()
            res_manifests_time[m] = toc_get_manif_cc - tic_get_manif_cc

        elif s_name == 'www.webcitation.org':
            tic_get_manif_wc = timeit.default_timer()
            res_manifests.append({m : get_manif_wc(m)})
            toc_get_manif_wc = timeit.default_timer()
            res_manifests_time[m] = toc_get_manif_wc - tic_get_manif_wc

        elif s_name == 'archive.is':
            tic_get_manif_is = timeit.default_timer()
            res_manifests.append({m : get_manif_is(m)})    
            toc_get_manif_is = timeit.default_timer()
            res_manifests_time[m] = toc_get_manif_is - tic_get_manif_is

def verify_atomic(current_manifest):

    global json_manif
    global res_manifests_time
    global res_manifests

    res_manifests = []

    res_manifests_time = {}

    with open(current_manifest) as data_file:    
            current_manifest_json = json.load(data_file)    

    with open(current_manifest+'.time') as data_file:
        curr_manif_time = json.load(data_file)

    verify_json = {
            "date": strftime("%Y%m%d%H%M%S", gmtime()),
            "current_manif":current_manifest,
            "time_in_seconds_to_download_current_memento":curr_manif_time["time_in_seconds_to_download_memento"],
            "time_in_seconds_to_generate_current_fixity":curr_manif_time["time_in_seconds_to_download_memento"],
            "manif_mementos":{}
    }


    tic_discover=timeit.default_timer()

    mdatetime = current_manifest_json['memento-datetime']
    mdatetime_ts = datetime.datetime.strptime(mdatetime, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y%m%d%H%M%S')
    generic_manifest = 'http://manifest.ws-dl.cs.odu.edu/manifest/'+mdatetime_ts+'/'+current_manifest_json['uri-m']
    hash_md5_sha256 = current_manifest_json["hash"]

    try:
        r = requests.get(generic_manifest, allow_redirects=True,  timeout=120)
        r.raise_for_status()
    except Exception as e:
        print('Error', str(e))
        sys.exit(1)

    json_manif = r.json()

    urimh = hashlib.md5(json_manif['uri-m'].encode()).hexdigest()

    created_dt = datetime.datetime.strptime(json_manif["created"],'%a, %d %b %Y %H:%M:%S GMT').strftime('%Y%m%d%H%M%S')
    manifh = json_manif["@id"].split('.ws-dl.cs.odu.edu/manifest/',1)[1].split("/",1)[1].split("/",1)[0]
    manif_urim_file = '/data/Fixity/manifests/'+urimh+'/'+created_dt+'-'+manifh+'.urim-manif'

    try:
        with open(manif_urim_file) as myfile:
            list_manif_urims = myfile.read().split('\n')
        list_manif_urims = list(filter(lambda a: a != "", list_manif_urims))
    except:
        list_manif_urims = []
        pass;

    uri_manif = r.url
    list_manif_urims = [uri_manif] + list_manif_urims
    
    toc_discover=timeit.default_timer()
    verify_json["time-to-discover_manifests_through_server"] = toc_discover - tic_discover

    matched = []
    mismatched = []

    threads = []

    for m in list_manif_urims:
        threads.append(Thread(target=get_manifests, args=(m,)))

    for th in threads:
        th.start()
    for th in threads:
        th.join()

    titit = 0.0
    for v, k in res_manifests_time.items():
        verify_json["manif_mementos"][v] = {"time-to-download-manifest-memento":k}
        if k > titit:
            titit = k
    verify_json['total-time-to-download-all-manifests-in-parallel'] = titit

    for v in res_manifests:
        m = list(v)[0]
        js = v[m]
        if js != None:
            if hash_md5_sha256 == js["hash"]:
                matched.append(m)
                verify_json["manif_mementos"][m]['matched'] = "YES"
            else:
                verify_json["manif_mementos"][m]['matched'] = "No"
                mismatched.append(m)

    mismatched = list(filter(lambda a: a != None, mismatched))

    verify_json['matched-manifests'] = len(matched)
    verify_json['mismatched-manifests'] = len(mismatched)

    manif_urim_file_verify = manif_urim_file+'.verify'
    with open(manif_urim_file_verify, 'w') as outfile:
        json.dump(verify_json, outfile, indent=4)    

    print(json.dumps(verify_json, indent=4))

    return hash_md5_sha256, matched, mismatched


if __name__ == '__main__':

    action = sys.argv[1]

    if action == 'generate_atomic':
        manif_loc = generate_atomic(sys.argv[2])
        print(manif_loc)
    elif action == 'generate_current':
        manif_loc = generate_current(sys.argv[2])
        print(manif_loc)
    elif action == 'publish_atomic':
        generic_uri, trusty_uri = publish_atomic(sys.argv[2])
        print(generic_uri)
        print(trusty_uri)    

    elif action == 'disseminate_atomic':
        manif_urims = disseminate_atomic(sys.argv[2])
        for m in manif_urims:
            print(m)

    elif action == "disseminate_block":
        disseminate_block(sys.argv[2], sys.argv[3].split(","))

    elif action == 'verify_atomic':
        current_h, matched, mismatched = verify_atomic(sys.argv[2])
        print('Current hash:', current_h)
        print(len(matched),'matched manifests:')
        for m in matched:
            print('\t'+str(m))
        print(len(mismatched),'mismatched manifests:')
        for m in mismatched:
            print('\t'+str(m))   
    elif action == 'verify_without_server':
        print("ready but not available yes.")

