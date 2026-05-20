import os
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///rekru_profiles.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text, nullable=False)
    primary_cta = db.Column(db.String(80), nullable=False)
    highlight_text = db.Column(db.String(120), nullable=False)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    skill = db.Column(db.String(160), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login ke dashboard terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def seed_database():
    default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin12345")

    if not User.query.filter_by(username=default_username).first():
        db.session.add(
            User(
                username=default_username,
                password_hash=generate_password_hash(default_password),
            )
        )

    if not SiteContent.query.first():
        db.session.add(
            SiteContent(
                title="Profil Kelompok Rekru",
                subtitle="Tim kecil dengan energi besar untuk membangun produk digital.",
                description=(
                    "Kenali anggota kelompok, peran utama, keahlian, dan fokus kerja "
                    "mereka dalam satu halaman profil yang rapi dan mudah diperbarui."
                ),
                primary_cta="Lihat anggota",
                highlight_text="4 anggota aktif",
            )
        )

    if Member.query.count() == 0:
        members = [
            Member(
                name="Alya Prameswari",
                role="Project Lead",
                location="Jakarta",
                skill="Riset pengguna, perencanaan sprint, komunikasi tim",
                bio=(
                    "Mengatur arah pengerjaan proyek, memastikan kebutuhan pengguna "
                    "dipahami, dan menjaga ritme kerja kelompok tetap jelas."
                ),
                image_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80",
                display_order=1,
                is_featured=True,
            ),
            Member(
                name="Bima Santoso",
                role="Backend Developer",
                location="Bandung",
                skill="Python, database SQL, API service",
                bio=(
                    "Membangun struktur data, endpoint aplikasi, dan integrasi database "
                    "agar konten dapat dikelola dari dashboard."
                ),
                image_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=80",
                display_order=2,
                is_featured=True,
            ),
            Member(
                name="Citra Lestari",
                role="UI Designer",
                location="Yogyakarta",
                skill="Desain antarmuka, layout responsif, visual system",
                bio=(
                    "Merancang tampilan home agar informasi profil terasa modern, "
                    "menarik, dan nyaman dibaca di berbagai ukuran layar."
                ),
                image_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=900&q=80",
                display_order=3,
                is_featured=False,
            ),
            Member(
                name="Dimas Wicaksono",
                role="QA & Documentation",
                location="Surabaya",
                skill="Testing, dokumentasi, deployment Docker",
                bio=(
                    "Mengecek alur aplikasi, menulis dokumentasi penggunaan, dan "
                    "memastikan proyek mudah dijalankan dengan Docker Compose."
                ),
                image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=80",
                display_order=4,
                is_featured=False,
            ),
        ]
        db.session.add_all(members)

    db.session.commit()


def init_database():
    try:
        db.create_all()
        seed_database()
    except OperationalError:
        app.logger.exception("Database belum siap.")
        raise


with app.app_context():
    init_database()


@app.route("/")
def home():
    content = SiteContent.query.first()
    members = Member.query.order_by(Member.display_order.asc(), Member.name.asc()).all()
    featured = [member for member in members if member.is_featured]
    return render_template(
        "home.html", content=content, members=members, featured=featured
    )


@app.route("/dashboard/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login berhasil.", "success")
            return redirect(url_for("dashboard"))

        flash("Username atau password salah.", "danger")

    return render_template("login.html")


@app.route("/dashboard/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Anda sudah logout.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    content = SiteContent.query.first()
    members = Member.query.order_by(Member.display_order.asc(), Member.name.asc()).all()
    return render_template("dashboard.html", content=content, members=members)


@app.route("/dashboard/content", methods=["POST"])
@login_required
def update_content():
    content = SiteContent.query.first()
    content.title = request.form.get("title", "").strip()
    content.subtitle = request.form.get("subtitle", "").strip()
    content.description = request.form.get("description", "").strip()
    content.primary_cta = request.form.get("primary_cta", "").strip()
    content.highlight_text = request.form.get("highlight_text", "").strip()
    db.session.commit()
    flash("Konten home berhasil diperbarui.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/members", methods=["POST"])
@login_required
def create_member():
    try:
        member = Member(
            name=request.form.get("name", "").strip(),
            role=request.form.get("role", "").strip(),
            location=request.form.get("location", "").strip(),
            skill=request.form.get("skill", "").strip(),
            bio=request.form.get("bio", "").strip(),
            image_url=request.form.get("image_url", "").strip(),
            display_order=int(request.form.get("display_order") or 0),
            is_featured=bool(request.form.get("is_featured")),
        )
        db.session.add(member)
        db.session.commit()
        flash("Anggota baru berhasil ditambahkan.", "success")
        
    except Exception as e:
        # Rollback membatalkan transaksi yang error agar DB tidak nyangkut
        db.session.rollback() 
        flash("Gagal menambahkan data! Pastikan teks tidak terlalu panjang.", "danger")
        app.logger.error(f"Database error: {e}")

    return redirect(url_for("dashboard"))

@app.route("/dashboard/members/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)

    if request.method == "POST":
        member.name = request.form.get("name", "").strip()
        member.role = request.form.get("role", "").strip()
        member.location = request.form.get("location", "").strip()
        member.skill = request.form.get("skill", "").strip()
        member.bio = request.form.get("bio", "").strip()
        member.image_url = request.form.get("image_url", "").strip()
        member.display_order = int(request.form.get("display_order") or 0)
        member.is_featured = bool(request.form.get("is_featured"))
        db.session.commit()
        flash("Data anggota berhasil diperbarui.", "success")
        return redirect(url_for("dashboard"))

    return render_template("member_form.html", member=member)


@app.route("/dashboard/members/<int:member_id>/delete", methods=["POST"])
@login_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash("Data anggota berhasil dihapus.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
