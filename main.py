import argparse
import subprocess

parser = argparse.ArgumentParser(description="Run a shell command.")
parser.add_argument(
    "--verbose", "-v", action="store_true", help="Enable verbose output"
)
parser.add_argument("-ip", type=str, required=True, help="Specify the IP address")
parser.add_argument(
    "--ports", "-p", type=str, nargs="+", help="Specify one or more ports"
)
parser.add_argument(
    "--serv_ports", "-sp", type=str, nargs="+", help="Specify one or more ports"
)

args = parser.parse_args()


def run_command_get_output(command):
    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout
    
def set_firewall(port_no):
    for port_no in port_no:
        inbound_firewall = [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f"name=Allow TCP Port {port_no}",
            "protocol=TCP",
            "dir=in",
            f"localport={port_no}",
            "action=allow",
        ]

        fire_output = str(
            f"for port number : {port_no} {run_command_get_output(inbound_firewall)}"
        )

        print(fire_output)

    set_netsh_chain(
        listen_port_no=args.ports, serv_ip=args.ip, serv_port=args.serv_ports
    )

def set_netsh_chain(listen_port_no, serv_ip, serv_port):
    pair_ports = list(zip(listen_port_no, serv_port))
    for listen_port_no, serv_port in pair_ports:
        netsh_cmd = [
            "netsh",
            "interface",
            "portproxy",
            "add",
            "v4tov4",
            f"listenport={listen_port_no}",
            f"connectaddress={serv_ip}",
            f"connectport={serv_port}",
        ]
        netsh_output = str(
            f"{listen_port_no} <----> {serv_port} {run_command_get_output(netsh_cmd)}"
        )
        print(netsh_output)

    input("press enter for exiting: ")
    remove_netsh_chain(port_no=args.ports)
    remove_firewall(port_no=args.ports)

def remove_netsh_chain(port_no):
    for port_no in port_no:
        remove_cmd = [
            "netsh",
            "interface",
            "portproxy",
            "delete",
            "v4tov4",
            f"listenport={port_no}",
        ]
        netsh_rm_output = str(
            f"removed {port_no} chain {run_command_get_output(remove_cmd)}"
        )
        print(netsh_rm_output)


def remove_firewall(port_no):
    for port_no in port_no:
        inbound_firewall = [
            "netsh",
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f"name=Allow TCP Port {port_no}",
        ]

        fire_output = str(
            f"for port number : {port_no} {run_command_get_output(inbound_firewall)}"
        )

        print(fire_output)

def main():
    if len(args.ports) == len(args.serv_ports):
        set_firewall(args.ports)
    else:
        print("len of serv ports equal to ports specified !!")


main()
