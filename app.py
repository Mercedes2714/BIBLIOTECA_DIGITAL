from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuración inicial de SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== TABLA INTERMEDIA (N-M) ====================
libro_genero = db.Table('libro_genero',
    db.Column('libro_id', db.Integer, db.ForeignKey('libro.id'), primary_key=True),
    db.Column('genero_id', db.Integer, db.ForeignKey('genero.id'), primary_key=True)
)

# ==================== MODELO AUTOR ====================
class Autor(db.Model):
    __tablename__ = "autor"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    nacionalidad = db.Column(db.String, nullable=False)
    
    # Relación 1-N con Libro (cascade para eliminación)
    libros = db.relationship('Libro', backref='autor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Autor('{self.nombre}', '{self.nacionalidad}')"


# ==================== MODELO GENERO ====================
class Genero(db.Model):
    __tablename__ = "genero"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False, unique=True)
    
    # Relación N-M con Libro
    libros = db.relationship('Libro', secondary=libro_genero, lazy='subquery',
                           backref=db.backref('generos', lazy=True))
    
    def __repr__(self):
        return f"Genero('{self.nombre}')"

# ==================== MODELO LIBRO ====================
class Libro(db.Model):
    __tablename__ = "libro"
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    
    # Foreign Key hacia Autor (relación 1-N)
    autor_id = db.Column(db.Integer, db.ForeignKey('autor.id'), nullable=False)
    
    def __repr__(self):
        return f"Libro('{self.titulo}', {self.anio})"


# ==================== INICIALIZAR BD ====================
def init_db():
    with app.app_context():
        db.create_all()
        print("✓ Tablas creadas exitosamente")

# ==================== INSERTAR DATOS ====================
def insertar_datos():
    with app.app_context():
        # Crear autores (mínimo 3)
        autor1 = Autor(nombre="Gabriel García Márquez", nacionalidad="Colombiana")
        autor2 = Autor(nombre="Isaac Asimov", nacionalidad="Estadounidense")
        autor3 = Autor(nombre="J.K. Rowling", nacionalidad="Británica")
        
        # Crear géneros (mínimo 4)
        genero1 = Genero(nombre="Ficcion")
        genero2 = Genero(nombre="Ciencia")
        genero3 = Genero(nombre="Tecnologia")
        genero4 = Genero(nombre="Lenguaje")
        
        # Crear libros (mínimo 5)
        libro1 = Libro(titulo="Cien años de soledad", anio=1967, autor=autor1)
        libro2 = Libro(titulo="El amor en los tiempos del cólera", anio=1985, autor=autor1)
        libro3 = Libro(titulo="Fundación", anio=1951, autor=autor2)
        libro4 = Libro(titulo="Yo, Robot", anio=1950, autor=autor2)
        libro5 = Libro(titulo="Harry Potter y la piedra filosofal", anio=1997, autor=autor3)


     # Asociar libros con géneros (relación N-M)
        libro1.generos.append(genero1)
        libro1.generos.append(genero4)
        
        libro2.generos.append(genero1)
        libro2.generos.append(genero4)
        
        libro3.generos.append(genero1)
        libro3.generos.append(genero2)
        
        libro4.generos.append(genero1)
        libro4.generos.append(genero2)
        libro4.generos.append(genero3)
        
        libro5.generos.append(genero1)
        
        # Añadir todo a la sesión
        db.session.add(autor1)
        db.session.add(autor2)
        db.session.add(autor3)
        
        db.session.add(genero1)
        db.session.add(genero2)
        db.session.add(genero3)
        db.session.add(genero4)
        
        db.session.add(libro1)
        db.session.add(libro2)
        db.session.add(libro3)
        db.session.add(libro4)
        db.session.add(libro5)
        
        # Guardar en BD
        db.session.commit()
        print("✓ Datos insertados correctamente")
        print(f"  - 3 autores")
        print(f"  - 5 libros")
        print(f"  - 4 géneros")


