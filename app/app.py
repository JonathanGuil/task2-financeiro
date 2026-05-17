from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import psycopg2
import os
import io
import json

app = Flask(__name__)
app.secret_key = "chave-secreta-task2"

# ── Email ──────────────────────────────────────────────────
app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER', 'jonathanguilhermequinot@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
mail = Mail(app)

# ── Banco ──────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "task2"),
        user=os.getenv("DB_USER", "finuser"),
        password=os.getenv("DB_PASS", "finpass")
    )

# ── Email helper ───────────────────────────────────────────
def enviar_email(acao, lanc, destinatario):
    if not destinatario:
        print("[email] Usuario sem email cadastrado; notificacao nao enviada.")
        return
    try:
        msg = Message(
            subject=f"Lancamento {acao}: {lanc['descricao']}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[destinatario]
        )
        msg.body = (
            f"Lancamento {acao} com sucesso!\n\n"
            f"Descricao:  {lanc['descricao']}\n"
            f"Data:       {lanc['data_lancamento']}\n"
            f"Valor:      R$ {float(lanc['valor']):.2f}\n"
            f"Tipo:       {lanc['tipo_lancamento']}\n"
            f"Situacao:   {lanc['situacao']}\n"
        )
        mail.send(msg)
    except Exception as e:
        print(f"[email] Erro ao enviar: {e}")

# ── Filtros helper ─────────────────────────────────────────
def build_query(base, args):
    params = []
    if args.get("data_inicio"):
        base += " AND data_lancamento >= %s"
        params.append(args["data_inicio"])
    if args.get("data_fim"):
        base += " AND data_lancamento <= %s"
        params.append(args["data_fim"])
    if args.get("situacao"):
        base += " AND situacao = %s"
        params.append(args["situacao"])
    if args.get("tipo"):
        base += " AND tipo_lancamento = %s"
        params.append(args["tipo"])
    base += " ORDER BY data_lancamento DESC, id DESC"
    return base, params

# ── Rotas ──────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        login_dig = request.form.get("login", "").strip()
        senha_dig = request.form.get("senha", "").strip()
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(
                "SELECT id, nome, email FROM usuario WHERE login=%s AND senha=%s AND situacao='ativo'",
                (login_dig, senha_dig)
            )
            usuario = cur.fetchone()
            cur.close(); conn.close()
            if usuario:
                session["usuario_id"]    = usuario[0]
                session["usuario_nome"]  = usuario[1]
                session["usuario_email"] = usuario[2]
                return redirect(url_for("index"))
            erro = "Login ou senha incorretos."
        except Exception as e:
            erro = f"Erro ao conectar ao banco: {e}"
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    filtros = {k: request.args.get(k, "") for k in ("data_inicio","data_fim","situacao","tipo")}
    try:
        conn = get_connection()
        cur  = conn.cursor()
        q, p = build_query(
            "SELECT id,descricao,data_lancamento,valor,tipo_lancamento,situacao FROM lancamento WHERE 1=1",
            filtros
        )
        cur.execute(q, p)
        lancamentos = cur.fetchall()
        cur.close(); conn.close()
        erro = None
    except Exception as e:
        lancamentos = []; erro = str(e)

    return render_template("index.html", lancamentos=lancamentos, erro=erro,
                           usuario_nome=session.get("usuario_nome"),
                           usuario_email=session.get("usuario_email"), filtros=filtros)

@app.route("/perfil", methods=["POST"])
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    novo_email = request.form.get("email", "").strip()
    if novo_email:
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("UPDATE usuario SET email=%s WHERE id=%s",
                        (novo_email, session["usuario_id"]))
            conn.commit(); cur.close(); conn.close()
            session["usuario_email"] = novo_email
        except Exception as e:
            print(f"[perfil] Erro ao atualizar email: {e}")
    return redirect(url_for("index"))

