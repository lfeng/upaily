# coding:utf-8

import json
import types
import urllib
import urllib2

from multipart import Multipart, Part
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class UpaiApi:

    upai_host    = "http://www.yupoo.com"
    cube_host    = "http://v.yupoo.com"
    img_host     = "http://pic.yupoo.com"

    perms_read   = 'read'
    perms_write  = 'write'
    perms_delete = 'delete'

    def __init__(self, api_key, secret, token=False, scope='upai', format='json'):
        self.api_key = api_key
        self.api_secret = secret
        self.token = token
        self.format = format

        if scope == 'upai':
            self.api_host = self.upai_host
        elif scope == 'cube':
            self.api_host = self.cube_host

    def get(self, api_method, **params):
        return self.call(api_method, 'GET', **params)

    def post(self, api_method, **params):
        return self.call(api_method, 'POST', **params)

    def call(self, api_method, request_method='GET', **params):
        params['api_key'] = self.api_key
        params['method'] = api_method

        if self.token:
            params['auth_token'] = self.token

        params['api_sig'] =self.sign(**params)

        return json.loads(self.__do_request('/api/', params, request_method,
                                 params))

    def upload(self,  photos, **params):#{{{
        params['format'] = self.format
        params['api_key'] = self.api_key

        if self.token:
            params['auth_token'] = self.token

        params['api_sig'] =self.sign(**params)

        req_url = self.api_host + '/api/upload/'

        body = Multipart()
        for arg, value in params.iteritems():
            part = Part({'name': arg}, value)
            body.attach(part)

        if type(photos) != types.ListType:
            photos = [photos]

        for photo in photos:
            filepart = Part({'name': 'photo', 'filename':params['title'].encode('utf8')},
                             photo['data'],
                            'image/'+photo['type'])
            body.attach(filepart)

        request = urllib2.Request(url=req_url)
        request.add_data(str(body))
        (header, value) = body.header()
        request.add_header(header, value)
        #request.add_header('content-length', len(str(body)))
        return json.loads(urllib2.urlopen(request).read())#}}}

    def get_auth_frob_url(self, perms):#{{{
        params = {
            'api_key':self.api_key,
            'perms':perms,
            #            'return':'fjdkslajfkdlasf!@#$%^&*(中文'
        }
        params['api_sig'] = self.sign(**params)

        return self.api_host + '/services/auth/?' + urllib.urlencode(params)#}}}

    def get_token(self, frob):#{{{
        params = {
            'method'  : 'yupoo.auth.getToken',
            'api_key' : self.api_key,
            'frob'    : frob
        }

        return json.loads(self.get('yupoo.auth.getToken', **params))#}}}

    def sign(self, **kwargs):#{{{#{{{
        """
        参数签名
        """
        data = [self.api_secret]
        for key in sorted(kwargs.keys()):
            data.append(key)
            val = kwargs[key]
            if isinstance(val, unicode):
                val = val.encode('utf-8')

            data.append(val)

        md5_hash = md5(''.join(data))

        return md5_hash.hexdigest()#}}}#}}}

    def __do_request(self, path, params, method="GET", is_multi=False):#{{{

        req_url = self.api_host + path + self.format

        try:
            if method == 'GET':
                request = urllib.urlopen(req_url, urllib.urlencode(params))
                response = request.read()
            else:
                data_str = urllib.urlencode(params)
                request = urllib2.Request(url = req_url, data = data_str)
                response = urllib2.urlopen(request).read()

            return response
        except Exception, e:
            raise e#}}}
