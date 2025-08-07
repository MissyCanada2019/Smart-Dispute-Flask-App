# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.postgresql
  ];

  # Sets environment variables in the workspace
  env = {
    # Extend PATH to include Python and pip without overriding system PATH
    PYTHON_PATH = "${pkgs.python311}/bin";
    PIP_PATH = "${pkgs.python311Packages.pip}/bin";
  };
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["python" "../main.py"];
          manager = "web";
          env = {
            FLASK_APP = "../main.py";
            FLASK_ENV = "development";
            PORT = "$PORT";
          };
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      onCreate = {
        pip-install = "pip install -r ../requirements.txt";
      };
      onStart = {
        start-app = "python ../main.py";
      };
    };
  };
}
