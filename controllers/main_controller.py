from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.db_helpers import fetch_records, execute_query

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("login.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        password = generate_password_hash(password)

        query = """
            INSERT INTO users (name, email, password, role)
            VALUES (:name, :email, :password, :role)
        """

        from models.db_helpers import execute_query

        try:
            execute_query(
                query,
                {
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": role
                }
            )

            return redirect(url_for("main.home"))

        except Exception as e:
            return f"Registration failed: {e}", 400

    return render_template("register.html")


@main_bp.route("/login", methods=["POST"])

@main_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    query = """
        SELECT id, name, email, password, role
        FROM users
        WHERE email = :email
    """

    users = fetch_records(query, {
        "email": email
    })

    if not users:
        return "Invalid email or password", 401

    user = users[0]

    if not check_password_hash(user["password"], password):
        return "Invalid email or password", 401

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["role"] = user["role"]

    if user["role"] == "Admin":
        return redirect(url_for("main.admin_dashboard"))

    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@main_bp.route("/services")
def services():
    services = fetch_records("""
        SELECT id, service_name, category, description, status
        FROM services
    """)

    print("SERVICES:", services)

    return render_template("services.html", services=services)

@main_bp.route("/request-service/<int:service_id>")
def request_service(service_id):
    if "user_id" not in session:
        return redirect(url_for("main.home"))

    user_id = session["user_id"]

    execute_query("""
        INSERT INTO service_requests (user_id, service_id, status)
        VALUES (:user_id, :service_id, 'pending')
    """, {
        "user_id": user_id,
        "service_id": service_id
    })

    return redirect(url_for("main.service_requests"))

@main_bp.route("/service-requests")
def service_requests():
    if "user_id" not in session:
        return redirect(url_for("main.home"))

    requests = fetch_records("""
        SELECT
            sr.id,
            s.service_name,
            s.category,
            sr.status
        FROM service_requests sr
        JOIN services s ON sr.service_id = s.id
        WHERE sr.user_id = :user_id
        ORDER BY sr.id DESC
    """, {
        "user_id": session["user_id"]
    })

    return render_template("service_requests.html", requests=requests)
@main_bp.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("main.home"))

    if session.get("role") != "Admin":
        return "Access denied. Admins only.", 403

    requests = fetch_records("""
        SELECT
            sr.id,
            u.name AS user_name,
            u.email,
            s.service_name,
            sr.request_date,
            sr.status
        FROM service_requests sr
        JOIN users u ON sr.user_id = u.id
        JOIN services s ON sr.service_id = s.id
        ORDER BY sr.id DESC
    """)

    return render_template(
        "admin_dashboard.html",
        requests=requests
    )
    requests = fetch_records("""
        SELECT
            sr.id,
            u.name AS user_name,
            u.email,
            s.service_name,
            sr.request_date,
            sr.status
        FROM service_requests sr
        JOIN users u ON sr.user_id = u.id
        JOIN services s ON sr.service_id = s.id
        ORDER BY sr.id DESC
    """)

    return render_template(
        "admin_dashboard.html",
        requests=requests
    )
@main_bp.route("/admin/request/<int:request_id>/status", methods=["POST"])
def update_request_status(request_id):
    if "user_id" not in session:
        return redirect(url_for("main.home"))

    if session.get("role") != "Admin":
        return "Access denied. Admins only.", 403

    status = request.form.get("status")

    # Get the current request information
    request_data = fetch_records("""
        SELECT user_id, service_id, status
        FROM service_requests
        WHERE id = :request_id
    """, {
        "request_id": request_id
    })

    if not request_data:
        return "Service request not found.", 404

    old_status = request_data[0]["status"]

    # Update the service request status
    execute_query("""
        UPDATE service_requests
        SET status = :status
        WHERE id = :request_id
    """, {
        "status": status,
        "request_id": request_id
    })

    # Add to history only when the request changes
    # from a non-completed status to completed
    if status == "completed" and old_status != "completed":
        execute_query("""
            INSERT INTO service_history
            (user_id, service_id, completion_date, status)
            VALUES
            (:user_id, :service_id, NOW(), 'completed')
        """, {
            "user_id": request_data[0]["user_id"],
            "service_id": request_data[0]["service_id"]
        })

    return redirect(url_for("main.admin_dashboard"))
@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.home"))
@main_bp.route("/service-history")
def service_history():
    if "user_id" not in session:
        return redirect(url_for("main.home"))

    history = fetch_records("""
        SELECT
            sh.id,
            s.service_name,
            s.category,
            sh.completion_date,
            sh.status
        FROM service_history sh
        JOIN services s ON sh.service_id = s.id
        WHERE sh.user_id = :user_id
        ORDER BY sh.id DESC
    """, {
        "user_id": session["user_id"]
    })

    return render_template(
        "service_history.html",
        history=history
    )