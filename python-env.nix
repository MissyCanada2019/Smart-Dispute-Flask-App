{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python311.withPackages (ps: [
      ps.flask
      ps.flask-login
      ps.flask-sqlalchemy
      ps.sqlalchemy
      ps.cryptography
      ps.flask-wtf
      ps.gunicorn
      ps.python-dotenv
      ps.reportlab
    ]))
    pkgs.nodejs_20
    pkgs.postgresql
  ];
}