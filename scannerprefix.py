import whois
import requests
from bs4 import BeautifulSoup
import socket
import ssl
import dns.resolver
import getpass

# Função para obter informações WHOIS
def get_whois_info(domain):
    try:
        whois_data = whois.whois(domain)
        return whois_data
    except Exception as e:
        return f"Erro ao obter informações WHOIS: {e}"

# Função para obter o endereço IP do domínio
def get_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return "Erro ao resolver o endereço IP"

# Função para obter informações DNS do domínio
def get_dns_info(domain):
    try:
        dns_info = {}
        resolver = dns.resolver.Resolver()
        for qtype in ['A', 'AAAA', 'MX', 'NS', 'TXT']:
            try:
                answers = resolver.resolve(domain, qtype)
                dns_info[qtype] = [str(rdata) for rdata in answers]
            except dns.resolver.NoAnswer:
                dns_info[qtype] = "Sem resposta"
            except dns.resolver.NXDOMAIN:
                dns_info[qtype] = "Domínio não encontrado"
        return dns_info
    except Exception as e:
        return f"Erro ao obter informações DNS: {e}"

# Função para obter informações do certificado SSL
def get_ssl_info(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        return f"Erro ao obter informações SSL: {e}"

# Função para obter informações da página (título, meta tags e links)
def get_page_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Obter título da página
        title = soup.title.string if soup.title else "Sem título"

        # Obter meta tags
        meta_tags = {meta.get('name', meta.get('property', '')): meta.get('content', '') for meta in soup.find_all('meta') if meta.get('content')}

        # Obter todos os links da página
        links = [a['href'] for a in soup.find_all('a', href=True)]

        return {
            "title": title,
            "meta_tags": meta_tags,
            "links": links
        }
    except Exception as e:
        return f"Erro ao obter informações da página: {e}"

# Função para formatar a saída das informações
def print_formatted_section(title, content):
    print(f"\n=== {title} ===")
    if isinstance(content, dict):
        for key, value in content.items():
            if isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key}: {value}")
    elif isinstance(content, list):
        for item in content:
            print(f"- {item}")
    else:
        print(content)

# Função principal para reunir todas as informações
def main():
    usuario = getpass.getuser()
    url = input(f"Olá {usuario}, para puxar os dados do site siga o exemplo: https://www.exemplo.com => ").strip()
    
    # Remover 'http://' ou 'https://' da URL para usar nas consultas WHOIS e IP
    if url.startswith('http://'):
        domain = url.replace('http://', '').split('/')[0]
    elif url.startswith('https://'):
        domain = url.replace('https://', '').split('/')[0]
    else:
        domain = url.split('/')[0]

    print_formatted_section("Informações WHOIS", get_whois_info(domain))
    print_formatted_section("Endereço IP", {"Endereço IP": get_ip(domain)})
    print_formatted_section("Informações DNS", get_dns_info(domain))
    print_formatted_section("Informações SSL", get_ssl_info(domain))

    page_info = get_page_info(url)
    if isinstance(page_info, dict):
        print_formatted_section("Título da Página", {"Título": page_info.get('title', 'Sem título')})
        print_formatted_section("Meta Tags", page_info.get('meta_tags', {}))
        print_formatted_section("Links", page_info.get('links', []))
    else:
        print_formatted_section("Erro ao obter informações da página", page_info)

if __name__ == "__main__":
    main()
input("Aperte ENTER para fechar.")