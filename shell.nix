with import <nixpkgs> {};
python311.withPackages (ps: with ps; [
  flask
  flask-login
  flask-sqlalchemy
  python-dotenv
  sqlalchemy
  psycopg2
  pillow
  pytesseract
  requests
  stripe
  google-cloud-storage
  google-cloud-vision
  pyjwt
  cryptography
  pyopenssl
])