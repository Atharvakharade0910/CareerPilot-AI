import httpx
from app.core.config import settings

async def search_adzuna(query: str, location: str = "", page: int = 1) -> list[dict]:
    app_id = getattr(settings, "adzuna_app_id", None); key = getattr(settings, "adzuna_app_key", None); country = getattr(settings, "adzuna_country", "in")
    if not app_id or not key: return []
    key = key.get_secret_value() if hasattr(key, "get_secret_value") else key
    url=f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    async with httpx.AsyncClient(timeout=12) as client:
        r=await client.get(url,params={"app_id":app_id,"app_key":key,"what":query,"where":location,"results_per_page":30,"content-type":"application/json"}); r.raise_for_status(); data=r.json()
    return [{"external_id":str(x.get("id")),"company":(x.get("company") or {}).get("display_name","Unknown"),"title":x.get("title","Untitled"),"location":(x.get("location") or {}).get("display_name",""),"work_type":"remote" if "remote" in x.get("title","").lower() else "any","salary":str(x.get("salary_min") or ""),"url":x.get("redirect_url",""),"description":x.get("description","")} for x in data.get("results",[])]
