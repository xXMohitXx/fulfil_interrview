"""
Custom database URL resolver for Render + Supabase IPv6 issues
Forces IPv4 connections to avoid network unreachable errors
"""
import socket
import dns.resolver
from urllib.parse import urlparse, urlunparse

def resolve_ipv4_database_url(database_url):
    """
    Resolve database hostname to IPv4 address to avoid IPv6 routing issues on Render
    """
    try:
        parsed = urlparse(database_url)
        hostname = parsed.hostname
        
        if not hostname:
            return database_url
            
        print(f"🔍 Resolving hostname: {hostname}")
        
        # Force IPv4 resolution
        try:
            # Use DNS resolver to get IPv4 address
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1']  # Use public DNS
            
            # Query for A records (IPv4)
            answers = resolver.resolve(hostname, 'A')
            ipv4_address = str(answers[0])
            
            print(f"✅ Resolved {hostname} to IPv4: {ipv4_address}")
            
            # Replace hostname with IPv4 address
            new_netloc = parsed.netloc.replace(hostname, ipv4_address)
            new_parsed = parsed._replace(netloc=new_netloc)
            new_url = urlunparse(new_parsed)
            
            print(f"🔗 New database URL: {new_url[:50]}...")
            return new_url
            
        except Exception as dns_error:
            print(f"⚠️ DNS resolution failed: {dns_error}")
            
            # Fallback to socket resolution
            try:
                # Get IPv4 address using socket
                ipv4_address = socket.gethostbyname(hostname)
                print(f"✅ Socket resolved {hostname} to IPv4: {ipv4_address}")
                
                # Replace hostname with IPv4 address
                new_netloc = parsed.netloc.replace(hostname, ipv4_address)
                new_parsed = parsed._replace(netloc=new_netloc)
                new_url = urlunparse(new_parsed)
                
                return new_url
                
            except Exception as socket_error:
                print(f"❌ Socket resolution also failed: {socket_error}")
                print(f"🔄 Using original URL as fallback")
                return database_url
                
    except Exception as e:
        print(f"❌ Error in resolve_ipv4_database_url: {e}")
        return database_url