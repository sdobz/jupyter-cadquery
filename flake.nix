{
  description = "marimo-cadquery — development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.micromamba
            pkgs.nodejs_20
            pkgs.yarn
          ];

          shellHook = ''
            echo "marimo-cadquery dev environment"
            echo ""
            echo "  Python and project libraries are managed by micromamba from environment.yml."
            echo ""
            export MAMBA_ROOT_PREFIX="$PWD/.mamba"
            export CONDA_PKGS_DIRS="$PWD/.mamba/pkgs"
            unset PYTHONPATH
            unset PYTHONHOME
            export PYTHONNOUSERSITE=1
            mkdir -p "$MAMBA_ROOT_PREFIX"

            # Make 'micromamba activate <env>' work in this shell without conda init.
            current_shell="$(basename "''${SHELL:-zsh}")"
            case "$current_shell" in
              zsh|bash)
                ;;
              *)
                current_shell="bash"
                ;;
            esac
            eval "$(micromamba shell hook --shell "$current_shell")"

            env_name="marimo-cadquery"
            env_file="$PWD/environment.yml"
            project_file="$PWD/pyproject.toml"
            state_dir="$MAMBA_ROOT_PREFIX/.state"
            state_file="$state_dir/''${env_name}.environment.sha256"
            mkdir -p "$state_dir"

            activate_env() {
              if [[ -d "$MAMBA_ROOT_PREFIX/envs/$env_name" ]]; then
                micromamba activate "$env_name" >/dev/null 2>&1 || true
              fi
            }

            activate_env

            # Auto-sync env on shell entry unless explicitly disabled.
            # Set JCQ_AUTO_ENV=0 to skip automatic create/update.
            if [[ "''${JCQ_AUTO_ENV:-1}" != "0" && -f "$env_file" ]]; then
              if command -v sha256sum >/dev/null 2>&1; then
                env_hash="$({
                  sha256sum "$env_file"
                  if [[ -f "$project_file" ]]; then
                    sha256sum "$project_file"
                  fi
                } | sha256sum | awk '{print $1}')"
              else
                env_hash="$({
                  shasum -a 256 "$env_file"
                  if [[ -f "$project_file" ]]; then
                    shasum -a 256 "$project_file"
                  fi
                } | shasum -a 256 | awk '{print $1}')"
              fi

              if [[ ! -d "$MAMBA_ROOT_PREFIX/envs/$env_name" ]]; then
                echo "  Creating micromamba env: $env_name"
                if micromamba create -f "$env_file" -y; then
                  activate_env
                  printf "%s" "$env_hash" > "$state_file"
                else
                  rm -f "$state_file"
                  echo "  Env create failed; will retry on next shell entry."
                fi
              elif [[ ! -f "$state_file" ]] || [[ "$(cat "$state_file")" != "$env_hash" ]]; then
                echo "  Updating micromamba env after environment.yml change: $env_name"
                activate_env
                if micromamba update -f "$env_file" --prune -y; then
                  printf "%s" "$env_hash" > "$state_file"
                else
                  rm -f "$state_file"
                  echo "  Env update failed; will retry on next shell entry."
                fi
              fi
            fi

            activate_env

            # Refuse accidental installs to non-env Python locations while
            # still allowing the activated micromamba environment to use pip.
            pip() {
              if [[ -z "$CONDA_PREFIX" ]]; then
                echo "pip is blocked outside the activated micromamba environment" >&2
                return 1
              fi
              command pip "$@"
            }

            python() {
              if [[ $# -ge 3 && "$1" == "-m" && "$2" == "pip" && -z "$CONDA_PREFIX" ]]; then
                echo "python -m pip is blocked outside the activated micromamba environment" >&2
                return 1
              fi
              command python "$@"
            }

            echo "  First-time setup:"
            echo "    micromamba create -f environment.yml -y"
            echo "    micromamba activate marimo-cadquery"
            echo ""
            echo "  Optional: disable auto env sync"
            echo "    export JCQ_AUTO_ENV=0"
            echo ""
            echo "  Verify interpreter:"
            echo "    which python"
            echo "    which pip"
            echo ""
            echo "  Run example:"
            echo "    marimo run examples/1-cadquery.py"
            echo ""
          '';
        };
      }
    );
}