# terrapinattack CVE-2023-48795 - SSH Protocol Prefix Truncation Attack

# SSH Debug Proxy

A lightweight TCP proxy written in Python 3 for debugging SSH connections.

The proxy sits between an SSH client and an SSH server, forwards all traffic, and logs the direction and size of each data chunk.

> ⚠️ **Important**
>
> This tool is for **debugging and educational purposes only**.
> It does **not** decrypt SSH traffic. It only passes raw encrypted bytes and prints their length.
> Do not use it in production or with sensitive credentials.

---

## Features

- Simple TCP forwarding for SSH traffic
- Logs traffic direction:
  - `CLIENT -> TARGET`
  - `TARGET -> CLIENT`
- Shows the size of each forwarded data chunk
- Uses Python standard library only
- No external dependencies

---

## Requirements

- Python 3.6 or later
- No additional Python packages required

---

## Usage

```bash
python3 ssh-debug-proxy.py --target-host <TARGET_IP> [OPTIONS]
```

### Arguments

| Argument | Default | Description |
| --- | --- | --- |
| `--listen-host` | `0.0.0.0` | IP address the proxy listens on |
| `--listen-port` | `2222` | TCP port the proxy listens on |
| `--target-host` | Required | IP address or hostname of the real SSH server |
| `--target-port` | `22` | TCP port of the real SSH server |

---

## How to Run

### 1. Start the Proxy

Run this on the machine where you want to inspect the SSH traffic, for example a Kali VM:

```bash
python3 ssh-debug-proxy.py --target-host 192.168.1.100
```

Example output:

```text
[12:34:56] SSH Debug Proxy listening on 0.0.0.0:2222
[12:34:56] Forwarding to target 192.168.1.100:22
[12:34:56] Waiting for client connection...
```

---

### 2. Connect the SSH Client Through the Proxy

From your real client machine, connect to the proxy address and port instead of directly connecting to the SSH server.

---

## OpenSSH Examples

### Linux, macOS, or Windows OpenSSH

```bash
ssh -o "ProxyCommand=nc <PROXY_IP> 2222" user@<TARGET_IP>
```

Even though the command includes the target IP, the connection goes through the proxy first.

Example:

```bash
ssh -o "ProxyCommand=nc 192.168.1.50 2222" root@192.168.1.100
```

> **Note:** On Windows, you can use `ncat` from Nmap if `nc` is unavailable.

---

### OpenSSH for Windows or Git Bash

```bash
ssh -o "ProxyCommand=ncat 192.168.1.50 2222" user@target
```

---

## PuTTY Configuration

For PuTTY on Windows:

1. Open **PuTTY**.
2. Go to **Connection → Proxy**.
3. Set **Proxy type** to **Local**.
4. Enter the proxy IP address, for example:

   ```text
   192.168.1.50
   ```

5. Enter the proxy port:

   ```text
   2222
   ```

6. Go back to the **Session** screen.
7. Enter the real target host or IP address and SSH port.
8. Click **Open**.

---

## Running in a Virtual Machine

Example scenario:

```text
VirtualBox Kali VM  ->  Windows Host  ->  SSH Target
```

There are two common network setups.

---

## Option A: Bridged Adapter Recommended

This is the simpler option because no port forwarding is required.

### 1. Set Network Mode to Bridged

In VirtualBox:

```text
VM Settings → Network → Attached to: Bridged Adapter
```

### 2. Find Kali's IP Address

Inside Kali, run:

```bash
ip a
```

Look for an IP address such as:

```text
192.168.1.50
```

### 3. Start the Proxy on Kali

```bash
python3 ssh-debug-proxy.py --target-host <TARGET_IP>
```

By default, the proxy listens on:

```text
0.0.0.0:2222
```

### 4. Connect From Windows

```bash
ssh -o "ProxyCommand=ncat <KALI_IP> 2222" user@target
```

Example:

```bash
ssh -o "ProxyCommand=ncat 192.168.1.50 2222" user@10.0.0.5
```

---

## Option B: NAT with Port Forwarding

Use this if the VM is using NAT mode.

### 1. Keep Network Mode as NAT

In VirtualBox:

```text
VM Settings → Network → Attached to: NAT
```

### 2. Add Port Forwarding

Go to:

```text
VM Settings → Network → Advanced → Port Forwarding
```

Add the following rule:

| Field | Value |
| --- | --- |
| Name | `ssh-proxy` |
| Protocol | `TCP` |
| Host Port | `2222` |
| Guest Port | `2222` |

### 3. Start the Proxy Inside Kali

```bash
python3 ssh-debug-proxy.py --target-host <TARGET_IP>
```

### 4. Connect From Windows

```bash
ssh -o "ProxyCommand=ncat 127.0.0.1 2222" user@target
```

---

## Example: Debugging an SSH Connection

### Kali VM Proxy

Assume the Kali VM IP address is:

```text
192.168.1.50
```

Start the proxy:

```bash
python3 ssh-debug-proxy.py --target-host 10.0.0.5 --target-port 22
```

### Windows Host SSH Client

```bash
ssh -o "ProxyCommand=ncat 192.168.1.50 2222" user@10.0.0.5
```

### Proxy Log Output

The Kali terminal will show output similar to this:

```text
[14:22:01] Client connected from 192.168.1.20:55321
[14:22:01] Connecting to target 10.0.0.5:22...
[14:22:02] Connected to target SSH server
[14:22:02] Proxy is now forwarding traffic
[14:22:03] CLIENT -> TARGET: 42 bytes
[14:22:03] TARGET -> CLIENT: 86 bytes
[14:22:04] CLIENT -> TARGET: 100 bytes
...
```

---

## Troubleshooting

| Error Message | Likely Cause | Fix |
| --- | --- | --- |
| `ERROR: Timeout connecting to target` | Proxy cannot reach the target IP or port | Check routing, VPN, firewall, or target IP |
| `ERROR: Connection refused by target` | Target is reachable, but SSH is closed or not running | Check if SSH service is running and listening on the correct port |
| `Connection reset by peer` | SSH server or client abruptly closed the connection | This can be normal when the SSH session ends |
| `Client connection refused` | Proxy port may be blocked by firewall | Allow port `2222/tcp` or temporarily disable firewall for testing |

If `ufw` is enabled on Kali, allow the proxy port:

```bash
sudo ufw allow 2222/tcp
```

---

## Security Notes

The proxy runs in user space and does not require elevated privileges when using the default non-privileged port `2222`.

Anyone who can reach the proxy listen port can forward traffic to the configured target. Only run this tool in trusted networks.

For safer local-only testing, bind the proxy to `127.0.0.1`:

```bash
python3 ssh-debug-proxy.py \
  --listen-host 127.0.0.1 \
  --listen-port 2222 \
  --target-host 192.168.1.100
```

This proxy does not inspect, decrypt, or modify SSH data. It cannot break SSH encryption.

---

## Disclaimer

Use this tool only in environments where you have permission to inspect and debug network traffic.
