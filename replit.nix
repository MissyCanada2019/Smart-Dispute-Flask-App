{ pkgs }: {
  deps = [
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
    (pkgs.python311Packages.sqlalchemy.overridePythonAttrs (old: rec {
      version = "1.4.48";
      src = pkgs.fetchPypi {
        pname = "SQLAlchemy";
        inherit version;
        hash = "sha256-4Q1k2Z3bLd1c5G7y+6Q3Y3X7H4Y6w5J8v9v0w1x2y3z4a5b6c7d8e9f0g";
      };
    }))
  ];
}
