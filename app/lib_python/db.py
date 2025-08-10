import os
import psycopg

def get_db_connection():
    """Get a simple database connection for Supabase"""
    # Supabase Vercel integration provides these environment variables
    postgres_url = os.getenv("POSTGRES_URL")
    postgres_prisma_url = os.getenv("POSTGRES_PRISMA_URL")  # Often used by Supabase
    postgres_url_non_pooling = os.getenv("POSTGRES_URL_NON_POOLING")  # Direct connection
    
    # Try different Supabase connection strings in order of preference
    connection_urls = [
        postgres_url_non_pooling,  # Direct connection (best for simple apps)
        postgres_url,              # Pooled connection
        postgres_prisma_url,       # Prisma-formatted URL
    ]
    
    for url in connection_urls:
        if url:
            try:
                print(f"Trying connection type: {url[:20]}...")
                
                # Clean up the URL - remove any problematic parameters
                clean_url = url
                
                # Handle common Supabase URL issues
                if "supabase" in url:
                    # Ensure SSL is required for Supabase
                    if "sslmode" not in url:
                        separator = "&" if "?" in url else "?"
                        clean_url = url + f"{separator}sslmode=require"
                    
                    # Remove any invalid parameters that might cause issues
                    # You might need to adjust this based on the exact error
                    if "pgbouncer=true" in clean_url:
                        clean_url = clean_url.replace("&pgbouncer=true", "").replace("?pgbouncer=true", "")
                
                return psycopg.connect(clean_url)
                
            except Exception as e:
                print(f"Connection attempt failed: {e}")
                continue
    
    # Fallback: build from individual environment variables
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER") 
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DATABASE")
    
    if all([host, user, password, database]):
        conn_string = f"postgresql://{user}:{password}@{host}/{database}?sslmode=require"
        print("Using individual environment variables")
        return psycopg.connect(conn_string)
    
    raise Exception("No valid database connection configuration found")
