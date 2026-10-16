# shelly-rpc

A Rust workspace for talking to [Shelly](https://www.shelly.com/) smart devices.

- **[`shelly-rpc`](https://crates.io/crates/shelly-rpc)** — a `no_std`-first
  async client library. Supply an `embedded-nal-async` TCP and DNS stack
  for your platform; HTTP is provided by `reqwless`.
- **[`shellyctl`](https://crates.io/crates/shellyctl)** — a command-line
  client built on top of `shelly-rpc`.

## Status

The library covers device information, switches, covers, lights, inputs,
system and Wi-Fi configuration, sensors, scripts, and cloud RPCs. The CLI
adds discovery, firmware updates, script compilation and upload, log streaming,
and cloud commands. APIs may change before 1.0.

## Workspace layout

```
.
├── Cargo.toml        # workspace manifest
├── shelly-rpc/       # library crate (no_std-first)
└── shellyctl/        # binary crate (std)
```

## Installation

### macOS / Linux (curl)

```sh
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/no-std-rs/shelly-rpc/releases/latest/download/shellyctl-installer.sh | sh
```

### Windows (PowerShell)

```powershell
powershell -c "irm https://github.com/no-std-rs/shelly-rpc/releases/latest/download/shellyctl-installer.ps1 | iex"
```

### Homebrew

```sh
brew install no-std-rs/shellyctl/shellyctl
```

### npm

```sh
npm install -g shellyctl
```

### From source

```sh
cargo install --git https://github.com/no-std-rs/shelly-rpc shellyctl
```

### Updating (for curl/PowerShell installs)

```sh
shellyctl self-update
```

Binaries installed via Homebrew or npm should be upgraded through those
package managers instead.

## Building

```sh
# default (no_std) build of the library
cargo check -p shelly-rpc

# verify the library on an embedded target
rustup target add thumbv7em-none-eabihf
cargo check -p shelly-rpc --target thumbv7em-none-eabihf

# build the CLI
cargo build -p shellyctl
```

## Checks and releases

CI runs formatting, Clippy, workspace tests, CLI smoke checks, crate packaging,
and an embedded `no_std` build.

Stable `v<workspace-version>` tags build the binary installers and publish
`shelly-rpc` followed by `shellyctl` to crates.io. Crate publishing uses the
`CARGO_REGISTRY_TOKEN` Actions secret, authorized for both crate names.
The Homebrew release App must have access to `no-std-rs/homebrew-shellyctl`,
and npm trusted publishing must authorize `no-std-rs/shelly-rpc` with workflow
filename `release.yml`.

## License

Dual-licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
- MIT license ([LICENSE-MIT](LICENSE-MIT))

at your option. Both licenses require that the original copyright notice
and license text be preserved in copies and substantial portions of the
software — i.e. attribution is required.
