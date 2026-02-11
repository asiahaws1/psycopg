from flask import Flask, jsonify, request
import psycopg2
import os

database_name = os.environ.get('DATABASE_NAME')
app_host = os.environ.get('APP_HOST')
app_port = os.environ.get('APP_PORT')

conn = psycopg2.connect(f"dbname={database_name}")
cursor = conn.cursor()

def get_conn():
    return db.get_connection()


app = Flask(__name__)


@app.route("/company", methods=["POST"])
def create_company():
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Companies (company_name, active) VALUES (%s, %s) RETURNING company_id, company_name, active;",
        (data.get("company_name"), data.get("active", True)),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "company created",
        "results": {"company_id": row[0], "company_name": row[1], "active": row[2]},
    }), 201


@app.route("/category", methods=["POST"])
def create_category():
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Categories (category_name) VALUES (%s) RETURNING category_id, category_name;",
        (data.get("category_name"),),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "category created",
        "results": {"category_id": row[0], "category_name": row[1]},
    }), 201


@app.route("/product", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Products (product_name, company_id, description, price, active) VALUES (%s, %s, %s, %s, %s) RETURNING product_id, product_name, company_id, description, price, active;",
        (
            data.get("product_name"),
            data.get("company_id"),
            data.get("description"),
            data.get("price"),
            data.get("active", True),
        ),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    price_val = float(row[4]) if row[4] is not None else None
    return jsonify({
        "message": "product created",
        "results": {
            "product_id": row[0],
            "product_name": row[1],
            "company_id": row[2],
            "description": row[3],
            "price": price_val,
            "active": row[5],
        },
    }), 201


@app.route("/warranty", methods=["POST"])
def create_warranty():
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Warranties (warranty_months, product_id) VALUES (%s, %s) RETURNING warranty_id, warranty_months;",
        (data.get("warranty_months"), data.get("product_id")),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "warranty created",
        "results": {"warranty_id": row[0], "warranty_months": row[1]},
    }), 201


@app.route("/product/category", methods=["POST"])
def create_product_category_xref():
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ProductsCategoriesXref (product_id, category_id) VALUES (%s, %s) RETURNING product_id, category_id;",
        (data.get("product_id"), data.get("category_id")),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "product/category association created",
        "results": {"product_id": row[0], "category_id": row[1]},
    }), 201


@app.route("/companies", methods=["GET"])
def get_companies():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT company_id, company_name, active FROM Companies ORDER BY company_id;")
    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append({"company_id": r[0], "company_name": r[1], "active": r[2]})
    cur.close()
    conn.close()
    return jsonify({"message": "companies found", "results": results}), 200


@app.route("/categories", methods=["GET"])
def get_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT category_id, category_name FROM Categories ORDER BY category_id;")
    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append({"category_id": r[0], "category_name": r[1]})
    cur.close()
    conn.close()
    return jsonify({"message": "categories found", "results": results}), 200


@app.route("/products", methods=["GET"])
def get_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT product_id, product_name, company_id, description, price, active FROM Products ORDER BY product_id;")
    rows = cur.fetchall()
    results = []
    for r in rows:
        product = {
            "product_id": r[0],
            "product_name": r[1],
            "company_id": r[2],
            "description": r[3],
            "price": float(r[4]) if r[4] is not None else None,
            "active": r[5],
        }
        pid = product["product_id"]
        cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE product_id = %s;", (pid,))
        w = cur.fetchone()
        if w:
            product["warranty"] = {"warranty_id": w[0], "warranty_months": w[1]}
        else:
            product["warranty"] = None
        cur.execute(
            "SELECT c.category_id, c.category_name FROM Categories c JOIN ProductsCategoriesXref x ON x.category_id = c.category_id WHERE x.product_id = %s;",
            (pid,),
        )
        cat_rows = cur.fetchall()
        categories = []
        for cat in cat_rows:
            categories.append({"category_id": cat[0], "category_name": cat[1]})
        product["categories"] = categories
        results.append(product)
    cur.close()
    conn.close()
    return jsonify({"message": "products found", "results": results}), 200


