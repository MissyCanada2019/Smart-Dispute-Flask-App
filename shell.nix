{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.flask
    pkgs.python311Packages.flask-sqlalchemy
    pkgs.python311Packages.flask-login
    pkgs.python311Packages.gunicorn
    pkgs.python311Packages.python-dotenv
    pkgs.python311Packages.werkzeug
    pkgs.python311Packages.openai
    pkgs.python311Packages.pillow
    pkgs.python311Packages.pytesseract
    pkgs.python311Packages.pypdf2
    pkgs.python311Packages.anthropic
    pkgs.python311Packages.reportlab
    pkgs.python311Packages.requests
  ];
}