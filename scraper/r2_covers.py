"""Store verified public photobook covers in R2 using content-addressed keys."""
import datetime as dt
import hashlib
import hmac
import ipaddress
import os
import socket
from urllib.parse import quote, urlsplit
import requests
from cover_policy import validate_cover_url


def load_env(path):
    for line in open(path, encoding='utf-8-sig'):
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class R2Covers:
    def __init__(self):
        def required(suffix):
            value = os.environ.get('CLOUDFLARE_R2_' + suffix, '').strip()
            if not value: raise ValueError('Missing CLOUDFLARE_R2_' + suffix)
            return value
        self.endpoint = required('ENDPOINT').rstrip('/')
        self.bucket = required('BUCKET')
        self.access = required('ACCESS_KEY_ID')
        self.secret = required('SECRET_ACCESS_KEY')
        self.public = required('PUBLIC_BASE_URL').rstrip('/')
        if urlsplit(self.endpoint).scheme != 'https' or urlsplit(self.public).scheme != 'https':
            raise ValueError('R2 endpoint and public base URL must use HTTPS')

    def request(self, method, key='', data=b'', content_type=''):
        url = self.endpoint + '/' + quote(self.bucket, safe='') + ('/' + quote(key, safe='/') if key else '')
        now = dt.datetime.now(dt.timezone.utc)
        stamp, day = now.strftime('%Y%m%dT%H%M%SZ'), now.strftime('%Y%m%d')
        digest = hashlib.sha256(data).hexdigest()
        headers = {'host':urlsplit(url).netloc,'x-amz-content-sha256':digest,'x-amz-date':stamp}
        if content_type: headers['content-type'] = content_type
        signed = ';'.join(sorted(headers))
        canonical = '\n'.join([method,urlsplit(url).path,'',''.join(k+':'+headers[k]+'\n' for k in sorted(headers)),signed,digest])
        scope = day+'/auto/s3/aws4_request'
        to_sign = 'AWS4-HMAC-SHA256\n'+stamp+'\n'+scope+'\n'+hashlib.sha256(canonical.encode()).hexdigest()
        signing = ('AWS4'+self.secret).encode()
        for part in [day,'auto','s3','aws4_request']: signing=hmac.new(signing,part.encode(),hashlib.sha256).digest()
        signature=hmac.new(signing,to_sign.encode(),hashlib.sha256).hexdigest()
        headers['Authorization']='AWS4-HMAC-SHA256 Credential='+self.access+'/'+scope+', SignedHeaders='+signed+', Signature='+signature
        response = requests.request(method,url,headers=headers,data=data,timeout=40,allow_redirects=False)
        if response.status_code >= 400: raise RuntimeError('R2 '+method+' failed: HTTP '+str(response.status_code))
        return response

    def upload(self, original_url):
        data, mime = download_cover(original_url)
        suffix = {'image/jpeg':'jpg','image/png':'png','image/webp':'webp','image/gif':'gif'}[mime]
        key='musebooks/covers/'+hashlib.sha256(data).hexdigest()+'.'+suffix
        self.request('PUT',key,data,mime)
        self.request('HEAD',key)
        public_url=self.public+'/'+key
        response=requests.get(public_url,timeout=30)
        if response.status_code != 200 or hashlib.sha256(response.content).digest()!=hashlib.sha256(data).digest():
            raise RuntimeError('Uploaded cover is not available through R2 public URL')
        return {'url':public_url,'key':key,'originalUrl':original_url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


def download_cover(url):
    for _ in range(4):
        validate_cover_url(url)
        parsed=urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Cover must be a public HTTPS URL')
        for entry in socket.getaddrinfo(parsed.hostname,443):
            if not ipaddress.ip_address(entry[4][0]).is_global: raise ValueError('Private cover host rejected')
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MusebooksCatalog/1.0)'}
        # Cite's CloudFront image host rejects hotlink requests without the
        # publisher-site referrer. Keep this scoped to that exact image host.
        if parsed.hostname == 'd4dpzjhk0g50s.cloudfront.net':
            headers['Referer'] = 'https://www.cite.com.tw/'
        with requests.get(url,headers=headers,timeout=30,stream=True,allow_redirects=False) as response:
            if response.is_redirect:
                from urllib.parse import urljoin
                url=urljoin(url,response.headers['Location']);continue
            response.raise_for_status()
            parts=[];size=0
            for chunk in response.iter_content(65536):
                size+=len(chunk)
                if size>8*1024*1024: raise ValueError('Cover exceeds 8 MB')
                parts.append(chunk)
            data=b''.join(parts)
        if data.startswith(b'\xff\xd8\xff'): mime='image/jpeg'
        elif data.startswith(b'\x89PNG\r\n\x1a\n'): mime='image/png'
        elif data[:6] in (b'GIF87a',b'GIF89a'): mime='image/gif'
        elif data[:4]==b'RIFF' and data[8:12]==b'WEBP': mime='image/webp'
        else: raise ValueError('Cover response is not a supported image')
        return data,mime
    raise ValueError('Too many cover redirects')

if __name__=='__main__':
    load_env('backend/.env')
    store=R2Covers()
    store.request('HEAD')
    print('R2 bucket access verified:',store.bucket)