@app.route("/products/active", methods=["GET"])
def get_products_active():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT product_id, product_name, company_id, description, price, active FROM Products WHERE active = TRUE ORDER BY product_id;")
    rows = cur.fetchall()
    results = []
    for r in rows:
        product = {
            "product_id": r[0],
            "product_name": r[1],
            "company_id": r[2],
            "description": r[3],
            "price": float(r[4]) if r[4] is not None else None,
            "active": r[5],
        }
        pid = product["product_id"]
        cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE product_id = %s;", (pid,))
        w = cur.fetchone()
        if w:
            product["warranty"] = {"warranty_id": w[0], "warranty_months": w[1]}
        else:
            product["warranty"] = None
        cur.execute(
            "SELECT c.category_id, c.category_name FROM Categories c JOIN ProductsCategoriesXref x ON x.category_id = c.category_id WHERE x.product_id = %s;",
            (pid,),
        )
        cat_rows = cur.fetchall()
        categories = []
        for cat in cat_rows:
            categories.append({"category_id": cat[0], "category_name": cat[1]})
        product["categories"] = categories
        results.append(product)
    cur.close()
    conn.close()
    return jsonify({"message": "active products found", "results": results}), 200


@app.route("/company/<int:company_id>", methods=["GET", "PUT"])
def company_by_id(company_id):
    conn = get_conn()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT company_id, company_name, active FROM Companies WHERE company_id = %s;", (company_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "company not found", "results": None}), 404
        return jsonify({
            "message": "company found",
            "results": {"company_id": row[0], "company_name": row[1], "active": row[2]},
        }), 200
    if request.method == "PUT":
        data = request.get_json() or {}
        updates = []
        args = []
        if "company_name" in data:
            updates.append("company_name = %s")
            args.append(data["company_name"])
        if "active" in data:
            updates.append("active = %s")
            args.append(data["active"])
        if not updates:
            cur.execute("SELECT company_id, company_name, active FROM Companies WHERE company_id = %s;", (company_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return jsonify({"message": "company not found", "results": None}), 404
            return jsonify({
                "message": "company unchanged",
                "results": {"company_id": row[0], "company_name": row[1], "active": row[2]},
            }), 200
        args.append(company_id)
        query = "UPDATE Companies SET " + ", ".join(updates) + " WHERE company_id = %s RETURNING company_id, company_name, active;"
        cur.execute(query, args)
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "company not found", "results": None}), 404
        return jsonify({
            "message": "company updated",
            "results": {"company_id": row[0], "company_name": row[1], "active": row[2]},
        }), 200


