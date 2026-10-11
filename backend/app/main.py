import logging, re
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .core.config import settings
from .core.database import Base, engine, get_db
from .core.security import create_token, decode_token, verify_password
from .models import AdminUser, BusinessSettings, ConsultationRequest, Enquiry, Property, PropertyImage
from .schemas import *
from .services import notify, rate_limit, StorageService
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s'); log=logging.getLogger("amba")
app=FastAPI(title="Amba Real Estate API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_url],allow_credentials=True,allow_methods=["GET","POST","PUT","PATCH","DELETE"],allow_headers=["Authorization","Content-Type"])
bearer=HTTPBearer()
@app.middleware("http")
async def logging_middleware(request:Request,call_next):
    response=await call_next(request); log.info("%s %s %s",request.method,request.url.path,response.status_code); return response
def current_admin(credentials:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db)):
    try: payload=decode_token(credentials.credentials)
    except Exception: raise HTTPException(401,detail={"code":"invalid_token","message":"Invalid authentication token."})
    user=db.get(AdminUser,int(payload["sub"]))
    if not user or not user.is_active: raise HTTPException(401,detail={"code":"unauthorized","message":"Authentication required."})
    return user
def slugify(title:str): return re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-")
def output(p:Property): return PropertyOut.model_validate(p)
@app.get("/health")
def health(): return {"data":{"status":"ok"}}
@app.get("/health/db")
def health_db(db:Session=Depends(get_db)): db.execute(select(1)); return {"data":{"status":"ok"}}
@app.get("/health/redis")
def health_redis():
    from .services import redis_client
    r=redis_client()
    try: r.ping(); return {"data":{"status":"ok"}}
    except Exception: raise HTTPException(503,detail={"code":"redis_unavailable","message":"Redis unavailable."})
