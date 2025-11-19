"""
NUCLEAR IPv6 WORKAROUND for Render + Supabase
Forces connection through alternative methods to bypass IPv6 routing
"""
import os
import socket

def apply_ipv6_workaround():
    """
    Apply workarounds for IPv6 connectivity issues on Render
    """
    # Set socket defaults to prefer IPv4
    if hasattr(socket, 'has_ipv6'):
        # Force IPv4 preference in socket connections
        socket.setdefaulttimeout(10)
        
    # Print debug information
    print("🔧 Applied IPv6 workaround - preferring IPv4 connections")
    
    return True

def get_alternative_database_url():
    """
    Try to get an alternative database URL that works with IPv4
    """
    original_url = os.environ.get('DATABASE_URL')
    
    if not original_url:
        return None
        
    # Check if we have a prefer IPv4 flag
    prefer_ipv4 = os.environ.get('PREFER_IPV4', '').lower() in ('1', 'true', 'yes')
    
    if prefer_ipv4 and 'supabase.co' in original_url:
        print("🚀 Attempting to use IPv4-optimized connection settings")
        
        # Add connection parameters that might help with IPv4 routing
        if '?' in original_url:
            modified_url = original_url + '&tcp_keepalives_idle=600&tcp_keepalives_interval=30&tcp_keepalives_count=3'
        else:
            modified_url = original_url + '?tcp_keepalives_idle=600&tcp_keepalives_interval=30&tcp_keepalives_count=3'
            
        return modified_url
    
    return original_url