@app.route("/category/<int:category_id>", methods=["GET", "PUT"])
def category_by_id(category_id):
    conn = get_conn()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT category_id, category_name FROM Categories WHERE category_id = %s;", (category_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "category not found", "results": None}), 404
        return jsonify({
            "message": "category found",
            "results": {"category_id": row[0], "category_name": row[1]},
        }), 200
    if request.method == "PUT":
        data = request.get_json() or {}
        if "category_name" not in data:
            cur.execute("SELECT category_id, category_name FROM Categories WHERE category_id = %s;", (category_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return jsonify({"message": "category not found", "results": None}), 404
            return jsonify({
                "message": "category unchanged",
                "results": {"category_id": row[0], "category_name": row[1]},
            }), 200
        cur.execute(
            "UPDATE Categories SET category_name = %s WHERE category_id = %s RETURNING category_id, category_name;",
            (data["category_name"], category_id),
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "category not found", "results": None}), 404
        return jsonify({
            "message": "category updated",
            "results": {"category_id": row[0], "category_name": row[1]},
        }), 200


@app.route("/product/<int:product_id>", methods=["GET", "PUT"])
def product_by_id(product_id):
    conn = get_conn()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT product_id, product_name, company_id, description, price, active FROM Products WHERE product_id = %s;",
            (product_id,),
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return jsonify({"message": "product not found", "results": None}), 404
        product = {
            "product_id": row[0],
            "product_name": row[1],
            "company_id": row[2],
            "description": row[3],
            "price": float(row[4]) if row[4] is not None else None,
            "active": row[5],
        }
        cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE product_id = %s;", (product_id,))
        w = cur.fetchone()
        if w:
            product["warranty"] = {"warranty_id": w[0], "warranty_months": w[1]}
        else:
            product["warranty"] = None
        cur.execute(
            "SELECT c.category_id, c.category_name FROM Categories c JOIN ProductsCategoriesXref x ON x.category_id = c.category_id WHERE x.product_id = %s;",
            (product_id,),
        )
        cat_rows = cur.fetchall()
        categories = []
        for cat in cat_rows:
            categories.append({"category_id": cat[0], "category_name": cat[1]})
        product["categories"] = categories
        cur.close()
        conn.close()
        return jsonify({
            "message": "product found",
            "results": product,
        }), 200
    if request.method == "PUT":
        data = request.get_json() or {}
        updates = []
        args = []
        if "product_name" in data:
            updates.append("product_name = %s")
            args.append(data["product_name"])
        if "company_id" in data:
            updates.append("company_id = %s")
            args.append(data["company_id"])
        if "description" in data:
            updates.append("description = %s")
            args.append(data["description"])
        if "price" in data:
            updates.append("price = %s")
            args.append(data["price"])
        if "active" in data:
            updates.append("active = %s")
            args.append(data["active"])
        if not updates:
            cur.execute(
                "SELECT product_id, product_name, company_id, description, price, active FROM Products WHERE product_id = %s;",
                (product_id,),
            )
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return jsonify({"message": "product not found", "results": None}), 404
            product = {
                "product_id": row[0],
                "product_name": row[1],
                "company_id": row[2],
                "description": row[3],
                "price": float(row[4]) if row[4] is not None else None,
                "active": row[5],
            }
            return jsonify({
                "message": "product unchanged",
                "results": product,
            }), 200
        args.append(product_id)
        query = "UPDATE Products SET " + ", ".join(updates) + " WHERE product_id = %s RETURNING product_id, product_name, company_id, description, price, active;"
        cur.execute(query, args)
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "product not found", "results": None}), 404
        product = {
            "product_id": row[0],
            "product_name": row[1],
            "company_id": row[2],
            "description": row[3],
            "price": float(row[4]) if row[4] is not None else None,
            "active": row[5],
        }
        return jsonify({
            "message": "product updated",
            "results": product,
        }), 200


@app.route("/warranty/<int:warranty_id>", methods=["GET", "PUT"])
def warranty_by_id(warranty_id):
    conn = get_conn()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE warranty_id = %s;", (warranty_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "warranty not found", "results": None}), 404
        return jsonify({
            "message": "warranty found",
            "results": {"warranty_id": row[0], "warranty_months": row[1]},
        }), 200
    if request.method == "PUT":
        data = request.get_json() or {}
        if "warranty_months" not in data:
            cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE warranty_id = %s;", (warranty_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return jsonify({"message": "warranty not found", "results": None}), 404
            return jsonify({
                "message": "warranty unchanged",
                "results": {"warranty_id": row[0], "warranty_months": row[1]},
            }), 200
        cur.execute(
            "UPDATE Warranties SET warranty_months = %s WHERE warranty_id = %s RETURNING warranty_id, warranty_months;",
            (data["warranty_months"], warranty_id),
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"message": "warranty not found", "results": None}), 404
        return jsonify({
            "message": "warranty updated",
            "results": {"warranty_id": row[0], "warranty_months": row[1]},
        }), 200


