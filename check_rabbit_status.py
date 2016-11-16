import urllib2
import abc
import json
from pynagios import Plugin, Response, make_option, OK, WARNING, CRITICAL, UNKNOWN

class RabbitStatusCheck(Plugin):
    # custom options
    user = make_option("--username", dest="username", help="RabbitMQ API username", type="string", default="admin")
    passw = make_option("--password", dest="password", help="RabbitMQ API password", type="string", default="admin")
    port = make_option("--port", dest="port", help="RabbitMQ API port", type="string", default="15672")
    vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')
    host = make_option("--host", dest="host", type="string", default="localhost")
    
    def check(self):
        # performs process
        try:
            # creating the url
            self.url = "http://%s:%s/api/aliveness-test/%s" % (self.options.host, self.options.port, self.options.vhost)
            
            # consulting rabbitmq api
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.url, self.options.user, self.options.passw)
            handler = urllib2.HTTPBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(handler)
        
            request = opener.open(self.url)
            response = request.read()
            request.close()
            
            # parsing response
            data = json.loads(response)
            
            if data['status'] and data['status'] == "ok": 
                result = Response(OK, "RabbitMQ is up and running")
            elif data['status'] and data['status'] != "ok":
                result = Response(CRITICAL, "RabbitMQ is down: {}".format(data['status']))
            elif not data['status']:
                result = Response(CRITICAL, "RabbitMq is down: No status received")
            
        except urllib2.URLError:
            result = Response(CRITICAL, "RabbitMQ is down: Api is not working")
            
        except Exception:
            result = Response(UNKNOWN, "RabbitMQ is confused!")
        
        return result

if __name__ == "__main__":
    RabbitStatusCheck().check().exit()