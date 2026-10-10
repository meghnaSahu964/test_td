from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
class ORM(BaseModel): model_config=ConfigDict(from_attributes=True)
class PropertyIn(BaseModel):
    title:str=Field(min_length=2,max_length=255); description:str|None=None; location:str|None=None; city:str|None=None; state:str|None=None; property_type:str|None=None; status:str="draft"; price:float|None=None; currency:str|None=None; area:str|None=None; bedrooms:int|None=Field(None,ge=0); bathrooms:int|None=Field(None,ge=0); featured:bool=False
class ImageOut(ORM): id:int; image_url:str; alt_text:str|None; sort_order:int
class PropertyOut(ORM): id:int; title:str; slug:str; description:str|None; location:str|None; city:str|None; state:str|None; property_type:str|None; status:str; price:float|None; currency:str|None; area:str|None; bedrooms:int|None; bathrooms:int|None; featured:bool; images:list[ImageOut]=[]
class EnquiryIn(BaseModel): name:str=Field(min_length=2,max_length=120); email:EmailStr; phone:str|None=Field(None,max_length=50); requirement:str|None=Field(None,max_length=120); message:str=Field(min_length=5,max_length=3000); website:str|None=None
class ConsultationIn(EnquiryIn): preferred_contact_method:str|None=Field(None,max_length=40)
class StatusUpdate(BaseModel): status:str
class LoginIn(BaseModel): email:EmailStr; password:str=Field(min_length=8,max_length=200)
class RefreshIn(BaseModel): refresh_token:str
class TokenOut(BaseModel): access_token:str; refresh_token:str; token_type:str="bearer"
class BusinessIn(BaseModel): business_name:str; email:EmailStr; phone:str; address:str; city:str; state:str; postal_code:str; country:str="India"; website:str
class BusinessOut(BusinessIn,ORM): id:int