@app.route("/product/company/<int:company_id>", methods=["GET"])
def get_products_by_company(company_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT product_id, product_name, company_id, description, price, active FROM Products WHERE company_id = %s ORDER BY product_id;",
        (company_id,),
    )
    rows = cur.fetchall()
    results = []
    for r in rows:
        product = {
            "product_id": r[0],
            "product_name": r[1],
            "company_id": r[2],
            "description": r[3],
            "price": float(r[4]) if r[4] is not None else None,
            "active": r[5],
        }
        pid = product["product_id"]
        cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE product_id = %s;", (pid,))
        w = cur.fetchone()
        if w:
            product["warranty"] = {"warranty_id": w[0], "warranty_months": w[1]}
        else:
            product["warranty"] = None
        cur.execute(
            "SELECT c.category_id, c.category_name FROM Categories c JOIN ProductsCategoriesXref x ON x.category_id = c.category_id WHERE x.product_id = %s;",
            (pid,),
        )
        cat_rows = cur.fetchall()
        categories = []
        for cat in cat_rows:
            categories.append({"category_id": cat[0], "category_name": cat[1]})
        product["categories"] = categories
        results.append(product)
    cur.close()
    conn.close()
    return jsonify({"message": "products found", "results": results}), 200


@app.route("/company/delete/<int:company_id>", methods=["DELETE"])
def delete_company(company_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT company_id, company_name, active FROM Companies WHERE company_id = %s;", (company_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"message": "company not found", "results": None}), 404
    cur.execute("DELETE FROM ProductsCategoriesXref WHERE product_id IN (SELECT product_id FROM Products WHERE company_id = %s);", (company_id,))
    cur.execute("DELETE FROM Warranties WHERE product_id IN (SELECT product_id FROM Products WHERE company_id = %s);", (company_id,))
    cur.execute("DELETE FROM Products WHERE company_id = %s;", (company_id,))
    cur.execute("DELETE FROM Companies WHERE company_id = %s;", (company_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "company and associated products, warranties, and xref records deleted",
        "results": {"company_id": row[0], "company_name": row[1], "active": row[2]},
    }), 200


@app.route("/product/delete/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT product_id, product_name, company_id, description, price, active FROM Products WHERE product_id = %s;",
        (product_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"message": "product not found", "results": None}), 404
    cur.execute("DELETE FROM Warranties WHERE product_id = %s;", (product_id,))
    cur.execute("DELETE FROM ProductsCategoriesXref WHERE product_id = %s;", (product_id,))
    cur.execute("DELETE FROM Products WHERE product_id = %s;", (product_id,))
    conn.commit()
    cur.close()
    conn.close()
    product = {
        "product_id": row[0],
        "product_name": row[1],
        "company_id": row[2],
        "description": row[3],
        "price": float(row[4]) if row[4] is not None else None,
        "active": row[5],
    }
    return jsonify({
        "message": "product and associated warranty and xref records deleted",
        "results": product,
    }), 200


@app.route("/category/delete/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT category_id, category_name FROM Categories WHERE category_id = %s;", (category_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"message": "category not found", "results": None}), 404
    cur.execute("DELETE FROM ProductsCategoriesXref WHERE category_id = %s;", (category_id,))
    cur.execute("DELETE FROM Categories WHERE category_id = %s;", (category_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "category and associated xref records deleted",
        "results": {"category_id": row[0], "category_name": row[1]},
    }), 200


@app.route("/warranty/delete/<int:warranty_id>", methods=["DELETE"])
def delete_warranty(warranty_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT warranty_id, warranty_months FROM Warranties WHERE warranty_id = %s;", (warranty_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"message": "warranty not found", "results": None}), 404
    cur.execute("DELETE FROM Warranties WHERE warranty_id = %s;", (warranty_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "message": "warranty deleted (association to product removed)",
        "results": {"warranty_id": row[0], "warranty_months": row[1]},
    }), 200


if __name__ == "__main__":
    db.create_tables()
    app.run(host=app_host, port=app_port)
