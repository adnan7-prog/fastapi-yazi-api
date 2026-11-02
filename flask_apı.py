from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel ,Field
from bagimliliklar import sifre_kontrol
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker,Session
import uvicorn
from bagimliliklar import sifre_kontrol, token_uret

app = FastAPI()
class GirisBilgileri(BaseModel):
    kullanici_adi: str
    sifre: str


@app.post("/giris")
async def giris(bilgiler: GirisBilgileri):

    if bilgiler.kullanici_adi != "adnan" or bilgiler.sifre != "adnanx":
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre yanlış")

    token = token_uret(bilgiler.kullanici_adi)
    return {"access_token": token, "token_type": "bearer"}


url = "sqlite:///./yazilar.db"
create = create_engine(url,connect_args={"check_same_thread": False})
sesionyerel = sessionmaker(autoflush=False,autocommit=False,bind=create)
base = declarative_base()

class Veri_tapan(base):
    __tablename__ = "yazilar"
    id = Column(Integer,primary_key=True)
    yazi = Column(String,unique=False)

base.metadata.create_all(create)

def VeriTabanGetir():
    db = sesionyerel()
    try :
        yield db
    finally:
        db.close()

class Eklemeler(BaseModel):
    yazi : str = Field(min_length=5)

@app.post("/yazi_ekleme")
async def yazi_ekleme(isim : Eklemeler,db : Session = Depends(VeriTabanGetir) , kullanici : str = Depends(sifre_kontrol)):
    ekle = Veri_tapan(yazi=isim.yazi)
    db.add(ekle)
    db.commit()
    return {"eklenenler":{"id":f"{ekle.id}","yazi":f"  {ekle.yazi}"}}

@app.get("/yazilar")
async def yazdir(db : Session = Depends(VeriTabanGetir),kullanici : str = Depends(sifre_kontrol)):
    hepsi = db.query(Veri_tapan).all()
    return {"mesaj" : hepsi}

@app.post("/yazilar/{id_cek}")
async def sil(id_cek:int, db : Session = Depends(VeriTabanGetir),kullanici : str = Depends(sifre_kontrol)):
    silmek = db.query(Veri_tapan).filter(Veri_tapan.id == id_cek).first()
    if silmek:
        db.delete(silmek)
        db.commit()
        return {"mesaj": f"{id_cek} id silindi"}
    return {"HATA":f"{id_cek} bu numarada id yok"}        

@app.post("/degistirme/{id_cek}")
async def degistirme(id_cek: int, yeni_yazi: str, db: Session = Depends(VeriTabanGetir),kullanici : Session = Depends(sifre_kontrol)): 
    guncellenecek_veri = db.query(Veri_tapan).filter(Veri_tapan.id == id_cek).first()  
    if guncellenecek_veri:
        guncellenecek_veri.yazi = yeni_yazi 
        db.commit()
        db.refresh(guncellenecek_veri) 
        return {"mesaj": f"{id_cek} id'li yazı başarıyla değiştirildi", "yeni_hali": guncellenecek_veri.yazi}
    else:
        return {"HATA": f"{id_cek} bu numarada bir id yok"}

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)