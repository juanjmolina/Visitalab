"""
VisitaLab — Backend Flask
Base de datos PostgreSQL (Azure) con SQLAlchemy
"""

import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Text, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional

# ─────────────────────────────────────────────
#  Configuración
# ─────────────────────────────────────────────

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)

    # DATABASE_URL viene de la variable de entorno de Azure App Service
    # Para desarrollo local usa SQLite como fallback
    db_url = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(app.instance_path, 'visitalab_dev.db')}"
    )

    # Azure PostgreSQL usa "postgres://" pero SQLAlchemy necesita "postgresql://"
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ─── Rutas ───
    register_routes(app)

    return app


# ─────────────────────────────────────────────
#  Modelos
# ─────────────────────────────────────────────

class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    pais: Mapped[Optional[str]] = mapped_column(String(100))
    ciudad: Mapped[Optional[str]] = mapped_column(String(100))
    industria: Mapped[Optional[str]] = mapped_column(String(100))
    tamano: Mapped[Optional[str]] = mapped_column(String(100))
    web: Mapped[Optional[str]] = mapped_column(String(200))
    tel: Mapped[Optional[str]] = mapped_column(String(60))
    sector: Mapped[Optional[str]] = mapped_column(String(100))
    dir: Mapped[Optional[str]] = mapped_column(String(300))
    desc: Mapped[Optional[str]] = mapped_column(Text)
    cert: Mapped[Optional[str]] = mapped_column(String(300))
    notas: Mapped[Optional[str]] = mapped_column(Text)
    emoji: Mapped[Optional[str]] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    visitas: Mapped[list["Visita"]] = relationship("Visita", back_populates="empresa", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "pais": self.pais or "",
            "ciudad": self.ciudad or "",
            "industria": self.industria or "",
            "tamano": self.tamano or "",
            "web": self.web or "",
            "tel": self.tel or "",
            "sector": self.sector or "",
            "dir": self.dir or "",
            "desc": self.desc or "",
            "cert": self.cert or "",
            "notas": self.notas or "",
            "emoji": self.emoji or "🏢",
        }


class Visita(Base):
    __tablename__ = "visitas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("empresas.id"), nullable=False)
    fecha: Mapped[Optional[str]] = mapped_column(String(20))
    lugar: Mapped[Optional[str]] = mapped_column(String(200))
    participantes: Mapped[Optional[str]] = mapped_column(Text)
    objetivo: Mapped[Optional[str]] = mapped_column(Text)
    agenda: Mapped[Optional[str]] = mapped_column(Text)
    notas: Mapped[Optional[str]] = mapped_column(Text)
    proximos: Mapped[Optional[str]] = mapped_column(Text)
    estado: Mapped[Optional[str]] = mapped_column(String(20), default="draft")
    visitante_nombre: Mapped[Optional[str]] = mapped_column(String(200))
    visitante_cargo: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="visitas")
    hallazgos: Mapped[list["Hallazgo"]] = relationship("Hallazgo", back_populates="visita", cascade="all, delete-orphan")
    contactos: Mapped[list["Contacto"]] = relationship("Contacto", back_populates="visita", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "emp_id": self.emp_id,
            "fecha": self.fecha or "",
            "lugar": self.lugar or "",
            "part": self.participantes or "",
            "obj": self.objetivo or "",
            "agenda": self.agenda or "",
            "notas": self.notas or "",
            "prox": self.proximos or "",
            "estado": self.estado or "draft",
            "visitante": self.visitante_nombre or "",
            "cargo": self.visitante_cargo or "",
        }


class Hallazgo(Base):
    __tablename__ = "hallazgos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vis_id: Mapped[int] = mapped_column(Integer, ForeignKey("visitas.id"), nullable=False)
    desc: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[Optional[str]] = mapped_column(String(30))
    impacto: Mapped[Optional[str]] = mapped_column(String(20))
    categorias: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    visita: Mapped["Visita"] = relationship("Visita", back_populates="hallazgos")
    oportunidades: Mapped[list["Oportunidad"]] = relationship("Oportunidad", back_populates="hallazgo", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "vis_id": self.vis_id,
            "desc": self.desc or "",
            "tipo": self.tipo or "practica",
            "impacto": self.impacto or "medio",
            "cats": self.categorias or "",
        }


