import click

from mysocketctl.utils import *


@click.group()
def socket():
    """Manage your global sockets"""
    pass


def get_sockets(authorization_header):
    api_answer = requests.get(api_url + "connect", headers=authorization_header)
    validate_response(api_answer)
    return api_answer.json()


def new_socket(
    authorization_header,
    connect_name,
    protected_socket,
    protected_user,
    protected_pass,
    socket_type,
):
    if not protected_socket:
        protected_socket = False
    else:
        protected_socket = True

    params = {
        "name": connect_name,
        "protected_socket": protected_socket,
        "protected_username": protected_user,
        "protected_password": protected_pass,
        "socket_type": socket_type,
    }
    api_answer = requests.post(
        api_url + "socket", data=json.dumps(params), headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer.json()


def delete_socket(authorization_header, socket_id):
    api_answer = requests.delete(
        f"{api_url}socket/{socket_id}", headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer


@socket.command()
def ls():
    table = PrettyTable(
        field_names=["socket_id", "dns_name", "type", "port(s)", "name"]
    )
    table.align = "l"
    table.border = True

    authorization_header = get_auth_header()
    sockets = get_sockets(authorization_header)
    for socket in sockets:
        ports_str = listToStr = " ".join(
            [str(elem) for elem in socket["socket_tcp_ports"]]
        )
        row = [
            socket["socket_id"],
            socket["dnsname"],
            socket["socket_type"],
            ports_str,
            socket["name"],
        ]
        table.add_row(row)
    print(table)


@socket.command()
@click.option("--name", required=True, type=str)
@click.option("--protected/--not-protected", default=False)
@click.option("--username", required=False, type=str, default="")
@click.option("--password", required=False, type=str, default="")
@click.option(
    "--type",
    required=False,
    type=click.Choice(["http", "https", "tcp", "tls"], case_sensitive=False),
    default="http",
    help="Socket type, http, https, tcp, tls",
)
def create(name, protected, username, password, type):

    if protected:
        if not username:
            print("--username required when using --protected")
            sys.exit(1)
        if not password:
            print("--password required when using --protected")
            sys.exit(1)

    authorization_header = get_auth_header()
    socket = new_socket(
        authorization_header, name, protected, str(username), str(password), str(type)
    )

    ssh_server = "ssh.mysocket.io"

    print_socket(socket, protected, username, password)


@socket.command()
@click.option("--socket_id", required=True, type=str)
def delete(socket_id):
    authorization_header = get_auth_header()
    delete_socket(authorization_header, socket_id)
    print(f"Socket {socket_id} deleted")