#=================== CONSULTAR DATOS ====================
def consultar_datos():
    with app.app_context():
        print("\n" + "="*60)
        print("AUTORES Y SUS LIBROS:")
        print("="*60)
        
        autores = Autor.query.all()
        for autor in autores:
            print(f"\n📝 {autor.nombre} ({autor.nacionalidad})")
            print(f"   ID: {autor.id}")
            if autor.libros:
                for libro in autor.libros:
                    print(f"   📖 '{libro.titulo}' ({libro.anio})")
                    print(f"      Géneros: {', '.join([g.nombre for g in libro.generos])}")
            else:
                print("   Sin libros registrados")
        
        print("\n" + "="*60)
        print("GÉNEROS Y SUS LIBROS:")
        print("="*60)
        
        generos = Genero.query.all()
        for genero in generos:
            print(f"\n📚 {genero.nombre}")
            print(f"   ID: {genero.id}")
            if genero.libros:
                for libro in genero.libros:
                    print(f"   📖 '{libro.titulo}' ({libro.anio}) - Autor: {libro.autor.nombre}")
            else:
                print("   Sin libros registrados")


# ==================== ACTUALIZAR DATOS ====================
def actualizar_datos():
    with app.app_context():
        print("\n" + "="*60)
        print("ACTUALIZAR DATOS:")
        print("="*60)
        
        # Buscar un libro
        libro = Libro.query.filter_by(id=1).first()
        
        if libro:
            print(f"\n📖 Libro ANTES de actualizar:")
            print(f"   ID: {libro.id}")
            print(f"   Título: '{libro.titulo}'")
            print(f"   Año: {libro.anio}")
            print(f"   Autor: {libro.autor.nombre}")
            
            # Actualizar título
            libro.titulo = "Cien años de soledad - Edición Especial"
            
            db.session.commit()
            
            print(f"\n✓ Libro DESPUÉS de actualizar:")
            print(f"   Título: '{libro.titulo}'")
            print("   ¡Título actualizado correctamente!")


# ==================== ELIMINAR DATOS ====================
def eliminar_datos():
    with app.app_context():
        print("\n" + "="*60)
        print("ELIMINAR DATOS (CASCADE):")
        print("="*60)
        
        # Mostrar autor a eliminar y sus libros
        autor = Autor.query.filter_by(id=3).first()
        
        if autor:
            print(f"\n📝 Autor a eliminar: {autor.nombre} (ID: {autor.id})")
            print(f"   Nacionalidad: {autor.nacionalidad}")
            
            if autor.libros:
                print(f"\n   📚 Libros que se eliminarán en cascada:")
                for libro in autor.libros:
                    print(f"      - '{libro.titulo}' (ID: {libro.id})")
            
            # Eliminar autor (los libros se eliminan en cascada)
            db.session.delete(autor)
            db.session.commit()
            
            print(f"\n✓ Autor eliminado correctamente")
            print("✓ Libros eliminados en cascada")


# ==================== VERIFICAR ELIMINACIÓN ====================
def verificar_eliminacion():
    with app.app_context():
        print("\n" + "="*60)
        print("VERIFICACIÓN FINAL - ESTADO DE LA BD:")
        print("="*60)
        
        print(f"\n📝 Autores restantes: {Autor.query.count()}")
        for autor in Autor.query.all():
            print(f"   - {autor.nombre} ({len(autor.libros)} libros)")
        
        print(f"\n📖 Libros restantes: {Libro.query.count()}")
        for libro in Libro.query.all():
            print(f"   - '{libro.titulo}' ({libro.anio})")
        
        print(f"\n📚 Géneros: {Genero.query.count()}")
        for genero in Genero.query.all():
            print(f"   - {genero.nombre} ({len(genero.libros)} libros)")


# ==================== FLUJO PRINCIPAL ====================
if __name__ == "__main__":
    print("="*60)
    print("SISTEMA DE GESTIÓN DE BIBLIOTECA DIGITAL")
    print("Flask + SQLAlchemy - ORM")
    print("="*60)
    
    # 1. Crear tablas
    #init_db()
    
    # 2. Insertar datos
    #insertar_datos()
    
    # 3. Consultar datos
    #consultar_datos()
    
    # 4. Actualizar datos
    #actualizar_datos()
    
    # 5. Eliminar datos (con cascade)
    #eliminar_datos()
    
    # 6. Verificar eliminación
    verificar_eliminacion()
    
    print("\n" + "="*60)
    print("¡Todas las operaciones completadas exitosamente!")
    print("="*60)