class Oportunidad(Base):
    __tablename__ = "oportunidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hall_id: Mapped[int] = mapped_column(Integer, ForeignKey("hallazgos.id"), nullable=False)
    titulo: Mapped[Optional[str]] = mapped_column(String(300))
    desc: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[Optional[str]] = mapped_column(String(30))
    plazo: Mapped[Optional[str]] = mapped_column(String(20))
    estado: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    hallazgo: Mapped["Hallazgo"] = relationship("Hallazgo", back_populates="oportunidades")

    def to_dict(self):
        return {
            "id": self.id,
            "hall_id": self.hall_id,
            "titulo": self.titulo or "",
            "desc": self.desc or "",
            "tipo": self.tipo or "ec",
            "plazo": self.plazo or "corto",
            "estado": self.estado or "pendiente",
        }


class Contacto(Base):
    __tablename__ = "contactos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vis_id: Mapped[int] = mapped_column(Integer, ForeignKey("visitas.id"), nullable=False)
    nombre: Mapped[Optional[str]] = mapped_column(String(200))
    cargo: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(200))
    tel: Mapped[Optional[str]] = mapped_column(String(60))
    notas: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    visita: Mapped["Visita"] = relationship("Visita", back_populates="contactos")

    def to_dict(self):
        return {
            "id": self.id,
            "vis_id": self.vis_id,
            "nombre": self.nombre or "",
            "cargo": self.cargo or "",
            "email": self.email or "",
            "tel": self.tel or "",
            "notas": self.notas or "",
        }


# ─────────────────────────────────────────────
#  Rutas de la API
# ─────────────────────────────────────────────

