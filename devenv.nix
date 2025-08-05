{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  dotenv.disableHint = true; # This line tells devenv to disable a hint in the terminal

  packages = [pkgs.git pkgs.posting pkgs.zlib];

  languages.python = {
    enable = true;
    poetry.enable = true;
  };

  languages.javascript = {
    enable = true;
    npm.enable = true;
  };

  enterShell = ''
    git --version
  '';

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';
}
