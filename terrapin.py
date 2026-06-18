#!/usr/bin/env python3
import argparse
import socket
import select
import sys
import time


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def close_socket(sock):
    try:
        if sock:
            sock.close()
    except Exception:
        pass


def ssh_proxy(listen_host, listen_port, target_host, target_port):
    proxy_sock = None
    client_conn = None
    server_conn = None

    try:
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_sock.bind((listen_host, listen_port))
        proxy_sock.listen(5)

        log(f"SSH Debug Proxy listening on {listen_host}:{listen_port}")
        log(f"Forwarding to target {target_host}:{target_port}")
        log("Waiting for client connection...")

        client_conn, client_addr = proxy_sock.accept()
        log(f"Client connected from {client_addr[0]}:{client_addr[1]}")

        server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_conn.settimeout(10)

        log(f"Connecting to target {target_host}:{target_port}...")
        server_conn.connect((target_host, target_port))
        server_conn.settimeout(None)

        log("Connected to target SSH server")
        log("Proxy is now forwarding traffic")

        sockets = [client_conn, server_conn]

        while True:
            readable, _, errored = select.select(sockets, [], sockets)

            if errored:
                log("Socket error detected, closing connection")
                break

            for sock in readable:
                try:
                    data = sock.recv(4096)
                except ConnectionResetError:
                    log("Connection reset by peer")
                    return

                if not data:
                    log("Connection closed")
                    return

                if sock is client_conn:
                    direction = "CLIENT -> TARGET"
                    server_conn.sendall(data)
                else:
                    direction = "TARGET -> CLIENT"
                    client_conn.sendall(data)

                log(f"{direction}: {len(data)} bytes")

    except KeyboardInterrupt:
        log("Interrupted by user")

    except socket.timeout:
        log("ERROR: Timeout connecting to target")
        log("Check routing/firewall/VPN/target SSH port")

    except ConnectionRefusedError:
        log("ERROR: Connection refused by target")
        log("Target reachable, but SSH port is closed or service is not listening")

    except OSError as e:
        log(f"ERROR: {e}")

    finally:
        close_socket(client_conn)
        close_socket(server_conn)
        close_socket(proxy_sock)
        log("Proxy stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe SSH TCP debug proxy")
    parser.add_argument("--listen-host", default="0.0.0.0")
    parser.add_argument("--listen-port", type=int, default=2222)
    parser.add_argument("--target-host", required=True)
    parser.add_argument("--target-port", type=int, default=22)

    args = parser.parse_args()

    ssh_proxy(
        args.listen_host,
        args.listen_port,
        args.target_host,
        args.target_port
    )