def register_routes(app: Flask):

    # ── Servir la SPA ──
    @app.route("/")
    @app.route("/<path:path>")
    def serve_spa(path=""):
        if path and path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404
        static_file = os.path.join(app.static_folder, path)
        if path and os.path.isfile(static_file):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    # ────── EMPRESAS ──────
    @app.route("/api/empresas", methods=["GET"])
    def get_empresas():
        empresas = db.session.execute(db.select(Empresa).order_by(Empresa.id)).scalars().all()
        return jsonify([e.to_dict() for e in empresas])

    @app.route("/api/empresas", methods=["POST"])
    def create_empresa():
        data = request.json
        e = Empresa(
            nombre=data.get("nombre", "").strip(),
            pais=data.get("pais", ""),
            ciudad=data.get("ciudad", ""),
            industria=data.get("industria", ""),
            tamano=data.get("tamano", ""),
            web=data.get("web", ""),
            tel=data.get("tel", ""),
            sector=data.get("sector", ""),
            dir=data.get("dir", ""),
            desc=data.get("desc", ""),
            cert=data.get("cert", ""),
            notas=data.get("notas", ""),
            emoji=data.get("emoji", "🏢"),
        )
        db.session.add(e)
        db.session.commit()
        return jsonify(e.to_dict()), 201

    @app.route("/api/empresas/<int:eid>", methods=["PUT"])
    def update_empresa(eid):
        e = db.get_or_404(Empresa, eid)
        data = request.json
        for field in ["nombre","pais","ciudad","industria","tamano","web","tel","sector","dir","desc","cert","notas","emoji"]:
            if field in data:
                setattr(e, field, data[field])
        db.session.commit()
        return jsonify(e.to_dict())

    @app.route("/api/empresas/<int:eid>", methods=["DELETE"])
    def delete_empresa(eid):
        e = db.get_or_404(Empresa, eid)
        db.session.delete(e)
        db.session.commit()
        return jsonify({"ok": True})

    # ────── VISITAS ──────
    @app.route("/api/visitas", methods=["GET"])
    def get_visitas():
        visitas = db.session.execute(db.select(Visita).order_by(Visita.id)).scalars().all()
        return jsonify([v.to_dict() for v in visitas])

    @app.route("/api/visitas", methods=["POST"])
    def create_visita():
        data = request.json
        v = Visita(
            emp_id=data["emp_id"],
            fecha=data.get("fecha", ""),
            lugar=data.get("lugar", ""),
            participantes=data.get("part", ""),
            objetivo=data.get("obj", ""),
            agenda=data.get("agenda", ""),
            notas=data.get("notas", ""),
            proximos=data.get("prox", ""),
            estado=data.get("estado", "draft"),
            visitante_nombre=data.get("visitante", ""),
            visitante_cargo=data.get("cargo", ""),
        )
        db.session.add(v)
        db.session.commit()
        return jsonify(v.to_dict()), 201

    @app.route("/api/visitas/<int:vid>", methods=["PUT"])
    def update_visita(vid):
        v = db.get_or_404(Visita, vid)
        data = request.json
        mapping = {"emp_id":"emp_id","fecha":"fecha","lugar":"lugar","part":"participantes",
                   "obj":"objetivo","agenda":"agenda","notas":"notas","prox":"proximos",
                   "estado":"estado","visitante":"visitante_nombre","cargo":"visitante_cargo"}
        for key, attr in mapping.items():
            if key in data:
                setattr(v, attr, data[key])
        db.session.commit()
        return jsonify(v.to_dict())

    @app.route("/api/visitas/<int:vid>", methods=["DELETE"])
    def delete_visita(vid):
        v = db.get_or_404(Visita, vid)
        db.session.delete(v)
        db.session.commit()
        return jsonify({"ok": True})

    # ────── HALLAZGOS ──────
    @app.route("/api/hallazgos", methods=["GET"])
    def get_hallazgos():
        hallazgos = db.session.execute(db.select(Hallazgo).order_by(Hallazgo.id)).scalars().all()
        return jsonify([h.to_dict() for h in hallazgos])

    @app.route("/api/hallazgos", methods=["POST"])
    def create_hallazgo():
        data = request.json
        h = Hallazgo(
            vis_id=data["vis_id"],
            desc=data.get("desc", ""),
            tipo=data.get("tipo", "practica"),
            impacto=data.get("impacto", "medio"),
            categorias=data.get("cats", ""),
        )
        db.session.add(h)
        db.session.commit()
        return jsonify(h.to_dict()), 201

    @app.route("/api/hallazgos/<int:hid>", methods=["PUT"])
    def update_hallazgo(hid):
        h = db.get_or_404(Hallazgo, hid)
        data = request.json
        for field, attr in [("desc","desc"),("tipo","tipo"),("impacto","impacto"),("cats","categorias")]:
            if field in data:
                setattr(h, attr, data[field])
        db.session.commit()
        return jsonify(h.to_dict())

    @app.route("/api/hallazgos/<int:hid>", methods=["DELETE"])
    def delete_hallazgo(hid):
        h = db.get_or_404(Hallazgo, hid)
        db.session.delete(h)
        db.session.commit()
        return jsonify({"ok": True})

    # ────── OPORTUNIDADES ──────
    @app.route("/api/oportunidades", methods=["GET"])
    def get_oportunidades():
        oportunidades = db.session.execute(db.select(Oportunidad).order_by(Oportunidad.id)).scalars().all()
        return jsonify([o.to_dict() for o in oportunidades])

    @app.route("/api/oportunidades", methods=["POST"])
    def create_oportunidad():
        data = request.json
        o = Oportunidad(
            hall_id=data["hall_id"],
            titulo=data.get("titulo", ""),
            desc=data.get("desc", ""),
            tipo=data.get("tipo", "ec"),
            plazo=data.get("plazo", "corto"),
            estado=data.get("estado", "pendiente"),
        )
        db.session.add(o)
        db.session.commit()
        return jsonify(o.to_dict()), 201

    @app.route("/api/oportunidades/<int:oid>", methods=["PUT"])
    def update_oportunidad(oid):
        o = db.get_or_404(Oportunidad, oid)
        data = request.json
        for field in ["titulo","desc","tipo","plazo","estado"]:
            if field in data:
                setattr(o, field, data[field])
        db.session.commit()
        return jsonify(o.to_dict())

    @app.route("/api/oportunidades/<int:oid>", methods=["DELETE"])
    def delete_oportunidad(oid):
        o = db.get_or_404(Oportunidad, oid)
        db.session.delete(o)
        db.session.commit()
        return jsonify({"ok": True})

    # ────── CONTACTOS ──────
    @app.route("/api/contactos", methods=["GET"])
    def get_contactos():
        contactos = db.session.execute(db.select(Contacto).order_by(Contacto.id)).scalars().all()
        return jsonify([c.to_dict() for c in contactos])

    @app.route("/api/contactos", methods=["POST"])
    def create_contacto():
        data = request.json
        c = Contacto(
            vis_id=data["vis_id"],
            nombre=data.get("nombre", ""),
            cargo=data.get("cargo", ""),
            email=data.get("email", ""),
            tel=data.get("tel", ""),
            notas=data.get("notas", ""),
        )
        db.session.add(c)
        db.session.commit()
        return jsonify(c.to_dict()), 201

    @app.route("/api/contactos/<int:cid>", methods=["PUT"])
    def update_contacto(cid):
        c = db.get_or_404(Contacto, cid)
        data = request.json
        for field in ["nombre","cargo","email","tel","notas"]:
            if field in data:
                setattr(c, field, data[field])
        db.session.commit()
        return jsonify(c.to_dict())

    @app.route("/api/contactos/<int:cid>", methods=["DELETE"])
    def delete_contacto(cid):
        c = db.get_or_404(Contacto, cid)
        db.session.delete(c)
        db.session.commit()
        return jsonify({"ok": True})

    # ────── EXPORTAR / IMPORTAR ──────
    @app.route("/api/export", methods=["GET"])
    def export_all():
        empresas = db.session.execute(db.select(Empresa)).scalars().all()
        visitas = db.session.execute(db.select(Visita)).scalars().all()
        hallazgos = db.session.execute(db.select(Hallazgo)).scalars().all()
        oportunidades = db.session.execute(db.select(Oportunidad)).scalars().all()
        contactos = db.session.execute(db.select(Contacto)).scalars().all()
        return jsonify({
            "meta": {
                "version": "2.0",
                "app": "VisitaLab",
                "exportedAt": datetime.now(timezone.utc).isoformat(),
                "counts": {
                    "empresas": len(empresas),
                    "visitas": len(visitas),
                    "hallazgos": len(hallazgos),
                    "oportunidades": len(oportunidades),
                    "contactos": len(contactos),
                }
            },
            "empresas": [e.to_dict() for e in empresas],
            "visitas": [v.to_dict() for v in visitas],
            "hallazgos": [h.to_dict() for h in hallazgos],
            "oportunidades": [o.to_dict() for o in oportunidades],
            "contactos": [c.to_dict() for c in contactos],
        })

    @app.route("/api/import", methods=["POST"])
    def import_all():
        data = request.json
        mode = data.get("mode", "agregar")  # "agregar" | "sobreescribir"

        if mode == "sobreescribir":
            # Borrar todo en orden (FK constraints)
            db.session.execute(db.delete(Oportunidad))
            db.session.execute(db.delete(Contacto))
            db.session.execute(db.delete(Hallazgo))
            db.session.execute(db.delete(Visita))
            db.session.execute(db.delete(Empresa))
            db.session.commit()

        # Calcular offsets para modo agregar
        emp_off = (db.session.execute(db.select(db.func.max(Empresa.id))).scalar() or 0)
        vis_off = (db.session.execute(db.select(db.func.max(Visita.id))).scalar() or 0)
        hal_off = (db.session.execute(db.select(db.func.max(Hallazgo.id))).scalar() or 0)
        opo_off = (db.session.execute(db.select(db.func.max(Oportunidad.id))).scalar() or 0)
        con_off = (db.session.execute(db.select(db.func.max(Contacto.id))).scalar() or 0)

        emp_map = {}
        for ed in data.get("empresas", []):
            new_id = ed["id"] + emp_off
            emp_map[ed["id"]] = new_id
            e = Empresa(id=new_id, nombre=ed.get("nombre",""), pais=ed.get("pais",""),
                ciudad=ed.get("ciudad",""), industria=ed.get("industria",""),
                tamano=ed.get("tamano",""), web=ed.get("web",""), tel=ed.get("tel",""),
                sector=ed.get("sector",""), dir=ed.get("dir",""), desc=ed.get("desc",""),
                cert=ed.get("cert",""), notas=ed.get("notas",""), emoji=ed.get("emoji","🏢"))
            db.session.add(e)

        vis_map = {}
        for vd in data.get("visitas", []):
            new_id = vd["id"] + vis_off
            vis_map[vd["id"]] = new_id
            v = Visita(id=new_id, emp_id=emp_map.get(vd["emp_id"], vd["emp_id"]),
                fecha=vd.get("fecha",""), lugar=vd.get("lugar",""),
                participantes=vd.get("part",""), objetivo=vd.get("obj",""),
                agenda=vd.get("agenda",""), notas=vd.get("notas",""),
                proximos=vd.get("prox",""), estado=vd.get("estado","draft"),
                visitante_nombre=vd.get("visitante",""), visitante_cargo=vd.get("cargo",""))
            db.session.add(v)

        hal_map = {}
        for hd in data.get("hallazgos", []):
            new_id = hd["id"] + hal_off
            hal_map[hd["id"]] = new_id
            h = Hallazgo(id=new_id, vis_id=vis_map.get(hd["vis_id"], hd["vis_id"]),
                desc=hd.get("desc",""), tipo=hd.get("tipo","practica"),
                impacto=hd.get("impacto","medio"), categorias=hd.get("cats",""))
            db.session.add(h)

        for od in data.get("oportunidades", []):
            o = Oportunidad(id=od["id"] + opo_off,
                hall_id=hal_map.get(od["hall_id"], od["hall_id"]),
                titulo=od.get("titulo",""), desc=od.get("desc",""),
                tipo=od.get("tipo","ec"), plazo=od.get("plazo","corto"),
                estado=od.get("estado","pendiente"))
            db.session.add(o)

        for cd in data.get("contactos", []):
            c = Contacto(id=cd["id"] + con_off,
                vis_id=vis_map.get(cd["vis_id"], cd["vis_id"]),
                nombre=cd.get("nombre",""), cargo=cd.get("cargo",""),
                email=cd.get("email",""), tel=cd.get("tel",""),
                notas=cd.get("notas",""))
            db.session.add(c)

        db.session.commit()
        return jsonify({"ok": True, "mode": mode})

    # ────── VACIAR ──────
    @app.route("/api/vaciar/<string:tabla>", methods=["DELETE"])
    def vaciar_tabla(tabla):
        if tabla == "visitas":
            db.session.execute(db.delete(Oportunidad))
            db.session.execute(db.delete(Contacto))
            db.session.execute(db.delete(Hallazgo))
            db.session.execute(db.delete(Visita))
        elif tabla == "empresas":
            db.session.execute(db.delete(Empresa))
        elif tabla == "hallazgos":
            db.session.execute(db.delete(Oportunidad))
            db.session.execute(db.delete(Hallazgo))
        elif tabla == "oportunidades":
            db.session.execute(db.delete(Oportunidad))
        elif tabla == "todo":
            db.session.execute(db.delete(Oportunidad))
            db.session.execute(db.delete(Contacto))
            db.session.execute(db.delete(Hallazgo))
            db.session.execute(db.delete(Visita))
            db.session.execute(db.delete(Empresa))
        else:
            return jsonify({"error": "Tabla no reconocida"}), 400
        db.session.commit()
        return jsonify({"ok": True})

    # ────── HEALTH CHECK ──────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
