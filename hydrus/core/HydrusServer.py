import time
import traceback

from twisted.web.http import _GenericHTTPChannelProtocol, HTTPChannel
from twisted.web.server import Request, Site
from twisted.web.resource import Resource

from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusData
from hydrus.core import HydrusServerResources

LOCAL_DOMAIN = HydrusServerResources.HydrusDomain( True )
REMOTE_DOMAIN = HydrusServerResources.HydrusDomain( False )

class HydrusRequest( Request ):
    
    def __init__( self, *args, **kwargs ):
        
        Request.__init__( self, *args, **kwargs )
        
        self.start_time = HydrusData.GetNowPrecise()
        self.parsed_request_args = None
        self.hydrus_response_context = None
        self.hydrus_account = None
        self.client_api_permissions = None
        
    
    def IsGET( self ):
        
        return self.method == b'GET'
        
    
    def IsPOST( self ):
        
        return self.method == b'POST'
        
    
class HydrusRequestLogging( HydrusRequest ):
    
    def finish( self ):
        
        HydrusRequest.finish( self )
        
        host = self.getHost()
        
        if self.hydrus_response_context is not None:
            
            status_text = str( self.hydrus_response_context.GetStatusCode() )
            
        elif hasattr( self, 'code' ):
            
            status_text = str( self.code )
            
        else:
            
            status_text = '200'
            
        
        message = str( host.port ) + ' ' + str( self.method, 'utf-8' ) + ' ' + str( self.path, 'utf-8' ) + ' ' + status_text + ' in ' + HydrusData.TimeDeltaToPrettyTimeDelta( HydrusData.GetNowPrecise() - self.start_time )
        
        HydrusData.Print( message )
        
    

class FatHTTPChannel( HTTPChannel ):
    
    totalHeadersSize = 1048576 # :^)
    
class HydrusService( Site ):
    
    def __init__( self, service ):
        
        self._service = service
        
        root = self._InitRoot()
        
        Site.__init__( self, root )
        
        self.protocol = self._ProtocolFactory
        
        if service.LogsRequests():
            
            self.requestFactory = HydrusRequestLogging
            
        else:
            
            self.requestFactory = HydrusRequest
            
        
    
    def _InitRoot( self ):
        
        root = Resource()
        
        root.putChild( b'', HydrusServerResources.HydrusResourceWelcome( self._service, REMOTE_DOMAIN ) )
        root.putChild( b'favicon.ico', HydrusServerResources.hydrus_favicon )
        root.putChild( b'robots.txt', HydrusServerResources.HydrusResourceRobotsTXT( self._service, REMOTE_DOMAIN ) )
        
        return root
        
    
    def _ProtocolFactory( self ):
        
        return _GenericHTTPChannelProtocol( FatHTTPChannel() )
        