@app.route("/novo", methods=["GET", "POST"])
def novo():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    erro = None
    if request.method == "POST":
        d = {k: request.form.get(k, "").strip()
             for k in ("descricao","data_lancamento","valor","tipo_lancamento","situacao")}
        if not all([d["descricao"], d["data_lancamento"], d["valor"], d["tipo_lancamento"]]):
            erro = "Todos os campos são obrigatórios."
        else:
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute(
                    "INSERT INTO lancamento "
                    "(descricao,data_lancamento,valor,tipo_lancamento,situacao) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (d["descricao"], d["data_lancamento"], float(d["valor"]),
                     d["tipo_lancamento"], d["situacao"] or "pendente")
                )
                conn.commit(); cur.close(); conn.close()
                enviar_email("criado", d, session.get("usuario_email"))
                return redirect(url_for("index"))
            except Exception as e:
                erro = str(e)
    return render_template("form.html", acao="Novo", lancamento=None, erro=erro)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    erro = None
    if request.method == "POST":
        d = {k: request.form.get(k, "").strip()
             for k in ("descricao","data_lancamento","valor","tipo_lancamento","situacao")}
        if not all([d["descricao"], d["data_lancamento"], d["valor"], d["tipo_lancamento"]]):
            erro = "Todos os campos são obrigatórios."
        else:
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute(
                    "UPDATE lancamento SET descricao=%s,data_lancamento=%s,"
                    "valor=%s,tipo_lancamento=%s,situacao=%s WHERE id=%s",
                    (d["descricao"], d["data_lancamento"], float(d["valor"]), d["tipo_lancamento"], d["situacao"], id)
                )
                conn.commit(); cur.close(); conn.close()
                enviar_email("atualizado", d, session.get("usuario_email"))
                return redirect(url_for("index"))
            except Exception as e:
                erro = str(e)
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT id,descricao,data_lancamento,valor,"
                    "tipo_lancamento,situacao FROM lancamento WHERE id=%s", (id,))
        row = cur.fetchone(); cur.close(); conn.close()
        if not row:
            return redirect(url_for("index"))
        lancamento = {
            "id": row[0], "descricao": row[1],
            "data_lancamento": row[2].strftime("%Y-%m-%d"),
            "valor": row[3], "tipo_lancamento": row[4], "situacao": row[5]
        }
    except Exception:
        return redirect(url_for("index"))
    return render_template("form.html", acao="Editar", lancamento=lancamento, erro=erro)

@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM lancamento WHERE id=%s", (id,))
        conn.commit(); cur.close(); conn.close()
    except Exception as e:
        print(f"[excluir] Erro: {e}")
    return redirect(url_for("index"))

@app.route("/exportar-pdf")
def exportar_pdf():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    filtros = {k: request.args.get(k, "") for k in ("data_inicio","data_fim","situacao","tipo")}
    try:
        conn = get_connection(); cur = conn.cursor()
        q, p = build_query(
            "SELECT id,descricao,data_lancamento,valor,tipo_lancamento,situacao FROM lancamento WHERE 1=1",
            filtros
        )
        cur.execute(q, p)
        lancamentos = cur.fetchall()
        cur.close(); conn.close()
    except Exception as e:
        return f"Erro: {e}", 500

    buf    = io.BytesIO()
    styles = getSampleStyleSheet()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm,  bottomMargin=2*cm)
    story  = []
    story.append(Paragraph("Relatorio de Lancamentos", styles['Title']))
    story.append(Spacer(1, 0.4*cm))

    partes = []
    if filtros["data_inicio"]: partes.append(f"De: {filtros['data_inicio']}")
    if filtros["data_fim"]:    partes.append(f"Ate: {filtros['data_fim']}")
    if filtros["situacao"]:    partes.append(f"Situacao: {filtros['situacao']}")
    if filtros["tipo"]:        partes.append(f"Tipo: {filtros['tipo']}")
    if partes:
        story.append(Paragraph("Filtros: " + " | ".join(partes), styles['Normal']))
        story.append(Spacer(1, 0.3*cm))

    rows = [["#","Descricao","Data","Valor (R$)","Tipo","Situacao"]]
    total_r = total_d = 0.0
    for lanc in lancamentos:
        rows.append([str(lanc[0]), lanc[1], lanc[2].strftime("%d/%m/%Y"),
                     f"R$ {lanc[3]:.2f}", lanc[4].capitalize(), lanc[5].capitalize()])
        if lanc[4] == "receita": total_r += float(lanc[3])
        else:                    total_d += float(lanc[3])
    rows += [
        ["","TOTAL RECEITAS","",f"R$ {total_r:.2f}","",""],
        ["","TOTAL DESPESAS","",f"R$ {total_d:.2f}","",""],
        ["","SALDO",         "",f"R$ {total_r-total_d:.2f}","",""],
    ]
    t = Table(rows, colWidths=[1*cm,5.5*cm,2.5*cm,2.5*cm,2.5*cm,2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0),  colors.HexColor("#1A5276")),
        ('TEXTCOLOR',     (0,0),(-1,0),  colors.white),
        ('FONTNAME',      (0,0),(-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1),(-1,-4), [colors.white, colors.HexColor("#F2F3F4")]),
        ('BACKGROUND',    (0,-3),(-1,-1),colors.HexColor("#D6EAF8")),
        ('FONTNAME',      (0,-3),(-1,-1),'Helvetica-Bold'),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('LEFTPADDING',   (0,0),(-1,-1), 6),
        ('RIGHTPADDING',  (0,0),(-1,-1), 6),
        ('TOPPADDING',    (0,0),(-1,-1), 4),
        ('BOTTOMPADDING', (0,0),(-1,-1), 4),
    ]))
    story.append(t)
    doc.build(story)
    buf.seek(0)

    resp = make_response(buf.read())
    resp.headers['Content-Type']        = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attachment; filename=lancamentos.pdf'
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
