{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = [pkgs.git pkgs.stdenv.cc.cc.lib pkgs.gcc-unwrapped.lib pkgs.zlib pkgs.nodePackages_latest.vercel];

  languages.python = {
    enable = true;
    poetry.enable = true;
  };

  languages.javascript = {
    enable = true;
    npm = {
      enable = true;
      install.enable = true;
      package = pkgs.nodejs_24;
    };
  };

  services.postgres.enable = true;
  env.PGHOST = "/var/run/postgresql";

  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.zlib
    pkgs.stdenv.cc.cc.lib
    pkgs.glibc
  ];
}