@app.get("/api/v1/properties")
def properties(page:int=1,limit:int=12,location:str|None=None,property_type:str|None=None,min_price:float|None=None,max_price:float|None=None,bedrooms:int|None=None,featured:bool|None=None,search:str|None=None,db:Session=Depends(get_db)):
    page=max(page,1); limit=min(max(limit,1),50); q=select(Property).where(Property.status=="available")
    if location:q=q.where(Property.location.ilike(f"%{location}%"))
    if property_type:q=q.where(Property.property_type==property_type)
    if min_price is not None:q=q.where(Property.price>min_price)
    if max_price is not None:q=q.where(Property.price<=max_price)
    if bedrooms is not None:q=q.where(Property.bedrooms>=bedrooms)
    if featured is not None:q=q.where(Property.featured==featured)
    if search:q=q.where(Property.title.ilike(f"%{search}%"))
    total=db.scalar(select(func.count()).select_from(q.subquery())) or 0; rows=db.scalars(q.options(selectinload(Property.images)).offset((page-1)*limit).limit(limit)).all()
    return {"data":[output(x).model_dump() for x in rows],"meta":{"page":page,"limit":limit,"total":total,"pages":(total+limit-1)//limit}}
@app.get("/api/v1/properties/{slug}")
def property_detail(slug:str,db:Session=Depends(get_db)):
    p=db.scalar(select(Property).options(selectinload(Property.images)).where(Property.slug==slug,Property.status=="available"))
    if not p: raise HTTPException(404,detail={"code":"not_found","message":"Property not found."})
    return {"data":output(p).model_dump()}
@app.post("/api/v1/enquiries",status_code=201)
def enquiry(payload:EnquiryIn,request:Request,db:Session=Depends(get_db)):
    rate_limit(f"enquiry:{request.client.host}",5,3600)
    if payload.website:return {"data":{"received":True}}
    item=Enquiry(**payload.model_dump(exclude={"website"})); db.add(item); db.commit(); notify("enquiry"); return {"data":{"id":item.id,"received":True}}
@app.post("/api/v1/consultations",status_code=201)
def consultation(payload:ConsultationIn,request:Request,db:Session=Depends(get_db)):
    rate_limit(f"consultation:{request.client.host}",5,3600)
    if payload.website:return {"data":{"received":True}}
    item=ConsultationRequest(**payload.model_dump(exclude={"website"})); db.add(item); db.commit(); notify("consultation"); return {"data":{"id":item.id,"received":True}}
@app.get("/api/v1/business")
def business(db:Session=Depends(get_db)):
    item=db.scalar(select(BusinessSettings).limit(1))
    if not item: raise HTTPException(404,detail={"code":"not_configured","message":"Business settings are not configured."})
    return {"data":BusinessOut.model_validate(item).model_dump()}
@app.post("/api/v1/auth/login",response_model=TokenOut)
def login(payload:LoginIn,request:Request,db:Session=Depends(get_db)):
    rate_limit(f"login:{request.client.host}",10,900); user=db.scalar(select(AdminUser).where(AdminUser.email==str(payload.email)))
    if not user or not user.is_active or not verify_password(payload.password,user.password_hash): raise HTTPException(401,detail={"code":"invalid_credentials","message":"Invalid email or password."})
    user.last_login=datetime.now(timezone.utc); db.commit(); return TokenOut(access_token=create_token(str(user.id)),refresh_token=create_token(str(user.id),True))
@app.post("/api/v1/auth/refresh",response_model=TokenOut)
def refresh(payload:RefreshIn,db:Session=Depends(get_db)):
    try: claims=decode_token(payload.refresh_token,True); user=db.get(AdminUser,int(claims["sub"])); assert user and user.is_active
    except Exception: raise HTTPException(401,detail={"code":"invalid_token","message":"Invalid refresh token."})
    return TokenOut(access_token=create_token(str(user.id)),refresh_token=create_token(str(user.id),True))
@app.get("/api/v1/admin/me")
def me(user:AdminUser=Depends(current_admin)): return {"data":{"id":user.id,"email":user.email}}
@app.get("/api/v1/admin/properties")
def admin_properties(db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    return {"data":[output(p).model_dump() for p in db.scalars(select(Property).options(selectinload(Property.images)).order_by(Property.updated_at.desc())).all()]}
@app.post("/api/v1/admin/properties",status_code=201)
def create_property(payload:PropertyIn,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    base=slugify(payload.title); slug=base; n=2
    while db.scalar(select(Property.id).where(Property.slug==slug)): slug=f"{base}-{n}"; n+=1
    p=Property(**payload.model_dump(),slug=slug); db.add(p); db.commit(); db.refresh(p); return {"data":output(p).model_dump()}
@app.get("/api/v1/admin/properties/{id}")
def admin_property(id:int,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    p=db.scalar(select(Property).options(selectinload(Property.images)).where(Property.id==id))
    if not p: raise HTTPException(404,detail={"code":"not_found","message":"Property not found."})
    return {"data":output(p).model_dump()}
@app.put("/api/v1/admin/properties/{id}")
def update_property(id:int,payload:PropertyIn,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    p=db.get(Property,id)
    if not p: raise HTTPException(404,detail={"code":"not_found","message":"Property not found."})
    for key,value in payload.model_dump().items(): setattr(p,key,value)
    db.commit(); db.refresh(p); return {"data":output(p).model_dump()}
@app.delete("/api/v1/admin/properties/{id}",status_code=204)
def delete_property(id:int,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    p=db.get(Property,id)
    if not p: raise HTTPException(404,detail={"code":"not_found","message":"Property not found."})
    db.delete(p); db.commit()
@app.post("/api/v1/admin/properties/{id}/images",status_code=201)
async def upload_image(id:int,file:UploadFile=File(...),alt_text:str|None=None,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    p=db.get(Property,id)
    if not p: raise HTTPException(404,detail={"code":"not_found","message":"Property not found."})
    if not (file.content_type or "").startswith("image/"): raise HTTPException(422,detail={"code":"invalid_image","message":"An image file is required."})
    url=await StorageService().save(file); image=PropertyImage(property_id=id,image_url=url,alt_text=alt_text,sort_order=len(p.images)); db.add(image); db.commit(); db.refresh(image); return {"data":ImageOut.model_validate(image).model_dump()}
@app.delete("/api/v1/admin/properties/{id}/images/{image_id}",status_code=204)
def delete_image(id:int,image_id:int,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    image=db.get(PropertyImage,image_id)
    if not image or image.property_id!=id: raise HTTPException(404,detail={"code":"not_found","message":"Image not found."})
    db.delete(image); db.commit()
@app.get("/api/v1/admin/enquiries")
def enquiries(db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)): return {"data":[{"id":x.id,"name":x.name,"email":x.email,"phone":x.phone,"requirement":x.requirement,"message":x.message,"status":x.status,"created_at":x.created_at} for x in db.scalars(select(Enquiry).order_by(Enquiry.created_at.desc())).all()]}
@app.get("/api/v1/admin/enquiries/{id}")
def enquiry_item(id:int,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    x=db.get(Enquiry,id)
    if not x: raise HTTPException(404,detail={"code":"not_found","message":"Enquiry not found."})
    return {"data":{"id":x.id,"name":x.name,"email":x.email,"phone":x.phone,"requirement":x.requirement,"message":x.message,"status":x.status,"created_at":x.created_at}}
@app.patch("/api/v1/admin/enquiries/{id}")
def update_enquiry(id:int,payload:StatusUpdate,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    x=db.get(Enquiry,id)
    if not x: raise HTTPException(404,detail={"code":"not_found","message":"Enquiry not found."})
    if payload.status not in {"new","contacted","qualified","closed"}: raise HTTPException(422,detail={"code":"invalid_status","message":"Invalid status."})
    x.status=payload.status; db.commit(); return {"data":{"id":x.id,"status":x.status}}
@app.get("/api/v1/admin/consultations")
def consultations(db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)): return {"data":[{"id":x.id,"name":x.name,"email":x.email,"phone":x.phone,"requirement":x.requirement,"preferred_contact_method":x.preferred_contact_method,"message":x.message,"status":x.status,"created_at":x.created_at} for x in db.scalars(select(ConsultationRequest).order_by(ConsultationRequest.created_at.desc())).all()]}
@app.patch("/api/v1/admin/consultations/{id}")
def update_consultation(id:int,payload:StatusUpdate,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    x=db.get(ConsultationRequest,id)
    if not x: raise HTTPException(404,detail={"code":"not_found","message":"Consultation not found."})
    if payload.status not in {"new","contacted","qualified","closed"}: raise HTTPException(422,detail={"code":"invalid_status","message":"Invalid status."})
    x.status=payload.status; db.commit(); return {"data":{"id":x.id,"status":x.status}}
@app.get("/api/v1/admin/business")
def admin_business(db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)): return business(db)
@app.put("/api/v1/admin/business")
def update_business(payload:BusinessIn,db:Session=Depends(get_db),_:AdminUser=Depends(current_admin)):
    item=db.scalar(select(BusinessSettings).limit(1))
    if not item: item=BusinessSettings(**payload.model_dump()); db.add(item)
    else:
        for key,value in payload.model_dump().items(): setattr(item,key,value)
    db.commit(); db.refresh(item); return {"data":BusinessOut.model_validate(item).model_dump()}
