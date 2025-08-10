from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Service role key for server-side operations
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Anonymous key (optional, respects RLS)

def get_supabase_client() -> Client:
    """Get Supabase client with service role for server-side operations"""
    if not SUPABASE_URL:
        raise Exception("SUPABASE_URL environment variable not set")
    
    # Use service role key for server-side operations (bypasses RLS)
    if SUPABASE_SERVICE_ROLE_KEY:
        print("Using service role key")
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Fallback to anon key (respects RLS)
    elif SUPABASE_ANON_KEY:
        print("Using anonymous key (RLS enforced)")
        return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    else:
        raise Exception("No Supabase key found in environment variables")

app = FastAPI()

# Simple CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://testing-deployment-f4ec.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/api/get_all")
def get_all():
    """Simple database test endpoint using Supabase client"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("data").select("*").execute()

        return response.data
    
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=500, detail=f"Supabase connection failed: {str(e)}")
