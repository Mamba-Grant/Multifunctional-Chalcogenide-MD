{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = [pkgs.git pkgs.stdenv.cc.cc.lib pkgs.gcc-unwrapped.lib pkgs.zlib pkgs.nodejs];

  languages.python = {
    enable = true;
    poetry.enable = true;
  };

  languages.javascript = {
    enable = true;
    npm = {
      enable = true;
      install.enable = true;
    };
  };

  services.postgres.enable = true;

  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.zlib
    pkgs.stdenv.cc.cc.lib
    pkgs.glibc
  ];
}
