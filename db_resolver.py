"""
Simple IPv4 database URL resolver for Render + Supabase IPv6 issues
Uses only standard library socket module to avoid external dependencies
"""
import socket
from urllib.parse import urlparse, urlunparse

def resolve_ipv4_database_url(database_url):
    """
    Resolve database hostname to IPv4 address using socket.gethostbyname()
    This forces IPv4 resolution and avoids IPv6 routing issues on Render
    """
    try:
        parsed = urlparse(database_url)
        hostname = parsed.hostname
        
        if not hostname:
            print("🔄 No hostname found, using original URL")
            return database_url
            
        print(f"🔍 Resolving hostname to IPv4: {hostname}")
        
        try:
            # Use socket to get IPv4 address (forces IPv4 lookup)
            ipv4_address = socket.gethostbyname(hostname)
            print(f"✅ Resolved {hostname} to IPv4: {ipv4_address}")
            
            # Replace hostname with IPv4 address in URL
            new_netloc = parsed.netloc.replace(hostname, ipv4_address)
            new_parsed = parsed._replace(netloc=new_netloc)
            new_url = urlunparse(new_parsed)
            
            print(f"🔗 IPv4 database URL created: {new_url[:50]}...")
            return new_url
            
        except socket.gaierror as e:
            print(f"❌ Failed to resolve {hostname} to IPv4: {e}")
            print(f"🔄 Using original URL as fallback")
            return database_url
            
        except Exception as e:
            print(f"❌ Unexpected error resolving {hostname}: {e}")
            print(f"🔄 Using original URL as fallback")
            return database_url
                
    except Exception as e:
        print(f"❌ Error in resolve_ipv4_database_url: {e}")
        print(f"🔄 Using original URL as fallback")
        return database_url