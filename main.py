from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib
import models, schemas, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

# USUARIOS

@app.post("/usuarios", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    hashed_password = hashlib.sha256(usuario.clave.encode()).hexdigest()
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        clave=hashed_password
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@app.get("/usuarios", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(database.get_db)):
    return db.query(models.Usuario).all()


@app.get("/usuarios/{id}", response_model=schemas.UsuarioResponse)
def obtener_usuario(id: int, db: Session = Depends(database.get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.put("/usuarios/{id}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(id: int, usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db_usuario.nombre = usuario.nombre
    db_usuario.apellido = usuario.apellido
    db_usuario.correo = usuario.correo
    db_usuario.clave = hashlib.sha256(usuario.clave.encode()).hexdigest()

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@app.delete("/usuarios/{id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(id: int, db: Session = Depends(database.get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_usuario)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}


# LOGIN

@app.post("/login")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(database.get_db)):
    # Buscar usuario por correo
    db_usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario.correo).first()
    if not db_usuario:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    # Comparar clave encriptada
    hashed_password = hashlib.sha256(usuario.clave.encode()).hexdigest()
    if db_usuario.clave != hashed_password:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    return {"mensaje": "Inicio de sesión exitoso"}
